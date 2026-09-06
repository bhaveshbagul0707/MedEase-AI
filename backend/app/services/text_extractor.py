from __future__ import annotations

from typing import List
from pypdf import PdfReader


def extract_text_pages_from_pdf(path: str) -> List[str]:
    """Attempt to extract text from PDF pages. If pypdf fails, fall back to reading raw text from file as a single page."""
    pages = []
    try:
        with open(path, "rb") as fh:
            reader = PdfReader(fh)
            for p in reader.pages:
                try:
                    t = p.extract_text() or ""
                except Exception:
                    t = ""
                pages.append(t)
    except Exception:
        # fallback: try reading the file as text
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
                pages = [content]
        except Exception:
            pages = [""]
    if not pages:
        pages = [""]
    return pages
