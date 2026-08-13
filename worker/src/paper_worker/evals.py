from __future__ import annotations

from pathlib import Path

import yaml

from .urls import normalize_url


def validate_eval_manifest(root: Path) -> dict:
    items = yaml.safe_load((root / "evals" / "golden-items.yaml").read_text(encoding="utf-8"))[
        "items"
    ]
    questions = yaml.safe_load(
        (root / "evals" / "robotics-questions.yaml").read_text(encoding="utf-8")
    )["questions"]
    branches = {item["branch"] for item in items}
    if len(items) != 30:
        raise ValueError(f"golden set must contain 30 items, found {len(items)}")
    unique_urls = {normalize_url(item["url"]) for item in items}
    if len(unique_urls) != len(items):
        raise ValueError("golden set must contain 30 distinct Research Items")
    if len(questions) < 50:
        raise ValueError(f"question set must contain at least 50 questions, found {len(questions)}")
    if len(branches) < 8:
        raise ValueError("golden set must cover at least eight Robotics branches")
    return {"items": len(items), "questions": len(questions), "branches": len(branches)}
