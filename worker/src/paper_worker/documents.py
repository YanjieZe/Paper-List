from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import pymupdf
import tiktoken
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class ExtractedChunk:
    ordinal: int
    page: int | None
    heading: str | None
    content: str
    bbox: tuple[float, float, float, float] | None
    token_count: int


@dataclass(frozen=True)
class ExtractedDocument:
    sha256: str
    byte_size: int
    page_count: int | None
    chunks: list[ExtractedChunk]


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _token_count(text: str) -> int:
    try:
        encoding = tiktoken.get_encoding("o200k_base")
        return len(encoding.encode(text))
    except (KeyError, ValueError):
        return max(1, len(text) // 4)


def _split_text(text: str, max_chars: int = 6000) -> list[str]:
    normalized = re.sub(r"[ \t]+", " ", text.replace("\x00", "")).strip()
    if len(normalized) <= max_chars:
        return [normalized] if normalized else []
    paragraphs = re.split(r"\n\s*\n", normalized)
    result: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > max_chars:
            result.append(current.strip())
            current = ""
        if len(paragraph) > max_chars:
            for start in range(0, len(paragraph), max_chars):
                part = paragraph[start : start + max_chars]
                if current:
                    result.append(current.strip())
                    current = ""
                result.append(part.strip())
        else:
            current += ("\n\n" if current else "") + paragraph
    if current.strip():
        result.append(current.strip())
    return result


def extract_pdf(path: Path) -> ExtractedDocument:
    content = path.read_bytes()
    document = pymupdf.open(stream=content, filetype="pdf")
    chunks: list[ExtractedChunk] = []
    ordinal = 0
    for page_index, page in enumerate(document):
        blocks = page.get_text("blocks", sort=True)
        for block in blocks:
            x0, y0, x1, y1, text, *_ = block
            for part in _split_text(str(text)):
                chunks.append(
                    ExtractedChunk(
                        ordinal=ordinal,
                        page=page_index + 1,
                        heading=None,
                        content=part,
                        bbox=(float(x0), float(y0), float(x1), float(y1)),
                        token_count=_token_count(part),
                    )
                )
                ordinal += 1
    return ExtractedDocument(
        sha256=sha256_bytes(content),
        byte_size=len(content),
        page_count=len(document),
        chunks=chunks,
    )


def extract_html(content: bytes) -> ExtractedDocument:
    soup = BeautifulSoup(content, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    chunks: list[ExtractedChunk] = []
    ordinal = 0
    current_heading: str | None = None
    for element in soup.find_all(["h1", "h2", "h3", "p", "li", "pre"]):
        text = element.get_text(" ", strip=True)
        if not text:
            continue
        if element.name in {"h1", "h2", "h3"}:
            current_heading = text
            continue
        for part in _split_text(text):
            chunks.append(
                ExtractedChunk(
                    ordinal=ordinal,
                    page=None,
                    heading=current_heading,
                    content=part,
                    bbox=None,
                    token_count=_token_count(part),
                )
            )
            ordinal += 1
    return ExtractedDocument(
        sha256=sha256_bytes(content), byte_size=len(content), page_count=None, chunks=chunks
    )
