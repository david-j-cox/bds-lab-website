#!/usr/bin/env python3
"""Build data/current-projects.js from the curated data/current-projects.json.

The map's project rings used to be generated straight from open ClickUp tasks,
which put raw internal task names on a public page ("Choice Lit Review Next
Draft", the same project listed twice at two stages, and so on). Projects are
now hand-curated: each entry carries the same title and description shown on
projects.html, plus the topic-map label it belongs under.

To add one, append to data/current-projects.json and re-run this script. Use
scripts/clickup_draft.py to dump open ClickUp tasks as a starting point for
that curation; its output is never published.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "current-projects.json"
CORPUS = ROOT / "data" / "corpus.json"
OUT = ROOT / "data" / "current-projects.js"


def main():
    projects = json.loads(SRC.read_text())
    # Resolve each label to the cluster id the map currently uses, rather than
    # hardcoding ids that shift whenever the corpus is relabelled.
    clusters = json.loads(CORPUS.read_text())["meta"]["clusters"]
    by_label = {c["label"]: c["id"] for c in clusters}

    out, bad = [], []
    for p in projects:
        cid = by_label.get(p["label"])
        if cid is None:
            bad.append(p["label"])
            continue
        out.append({
            "title": p["title"],
            "desc": p.get("desc", ""),
            "cluster": cid,
            "category": p.get("section", "Current"),
            "source": "curated",
        })
    if bad:
        sys.exit("labels not present in the corpus clusters: " + ", ".join(sorted(set(bad)))
                 + "\nvalid labels: " + ", ".join(sorted(by_label)))

    OUT.write_text("window.CURRENT_PROJECTS = " + json.dumps(out, ensure_ascii=False) + ";\n")
    print(f"current projects: {len(out)} -> {OUT.name}")
    for p in out:
        print(f"  [{p['category']}] {p['title'][:60]}")


if __name__ == "__main__":
    main()
