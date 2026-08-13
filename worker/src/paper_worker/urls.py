from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from .schemas import ItemType

ARXIV_RE = re.compile(
    r"(?:arxiv\.org/(?:abs|pdf)/)(\d{4}\.\d{4,5})(?:v\d+)?(?:\.pdf)?", re.IGNORECASE
)
DOI_RE = re.compile(
    r"(?:doi\.org/|doi:\s*)(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.IGNORECASE
)
OPENREVIEW_RE = re.compile(
    r"openreview\.net/(?:forum|pdf)\?id=([A-Za-z0-9_-]+)", re.IGNORECASE
)
TRACKING_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "ref",
    "source",
}


@dataclass(frozen=True)
class URLIdentity:
    normalized_url: str
    item_type: ItemType
    arxiv_id: str | None = None
    doi: str | None = None
    openreview_id: str | None = None
    github_repo: str | None = None


def normalize_url(raw_url: str) -> str:
    url = raw_url.strip().rstrip(".,;]")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    scheme = "https" if parsed.scheme in {"http", "https"} else parsed.scheme
    host = parsed.netloc.lower()
    host = host.removeprefix("www.")
    path = re.sub(r"/{2,}", "/", parsed.path)
    if path != "/":
        path = path.rstrip("/")
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in TRACKING_KEYS
    ]
    query.sort()
    return urlunparse((scheme, host, path, "", urlencode(query), ""))


def identify_url(raw_url: str) -> URLIdentity:
    normalized = normalize_url(raw_url)
    arxiv_match = ARXIV_RE.search(normalized)
    if arxiv_match:
        arxiv_id = arxiv_match.group(1)
        return URLIdentity(
            normalized_url=f"https://arxiv.org/abs/{arxiv_id}",
            item_type=ItemType.PAPER,
            arxiv_id=arxiv_id,
        )
    doi_match = DOI_RE.search(normalized)
    if doi_match:
        doi = doi_match.group(1).rstrip(".").lower()
        return URLIdentity(
            normalized_url=f"https://doi.org/{doi}", item_type=ItemType.PAPER, doi=doi
        )
    openreview_match = OPENREVIEW_RE.search(normalized)
    if openreview_match:
        openreview_id = openreview_match.group(1)
        return URLIdentity(
            normalized_url=f"https://openreview.net/forum?id={openreview_id}",
            item_type=ItemType.PAPER,
            openreview_id=openreview_id,
        )

    parsed = urlparse(normalized)
    host = parsed.netloc.lower()
    parts = [part for part in parsed.path.split("/") if part]
    if host == "github.com" and len(parts) >= 2:
        repo = f"{parts[0]}/{parts[1].removesuffix('.git')}"
        return URLIdentity(
            normalized_url=f"https://github.com/{repo}",
            item_type=ItemType.REPOSITORY,
            github_repo=repo.lower(),
        )
    if "dataset" in normalized.lower():
        item_type = ItemType.DATASET
    elif "benchmark" in normalized.lower() or "leaderboard" in normalized.lower():
        item_type = ItemType.BENCHMARK
    elif any(token in host for token in ("medium.com", "substack.com")) or "/blog" in parsed.path:
        item_type = ItemType.BLOG
    elif any(
        token in host for token in ("neurips.cc", "iclr.cc", "thecvf.com", "pmlr.press")
    ) or parsed.path.lower().endswith(".pdf"):
        item_type = ItemType.PAPER
    else:
        item_type = ItemType.PROJECT
    return URLIdentity(normalized_url=normalized, item_type=item_type)
