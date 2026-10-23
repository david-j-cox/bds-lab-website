#!/usr/bin/env python3
"""Build data/publications.json (+ .js) for the publications page.

Sources:
  - Published articles, chapters, books, and white papers: the live CV
    (~/Dropbox/Curriculum Vitae/2026/David J. Cox CV.docx), parsed with pandoc.
  - Preprints, in-review, and in-press manuscripts: data/preprints.json (the
    curated list that already carries links and topic labels).
  - Entries missing from the CV or needing a fix: data/publications_extra.json.

Each entry is matched to its topic-map item (data/corpus.json) by title so the
page can color it by cluster and link to it on the map. Run after
build_corpus.py and build_layout.py. Deterministic; no network.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CV = Path.home() / "Dropbox/Curriculum Vitae/2026/David J. Cox CV.docx"

STOP = {"a", "an", "the", "of", "and", "in", "on", "for", "to", "with", "by", "as", "at", "or", "from", "is"}


def tokens(text):
    text = re.sub(r"\bml\b", "machine learning", text.lower())
    text = re.sub(r"\bai\b", "artificial intelligence", text)
    text = re.sub(r"\brl\b", "reinforcement learning", text)
    return {t for t in re.findall(r"[a-z0-9]+", text) if t not in STOP}


def similarity(a, b):
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    # corpus titles from filenames are often shortened, so score overlap
    # against the shorter title rather than the union
    return len(ta & tb) / min(len(ta), len(tb))


def plain(md):
    """Markdown fragment -> plain text (drop emphasis, escapes, mentee marks)."""
    s = re.sub(r"\[([^\]]*)\]\{[^}]*\}", r"\1", md)
    s = s.replace("\\*", "").replace("\\^", "").replace("\\", "")
    s = s.replace("*", "")
    return re.sub(r"\s+", " ", s).strip()


def cv_sections():
    md = subprocess.run(["pandoc", str(CV), "-t", "markdown", "--wrap=none"],
                        capture_output=True, text=True, check=True).stdout
    md = md[md.index("PUBLICATIONS]"):md.index("**RESEARCH SUPPORT**")]
    # join wrapped continuation lines (a line ending in "\" continues)
    md = re.sub(r"\\\n\s*", " ", md)
    sections, current = {}, None
    for line in md.split("\n"):
        h = re.match(r"\*\*([^*]+)\*\*", line.strip())
        if h and not re.match(r"\s*\d+\\\.", line):
            current = h.group(1).strip()
            sections[current] = []
            continue
        if current and line.strip() and not line.strip().startswith("--"):
            sections[current].append(re.sub(r"^\s*\d+\\\.\s+", "", line).strip())
    return sections


def parse_citation(md, kind_hint=None):
    m = re.search(r"\((\d{4})[^)]*\)\.?\s*", md)
    if not m:
        return None
    authors = plain(md[:m.start()]).rstrip(",")
    year = int(m.group(1))
    rest = md[m.end():]
    links = re.findall(r"<(https?://[^>]+)>", rest)
    rest = re.sub(r"<https?://[^>]+>", "", rest).strip()
    link = links[-1] if links else None
    if not link:
        bare = re.search(r"https?://\S+", rest)
        if bare:
            link = bare.group(0).rstrip(".")
            rest = rest.replace(bare.group(0), "").strip()

    chapter = re.search(r"\.\s+In\s+.*?\(Eds?\.?\)", rest)
    if kind_hint == "book":
        kind = "book"
        # title is the italic span when present, else up to the publisher
        it = re.search(r"\*([^*]+)\*", rest)
        if it and rest.index("*") < 3:
            title, venue = it.group(1), rest[it.end():]
        else:
            title, _, venue = plain(rest).partition(". ")
    elif chapter:
        kind = "chapter"
        title, venue = rest[:chapter.start()], rest[chapter.start() + 1:]
    else:
        kind = "article"
        # the venue is the italic run after the title's closing period; an
        # italic word inside the title (e.g., *N*) is not a sentence break
        stars = [i for i, c in enumerate(rest) if c == "*"]
        breaks = [i for i in stars if rest[max(0, i - 2):i] == ". " or rest[i + 1:i + 3] == ". "]
        star = breaks[0] if breaks else (stars[0] if stars else -1)
        title, venue = (rest[:star], rest[star:]) if star > 0 else (rest, "")
    title = plain(title).rstrip(". ")
    venue = plain(venue).strip(" .").lstrip(". ")
    venue = re.sub(r"\s*ISBN:?\s*[\dX-]+", "", venue).strip(" .")
    return {"kind": kind, "year": year, "authors": authors, "title": title,
            "venue": venue, "link": link}


def parse_report(md):
    m = re.match(r"(.+?)\s*\(([A-Za-z]+),?\s*(\d{4})\)\.\s*(.*)", md)
    if not m:
        return None
    rest = m.group(4)
    links = re.findall(r"<(https?://[^>]+)>", rest)
    title = plain(re.sub(r"<https?://[^>]+>", "", rest)).rstrip("./ ")
    return {"kind": "report", "year": int(m.group(3)), "authors": plain(m.group(1)),
            "title": title, "venue": "White paper", "link": links[-1] if links else None}


def main():
    corpus = json.loads((DATA / "corpus.json").read_text())
    items = corpus if isinstance(corpus, list) else corpus["items"]
    clusters = {c["id"]: c["label"] for c in corpus["meta"]["clusters"]} if isinstance(corpus, dict) else {}
    by_id = {it["id"]: it for it in items}

    pubs = []
    sec = cv_sections()
    published = next(k for k in sec if k.startswith("Accepted/In Press/Published"))
    for line in sec[published]:
        p = parse_citation(line)
        if p:
            p["status"] = "published"
            pubs.append(p)
    for line in sec.get("BOOKS", []):
        if "expected" in line or "under contract" in line:
            continue
        p = parse_citation(line, kind_hint="book")
        if p:
            p["status"] = "published"
            pubs.append(p)
    for key in sec:
        if key.startswith("INDUSTRY WHITE PAPERS"):
            for line in sec[key]:
                p = parse_report(line)
                if p:
                    p["status"] = "published"
                    pubs.append(p)

    extra = json.loads((DATA / "publications_extra.json").read_text())
    pubs.extend(extra.get("add", []))

    # curated preprints / in review / in press, already tied to corpus ids;
    # the CV's "In Review" list supplies the journal each one is under review at
    in_review = [parse_citation(l.replace("(*in review*)", "(0000)")) for l in sec.get("In Review", [])]
    in_review = [r for r in in_review if r]
    have = {p.get("map") for p in pubs}
    for pr in json.loads((DATA / "preprints.json").read_text()):
        if pr["id"] in have:
            continue
        status = pr.get("type", "preprint")
        venue = ""
        if status == "inreview" and in_review:
            best = max(in_review, key=lambda r: similarity(pr["title"], r["title"]))
            if similarity(pr["title"], best["title"]) >= 0.6:
                v = best["venue"]
                book = re.search(r"\(Eds?\.?\)\s*(.+)", v)
                venue = ("Under review as a chapter in " + book.group(1)) if book else ("Under review at " + v)
        for frag, v in extra.get("venue", {}).items():
            if frag.lower() in pr["title"].lower():
                venue = v
        pubs.append({"kind": "article", "status": status, "year": None,
                     "authors": pr["authors"], "title": pr["title"], "venue": venue,
                     "link": pr.get("url"), "map": pr["id"]})

    # a white paper that is also listed as a preprint shows once, as the preprint
    preprint_titles = [p["title"] for p in pubs if p["status"] != "published"]
    pubs = [p for p in pubs if not (p["kind"] == "report" and
            any(similarity(p["title"], t) >= 0.9 for t in preprint_titles))]

    # match each entry to its topic-map item
    forced = extra.get("match", {})
    unmatched = []
    for p in pubs:
        if p.get("map"):
            continue
        hit = next((cid for frag, cid in forced.items() if frag.lower() in p["title"].lower()), None)
        if hit is None:
            pool = [it for it in items if it["type"] in ("article", "book")]
            best = max(pool, key=lambda it: similarity(p["title"], it["title"]))
            score = similarity(p["title"], best["title"])
            yr_ok = best.get("year") in (None, p["year"]) or best["type"] == "book"
            hit = best["id"] if score >= 0.6 and yr_ok else None
        p["map"] = hit
        if hit is None:
            unmatched.append(f'{p["year"]} {p["title"][:70]}')

    for p in pubs:
        it = by_id.get(p["map"]) if p["map"] else None
        p["cluster"] = it.get("cluster") if it else None
        p["topic"] = clusters.get(p["cluster"]) if it else None
        p["id"] = re.sub(r"[^a-z0-9]+", "-", f'{p["year"] or p["status"]}-{p["title"].lower()}')[:70].strip("-")

    order = {"inpress": 0, "inreview": 1, "preprint": 2, "published": 3}
    pubs.sort(key=lambda p: (order[p["status"]], -(p["year"] or 0), p["title"].lower()))
    out = {"clusters": [{"id": k, "label": v} for k, v in sorted(clusters.items())], "items": pubs}
    (DATA / "publications.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    (DATA / "publications.js").write_text("window.PUBS = " + json.dumps(out, ensure_ascii=False) + ";\n")

    from collections import Counter
    print("entries:", len(pubs), dict(Counter(p["kind"] for p in pubs)), dict(Counter(p["status"] for p in pubs)))
    print(f"matched to map: {sum(1 for p in pubs if p['map'])}/{len(pubs)}")
    for u in unmatched:
        print("  unmatched:", u)


if __name__ == "__main__":
    main()
