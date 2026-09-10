#!/usr/bin/env python3
"""Rewrite the Preprints section of publications.html from data/preprints.json.

Keeps the public list in step with the topic-map source of truth, so adding or
promoting a preprint is a one-file edit plus a re-run. Items typed "inpress" are
skipped: those are forthcoming publications and already sit in the main list.
Re-run after editing data/preprints.json.
"""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "preprints.json"
PAGE = ROOT / "publications.html"
START = "                    <!-- BUILD:preprints -->\n"
END = "                    <!-- /BUILD:preprints -->\n"

KIND = {"inreview": "In Review", "preprint": "Preprint"}


def card(item):
    kind = KIND.get(item.get("type", "preprint"), "Preprint")
    link = ""
    if item.get("url"):
        link = (
            '                        <div class="publication-links">\n'
            f'                            <a href="{escape(item["url"], quote=True)}" target="_blank" '
            'class="cyber-button small">LINK TO PREPRINT</a>\n'
            "                        </div>\n"
        )
    return (
        '                    <article class="publication-item">\n'
        f'                        <div class="publication-year">{kind}</div>\n'
        f'                        <h3 class="publication-title">{escape(item["title"])}</h3>\n'
        f'                        <p class="publication-authors">{escape(item.get("authors", ""))}</p>\n'
        f"{link}"
        "                    </article>\n"
    )


def main():
    items = [x for x in json.loads(SRC.read_text()) if x.get("type") != "inpress"]
    # In review first, then preprints; preserve file order within each group.
    items.sort(key=lambda x: x.get("type") != "inreview")
    block = "\n".join(card(x) for x in items)

    page = PAGE.read_text()
    i, j = page.index(START), page.index(END)
    PAGE.write_text(page[: i + len(START)] + block + page[j:])
    print(f"wrote {len(items)} preprints into {PAGE.name}")


if __name__ == "__main__":
    main()
