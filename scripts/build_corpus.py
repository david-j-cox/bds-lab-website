#!/usr/bin/env python3
"""Build data/corpus.json from the Dropbox article + book corpus.

Parses article filenames of the form "(YEAR) Title, Authors.pdf" and pulls
page 1-2 text via pdftotext to give the topic-layout step richer signal.
Books are taken from folder names. PDFs themselves are never copied into the
repo (publisher copyright) - only derived metadata + abstract text.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ARTICLES = Path.home() / "Dropbox/Articles/My Articles"
BOOKS = Path.home() / "Dropbox/Articles/My Books"
OUT = Path(__file__).resolve().parent.parent / "data" / "corpus.json"

YEAR_RE = re.compile(r"^\((\d{4})\)\s*(.*)$")


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60]


def parse_article_name(stem: str):
    """'(2021) Title, Authors' -> (year, title, authors)."""
    m = YEAR_RE.match(stem)
    if not m:
        return None, stem.strip(), ""
    year = int(m.group(1))
    rest = m.group(2).strip()
    # Authors are the trailing chunk after the last comma; titles may contain
    # commas, so split on the LAST ', '.
    if ", " in rest:
        title, authors = rest.rsplit(", ", 1)
    else:
        title, authors = rest, ""
    # Normalise a few quirks
    authors = authors.rstrip(".").strip()
    title = title.strip()
    return year, title, authors


# Lines matching these are journal/affiliation boilerplate, not topic signal.
NOISE_LINE = re.compile(
    r"(university|department|institute|college|@|http|www\.|doi|"
    r"contents lists|sciencedirect|elsevier|springer|wiley|sage|taylor|"
    r"journal homepage|published online|copyright|©|all rights reserved|"
    r"^\s*\d|drive|street|gainesville|berkeley|llc|corresponding author)",
    re.IGNORECASE,
)
# Tolerate spaced letters ("a b s t r a c t") that Elsevier/Springer PDFs emit.
ABSTRACT_RE = re.compile(r"a\s?b\s?s\s?t\s?r\s?a\s?c\s?t", re.IGNORECASE)
STOP_AT = re.compile(r"(keywords?|introduction|©|\b1\.\s)", re.IGNORECASE)
DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")


def extract_doi(raw: str):
    m = DOI_RE.search(raw)
    if not m:
        return None
    # Trim trailing punctuation that regex tends to grab.
    return m.group(0).rstrip(".,;)")


def pdf_extract(path: Path, max_chars: int = 1500):
    """Return (abstract, doi) from the first two pages of a PDF."""
    try:
        out = subprocess.run(
            ["pdftotext", "-f", "1", "-l", "2", "-nopgbrk", str(path), "-"],
            capture_output=True, timeout=30,
        )
        raw = out.stdout.decode("utf-8", "ignore")
    except Exception:
        return "", None
    doi = extract_doi(raw)
    return _abstract_from_raw(raw, max_chars), doi


def _polish(text: str) -> str:
    """Strip leftover journal-header signatures from the front of an abstract."""
    # Journal name + volume + (year) + pages, sometimes doubled by column order.
    for _ in range(2):
        text = re.sub(r"^\s*[A-Z][A-Za-z.&\- ]{3,40}\s+\d{1,4}\s*\(\d{4}\)\s*[\d:–—\-]*\s*", "", text)
    text = re.sub(r"^(BOOK REVIEW|RESEARCH ARTICLE|ORIGINAL ARTICLE|ARTICLE HISTORY|ARTICLE)\b[:\s]*", "", text, flags=re.I)
    # Leading run of ALL-CAPS words (journal / title / author block in caps).
    text = re.sub(r"^([A-Z][A-Z.]+[,]?\s+){2,}", "", text)
    return text.strip()


def _abstract_from_raw(raw: str, max_chars: int) -> str:
    # Prefer the real abstract: the chunk after an "Abstract" heading, cut at
    # "Keywords"/"Introduction".
    # Use the last marker within the front matter (Elsevier puts the spaced
    # "a b s t r a c t" after the keywords block).
    marks = [mm for mm in ABSTRACT_RE.finditer(raw) if mm.start() < 3500]
    if marks:
        m = marks[-1]
        chunk = raw[m.end(): m.end() + 2500]
        stop = STOP_AT.search(chunk)
        if stop:
            chunk = chunk[: stop.start()]
        text = _polish(re.sub(r"\s+", " ", chunk).strip())
        if len(text) > 120:
            return text[:max_chars]
    # Fallback: drop affiliation/journal lines, keep prose lines.
    keep = [ln for ln in raw.splitlines() if ln.strip() and not NOISE_LINE.search(ln)]
    text = _polish(re.sub(r"\s+", " ", " ".join(keep)).strip())
    return text[:max_chars]


def build_articles():
    items = []
    if not ARTICLES.exists():
        print(f"WARN: {ARTICLES} not found", file=sys.stderr)
        return items
    for p in sorted(ARTICLES.iterdir()):
        if p.suffix.lower() not in (".pdf", ".docx"):
            continue
        year, title, authors = parse_article_name(p.stem)
        abstract, doi = pdf_extract(p) if p.suffix.lower() == ".pdf" else ("", None)
        items.append({
            "id": slugify(f"{year}-{title}"),
            "type": "article",
            "year": year,
            "title": title,
            "authors": authors,
            "filename": p.name,
            "abstract": abstract,
            "doi": doi,
        })
    return items


# Book folders to exclude from the corpus / topic map.
EXCLUDE_BOOKS = {"CodingForBehaviorAnalysts"}


def build_books():
    items = []
    if not BOOKS.exists():
        return items
    for d in sorted(BOOKS.iterdir()):
        if not d.is_dir() or d.name in EXCLUDE_BOOKS:
            continue
        name = d.name
        # Strip a trailing ", Cox et al." style author tag from the title
        title = re.sub(r",\s*Cox.*$", "", name).strip()
        items.append({
            "id": slugify(f"book-{title}"),
            "type": "book",
            "year": None,
            "title": title,
            "authors": "",
            "filename": name,
            "abstract": "",
        })
    return items


def build_preprints():
    """Curated preprints (not in the article folder) from data/preprints.json."""
    path = OUT.parent / "preprints.json"
    if not path.exists():
        return []
    items = []
    for p in json.loads(path.read_text()):
        items.append({
            "id": p["id"],
            "type": "preprint",
            "year": None,
            "title": p["title"],
            "authors": p.get("authors", ""),
            "filename": None,
            "abstract": "",
            "doi": None,
            "url": p.get("url"),
            "label": p.get("label"),
        })
    return items


def main():
    articles = build_articles()
    books = build_books()
    preprints = build_preprints()
    corpus = articles + books + preprints
    print(f"preprints={len(preprints)}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(corpus, indent=2, ensure_ascii=False))
    n_abs = sum(1 for a in articles if a["abstract"])
    print(f"articles={len(articles)} (abstracts={n_abs}) books={len(books)} -> {OUT}")


if __name__ == "__main__":
    main()
