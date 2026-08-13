#!/usr/bin/env python3
"""Find README paper bullets added after the Markdown classification baseline."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import parse_qs, urlsplit, urlunsplit

SECTION = "# Recent Random Papers"
BASELINE_RE = re.compile(r"<!--\s*paper-classifier-baseline:\s*([0-9a-f]{7,40})\s*-->")
URL_RE = re.compile(r"https?://[^\s)>]+")
ARXIV_RE = re.compile(r"(?:arxiv\.org/(?:abs|pdf)/)?(\d{4}\.\d{4,5})(?:v\d+)?", re.I)
DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def section_bullets(markdown: str) -> list[dict[str, object]]:
    lines = markdown.splitlines()
    try:
        start = lines.index(SECTION) + 1
    except ValueError as error:
        raise ValueError(f"README is missing {SECTION!r}") from error

    bullets: list[dict[str, object]] = []
    for index in range(start, len(lines)):
        line = lines[index]
        if line.startswith("# "):
            break
        if line.startswith("- "):
            bullets.append(
                {
                    "line": index + 1,
                    "markdown": line,
                    "urls": clean_urls(line),
                    "identities": identities(line),
                }
            )
    return bullets


def clean_urls(text: str) -> list[str]:
    return [match.group(0).rstrip(".,;]") for match in URL_RE.finditer(text)]


def normalize_url(value: str) -> str:
    parts = urlsplit(value)
    host = parts.netloc.lower()
    path = parts.path.rstrip("/")
    arxiv = ARXIV_RE.search(f"{host}{path}")
    if arxiv:
        return f"arxiv:{arxiv.group(1)}"
    if host == "openreview.net" and path == "/forum":
        forum_id = parse_qs(parts.query).get("id", [""])[0]
        if forum_id:
            return f"openreview:{forum_id}"
    return urlunsplit((parts.scheme.lower(), host, path, "", ""))


def identities(text: str) -> list[str]:
    found = {normalize_url(url) for url in clean_urls(text)}
    found.update(f"arxiv:{match.group(1)}" for match in ARXIV_RE.finditer(text))
    found.update(f"doi:{match.group(0).lower().rstrip(').,;')}" for match in DOI_RE.finditer(text))
    plain_text = re.sub(r"\[([^]]+)]\([^)]+\)", r"\1", text)
    plain_text = re.sub(r"[*_`]", "", plain_text).lower()
    plain_text = re.sub(r"[^a-z0-9]+", " ", plain_text).strip()
    if plain_text:
        found.add(f"text:{plain_text}")
    return sorted(found)


def matches_seen(candidate: dict[str, object], seen: set[str]) -> bool:
    return bool(set(candidate["identities"]) & seen)


def topic_inventory(repo: Path) -> list[dict[str, object]]:
    inventory = []
    for path in sorted((repo / "topics").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        headings = [line.lstrip("# ").strip() for line in text.splitlines() if line.startswith("##")]
        inventory.append(
            {
                "path": str(path.relative_to(repo)),
                "title": next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), path.stem),
                "headings": headings,
                "papers": sum(1 for line in text.splitlines() if line.startswith("- ")),
            }
        )
    return inventory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--readme", type=Path)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    repo = args.repo.resolve()
    readme = args.readme or repo / "README.md"
    log_path = args.log or repo / ".paper-list" / "classification-log.md"
    log_text = log_path.read_text(encoding="utf-8")
    marker = BASELINE_RE.search(log_text)
    if not marker:
        raise ValueError(f"Missing paper-classifier baseline marker in {log_path}")
    baseline = git(repo, "rev-parse", marker.group(1)).strip()
    baseline_readme = git(repo, "show", f"{baseline}:README.md")

    baseline_seen = {
        identity
        for bullet in section_bullets(baseline_readme)
        for identity in bullet["identities"]
    }
    logged_seen = set(identities(log_text))
    candidates = [
        bullet
        for bullet in section_bullets(readme.read_text(encoding="utf-8"))
        if not matches_seen(bullet, baseline_seen | logged_seen)
    ]

    output = {
        "baseline": baseline,
        "head": git(repo, "rev-parse", "HEAD").strip(),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "topics": topic_inventory(repo),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
