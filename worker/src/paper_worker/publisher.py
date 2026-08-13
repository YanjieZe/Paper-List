from __future__ import annotations

import hashlib
import os
import re
import subprocess
import tempfile
from pathlib import Path
from uuid import UUID

import frontmatter
from psycopg import Connection

from .config import Settings
from .reviews import validate_review_publishable

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"OPENAI_API_KEY\s*="),
    re.compile(r"BEGIN (?:RSA |OPENSSH )?PRIVATE KEY"),
]


def _git(root: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=check,
        capture_output=True,
        text=True,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    return result.stdout.strip()


def _git_code(root: Path, *args: str) -> int:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    ).returncode


def current_origin_main(root: Path) -> str:
    _git(root, "fetch", "origin", "main")
    return _git(root, "rev-parse", "origin/main")


def render_review_markdown(review: dict) -> str:
    if review["review_type"] == "roadmap":
        metadata = {
            "id": f"roadmap:{review['roadmap_id']}",
            "title": review["roadmap_title"],
            "slug": review["roadmap_slug"],
            "version": review["roadmap_version"] + 1,
            "review_id": str(review["id"]),
            "schema_version": 1,
        }
        body_parts = [f"# {review['roadmap_title']}"]
        if review["roadmap_description"]:
            body_parts.append(review["roadmap_description"])
        for section in review["sections"]:
            body_parts.extend(
                [
                    f"## {section['title']}",
                    section["edited_markdown"] or section["generated_markdown"],
                ]
            )
        return frontmatter.dumps(frontmatter.Post("\n\n".join(body_parts) + "\n", **metadata)) + "\n"
    metadata = {
        "id": f"item:{review['research_item_id']}",
        "work_id": str(review["work_id"]),
        "title": review["item_title"],
        "type": review["item_type"],
        "url": review["canonical_url"],
        "authors": review["authors"],
        "year": review["year"],
        "venue": review["venue"],
        "reading_status": "read",
        "review_id": str(review["id"]),
        "schema_version": 1,
    }
    body_parts = [f"# {review['item_title']}"]
    for section in review["sections"]:
        body_parts.append(f"## {section['title']}")
        body_parts.append(section["edited_markdown"] or section["generated_markdown"])
    post = frontmatter.Post("\n\n".join(body_parts) + "\n", **metadata)
    return frontmatter.dumps(post) + "\n"


def validate_public_markdown(content: str) -> None:
    if not content.startswith("---\n"):
        raise ValueError("published knowledge requires YAML frontmatter")
    for pattern in SECRET_PATTERNS:
        if pattern.search(content):
            raise ValueError("secret-like content detected; publication blocked")
    post = frontmatter.loads(content)
    for required in ("id", "title", "schema_version"):
        if required not in post.metadata:
            raise ValueError(f"missing frontmatter field: {required}")
    if not post.content.strip():
        raise ValueError("published knowledge cannot be empty")


def publish_review(conn: Connection, settings: Settings, review_id: UUID) -> dict:
    review = validate_review_publishable(conn, review_id)
    content = render_review_markdown(review)
    validate_public_markdown(content)
    repo = settings.repository_root.resolve()
    remote_sha = current_origin_main(repo)
    if review["base_git_sha"] and review["base_git_sha"] != remote_sha:
        conn.execute("UPDATE review_items SET status = 'conflict' WHERE id = %s", (review_id,))
        conn.execute(
            """
            INSERT INTO notifications (kind, title, message, href)
            VALUES ('git_conflict', 'Publication paused', 'The remote main branch changed since this review was created.', %s)
            """,
            (f"/reviews/{review_id}",),
        )
        conn.commit()
        raise RuntimeError("remote main changed after the review was created")

    if review["review_type"] == "roadmap":
        path = Path("knowledge/roadmaps") / f"{review['roadmap_slug']}.md"
        commit_title = review["roadmap_title"]
    else:
        path = Path("knowledge/items") / f"{review['item_slug']}.md"
        commit_title = review["item_title"]
    with tempfile.TemporaryDirectory(prefix="paper-os-publish-") as temp:
        worktree = Path(temp) / "repo"
        _git(repo, "worktree", "add", "--detach", str(worktree), remote_sha)
        try:
            target = worktree / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            _git(worktree, "add", str(path))
            if _git_code(worktree, "diff", "--cached", "--quiet") == 0:
                commit_sha = remote_sha
            else:
                _git(worktree, "commit", "-m", f"Publish knowledge: {commit_title}")
                commit_sha = _git(worktree, "rev-parse", "HEAD")
                latest_remote = current_origin_main(repo)
                if latest_remote != remote_sha:
                    raise RuntimeError("remote main advanced during publication")
                _git(worktree, "push", "origin", "HEAD:main")
        finally:
            _git(repo, "worktree", "remove", "--force", str(worktree), check=False)

    conn.execute(
        """
        INSERT INTO git_exports (review_item_id, path, base_sha, commit_sha, push_status, finished_at)
        VALUES (%s, %s, %s, %s, 'pushed', now())
        """,
        (review_id, str(path), remote_sha, commit_sha),
    )
    conn.execute("UPDATE review_items SET status = 'published' WHERE id = %s", (review_id,))
    if review["review_type"] == "roadmap":
        conn.execute(
            "UPDATE roadmaps SET status = 'current', published_path = %s, version = version + 1 WHERE id = %s",
            (str(path), review["roadmap_id"]),
        )
        for section in review["sections"]:
            conn.execute(
                "UPDATE roadmap_nodes SET narrative = %s, review_status = %s WHERE roadmap_id = %s AND slug = %s",
                (
                    section["edited_markdown"] or section["generated_markdown"],
                    section["status"],
                    review["roadmap_id"],
                    section["section_key"],
                ),
            )
        href = f"/roadmaps/{review['roadmap_slug']}"
    else:
        conn.execute(
            "UPDATE research_items SET lifecycle_status = 'published', published_path = %s, reading_status = 'read' WHERE id = %s",
            (str(path), review["research_item_id"]),
        )
        conn.execute(
            """
            UPDATE roadmaps SET status = 'stale'
            WHERE id IN (
              SELECT DISTINCT rn.roadmap_id FROM roadmap_nodes rn
              WHERE rn.work_id = %s OR rn.node_type = 'branch'
            )
            """,
            (review["work_id"],),
        )
        href = f"/library/{review['research_item_id']}"
    conn.execute(
        """
        INSERT INTO notifications (kind, title, message, href)
        VALUES ('published', 'Knowledge published', %s, %s)
        """,
        (commit_title, href),
    )
    conn.commit()
    return {
        "path": str(path),
        "commitSha": commit_sha,
        "sha256": hashlib.sha256(content.encode()).hexdigest(),
    }
