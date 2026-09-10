#!/usr/bin/env python3
"""Build data/landscape.json for the 'Integrating principles' combination matrix.

Field cells come from the behavior-analytic literature corpus in the sibling
thesis-scaffold repo: 46,988 articles across 22 journals, 1956 to 2026, with
abstracts for most. Processes are detected by deterministic phrase matching
(scripts/process_terms.py) over title + abstract, so the build stays offline,
reproducible, and free of any embedding or API dependency.

Lab cells are derived the same way from the lab's own corpus (data/corpus.json),
which means adding a publication and re-running build_corpus.py is enough to put
it on the matrix. A short hand-curated list supplements that for collaborations
whose PDFs are not in the lab article folder.

Re-run after build_corpus.py. Falls back to the previous catalog source only if
the thesis-scaffold corpus is missing.
"""
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from process_terms import GROUPS, IDS, LABELS, detect  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIELD_CORPUS = ROOT.parent / "thesis-scaffold" / "data" / "corpus.json"
LAB_CORPUS = ROOT / "data" / "corpus.json"
OUT = ROOT / "data" / "landscape.json"

# Most-cited articles kept per cell for the click-through panel. The full count
# is reported separately, so capping here only trims the reading list.
REFS_PER_CELL = 8
TITLE_CAP = 150

# Collaborations and preprints behind lab cells whose PDFs are not in the lab
# article folder, so the corpus cannot find them. Everything else is derived.
EXTRA_LAB = [
    (["delay_disc", "prob_disc"], "Further comparison of 5-trial adjusting delay and probability tasks (Miranda et al., 2018)", "10.1016/beproc.2018.08.004"),
    (["delay_disc", "sign"], "Multiplicative vs additive hyperbolic discounting, gains and losses (Bialaszek et al., 2020)", "10.1371/journal.pone.0233337"),
    (["prob_disc", "sign"], "Multiplicative vs additive hyperbolic discounting, gains and losses (Bialaszek et al., 2020)", "10.1371/journal.pone.0233337"),
]


def short_authors(authors):
    """OpenAlex author records or a plain string -> 'Cox et al.'"""
    if isinstance(authors, str):
        return authors
    names = []
    for a in authors or []:
        n = (a.get("display_name") or "").strip() if isinstance(a, dict) else str(a).strip()
        if n:
            names.append(n.split()[-1])
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} & {names[1]}"
    return f"{names[0]} et al."


def build_field():
    """Scan the field corpus; return (scanned, articles, {(a,b): [index, ...]})."""
    corpus = json.loads(FIELD_CORPUS.read_text())
    scanned = len(corpus["articles"])
    articles, refs = [], defaultdict(list)
    for a in corpus["articles"]:
        title = (a.get("title") or "").strip()
        if not title:
            continue
        ids = detect(title + " " + (a.get("abstract") or ""))
        if len(ids) < 2:
            continue
        authors = a.get("authors")
        if isinstance(authors, str):          # some rows arrive pre-stringified
            try:
                authors = json.loads(authors.replace("'", '"'))
            except (ValueError, TypeError):
                authors = []
        try:
            cited = int(a.get("cited_by") or 0)
        except (TypeError, ValueError):
            cited = 0
        idx = len(articles)
        articles.append({
            "t": title[:TITLE_CAP],
            "a": short_authors(authors),
            "y": a.get("year"),
            "u": a.get("doi") or "",
            "c": cited,
        })
        for x, y in combinations(sorted(ids), 2):
            refs[(x, y)].append(idx)
    return scanned, articles, refs


def build_lab():
    """Derive lab cells from the lab's own corpus, plus the curated extras."""
    items = json.loads(LAB_CORPUS.read_text())["items"]
    cells = defaultdict(list)
    for it in items:
        ids = detect((it.get("title") or "") + " " + (it.get("abstract") or ""))
        if len(ids) < 2:
            continue
        study = (it.get("title") or "").strip()[:TITLE_CAP]
        doi = it.get("doi") or it.get("url") or ""
        for x, y in combinations(sorted(ids), 2):
            cells[(x, y)].append({"study": study, "doi": doi})
    for procs, study, doi in EXTRA_LAB:
        for x, y in combinations(sorted(set(procs)), 2):
            if not any(s["study"] == study for s in cells[(x, y)]):
                cells[(x, y)].append({"study": study, "doi": doi})
    return cells


def main():
    if not FIELD_CORPUS.exists():
        sys.exit(f"field corpus not found at {FIELD_CORPUS}")

    scanned, articles, field_refs = build_field()
    lab_cells = build_lab()

    # Keep only the most-cited articles per cell, then drop articles nothing
    # points at any more so the payload stays small.
    field = []
    keep = set()
    for (a, b), idxs in field_refs.items():
        top = sorted(idxs, key=lambda i: -articles[i]["c"])[:REFS_PER_CELL]
        keep.update(top)
        field.append({"a": a, "b": b, "n": len(idxs), "refs": top})
    remap = {old: new for new, old in enumerate(sorted(keep))}
    kept = [{k: v for k, v in articles[i].items() if k != "c"} for i in sorted(keep)]
    for f in field:
        f["refs"] = [remap[i] for i in f["refs"]]

    out = {
        "processes": [{"id": i, "label": LABELS[i], "group": GROUPS[i]} for i in IDS],
        "articles": kept,
        "field": field,
        "lab": [{"a": a, "b": b, "studies": s} for (a, b), s in sorted(lab_cells.items())],
        "meta": {
            "field_articles_scanned": scanned,
            "field_articles_matched": len(articles),
        },
    }
    OUT.write_text(json.dumps(out))
    (ROOT / "data" / "landscape.js").write_text("window.LANDSCAPE = " + json.dumps(out) + ";\n")

    total = len(IDS) * (len(IDS) - 1) // 2
    print(f"processes={len(IDS)} field-articles={len(articles)} kept={len(kept)}")
    print(f"field-cells={len(field)}/{total}  lab-cells={len(out['lab'])}")
    for t in (5, 10, 25):
        print(f"  cells with n>={t}: {sum(1 for f in field if f['n'] >= t)}")
    print(f"landscape.json = {OUT.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
