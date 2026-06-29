#!/usr/bin/env python3
"""Generate the four research-area deep-dive pages from the corpus + hand labels.

Each page = a narrative intro (the lab's framing) + the actual papers/books the
PI assigned to that area's labels (from data/labels.json), grouped by label and
linked to open on the topic map. Re-run after re-labeling to keep them in sync.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
corpus = json.loads((ROOT / "data" / "corpus.json").read_text())
ITEMS = corpus["items"]
assign = json.loads((ROOT / "data" / "labels.json").read_text())["assign"]
# Items may carry their own label (preprints); labels.json wins otherwise.
label_of = lambda it: assign.get(it["id"]) or it.get("label")

NAV = """        <header class="cyber-header">
            <div class="header-content">
                <h1 class="lab-title">
                    <span class="glitch">BEHAVIORAL DATA SCIENCE</span>
                    <span class="lab-subtitle">RESEARCH LAB</span>
                </h1>
                <div class="pliny-logo"><div class="pliny-container">
                    <img src="images/Pliny-the-Pigeon.png" alt="Pliny the Pigeon" class="pliny-image">
                </div></div>
            </div>
        </header>

        <nav class="cyber-nav">
            <ul class="nav-list">
                <li><a href="index.html" class="nav-link">TOPIC MAP</a></li>
                <li><a href="about.html" class="nav-link">ABOUT US</a></li>
                <li><a href="projects.html" class="nav-link">CURRENT PROJECTS</a></li>
                <li><a href="publications.html" class="nav-link">PUBLICATIONS</a></li>
                <li><a href="books.html" class="nav-link">BOOKS &amp; COURSE COMPANIONS</a></li>
                <li><a href="https://david-j-cox.github.io/planarian-live/" class="nav-link" target="_blank" rel="noopener"><span style="color:#39ff14;">&#9679;</span> LIVE RIG</a></li>
            </ul>
        </nav>"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Behavioral Data Science Research Lab</title>
    <link rel="icon" type="image/png" href="images/Pliny-the-Pigeon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="site.css">
</head>
<body>
    <div class="cyberpunk-container">
{nav}

        <main class="cyber-main">
            <p class="area-back"><a href="index.html">&larr; Back to the topic map</a></p>
            <section class="page-header" style="text-align:left;border:none;margin-bottom:18px">
                <div class="area-kicker">{kicker}</div>
                <h2 class="cyber-h2" style="text-align:left">{title}</h2>
            </section>

            <div class="about-card">
                <p class="cyber-text" style="font-size:1.02rem;color:var(--ink)">{narrative}</p>
                {extra}
            </div>
{groups}
        </main>

        <footer class="cyber-footer">
            <div class="footer-content">
                <p>&copy; 2025 Behavioral Data Science Research Lab</p>
            </div>
        </footer>
    </div>
</body>
</html>
"""

AREAS = [
    # NOTE: area-integrating-principles.html is now a hand-built deck (the
    # combination-landscape page). It is intentionally not generated here.
    dict(
        file="area-artificial-organisms.html",
        kicker="Basic research &middot; Artificial organisms",
        title="Artificial organisms",
        labels=["Artificial organisms"],
        narrative=(
            "&ldquo;What I cannot create, I do not understand.&rdquo; One way we test how behavioral "
            "principles integrate is to build them. We construct artificial organisms that combine principles "
            "and processes under a set of assumptions, then watch what reproduces real behavior and where "
            "things break down. Where the lab studies how processes interact in living organisms, this program "
            "asks a related question: can the same processes, assembled from first principles, generate the "
            "same patterns?"),
        extra=('<div class="publication-links" style="margin-top:1.4rem">'
               '<a href="ao-lab-update.html" class="cyber-button" style="font-size:.85rem;padding:.7rem 1.2rem">'
               'Open the Lab Update &rarr;</a></div>'),
    ),
    # area-applied-domains.html is hand-built (the translation-map deck); do not generate it here.
    dict(
        file="area-methodological-backbone.html",
        kicker="Data &middot; science &middot; mathematics",
        title="Methodological backbone",
        labels=[
            "Quantitative, computational & statistical methods",
            "Research Methodologies",
        ],
        narrative=(
            "Running beneath every project is a common methodological spine. This area covers the quantitative, "
            "computational, and statistical methods we use to model environment-behavior relations, along with "
            "the research methodologies (e.g., measurement, design, and analysis) that let us see interactions "
            "in the first place and move findings from one level of analysis to the next."),
        extra="",
    ),
]


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def paper_html(it):
    yr = it["year"] if it["year"] else ("Preprint" if it["type"] == "preprint" else "Book")
    meta = esc(it["authors"]) + (" &middot; " if it["authors"] else "") + str(yr)
    link = it.get("url") or (f'https://doi.org/{it["doi"]}' if it.get("doi") else None)
    if link:
        word = "Preprint" if it["type"] == "preprint" else "DOI"
        meta += f' &middot; <a href="{esc(link)}" target="_blank" rel="noopener">{word}</a>'
    return (f'                    <div class="project-item">\n'
            f'                        <h4 class="project-title">'
            f'<a href="index.html#paper={it["id"]}">{esc(it["title"])}</a></h4>\n'
            f'                        <p class="project-description">{meta}</p>\n'
            f'                    </div>')


def groups_html(labels):
    out = []
    for lab in labels:
        members = [it for it in ITEMS if label_of(it) == lab]
        members.sort(key=lambda it: (it["year"] or 0), reverse=True)
        if not members:
            continue
        rows = "\n".join(paper_html(it) for it in members)
        out.append(
            f'            <div class="project-category">\n'
            f'                <h3 class="category-title">{esc(lab)} '
            f'<span style="color:var(--faint);font-weight:400">({len(members)})</span></h3>\n'
            f'                <div class="project-list">\n{rows}\n                </div>\n'
            f'            </div>')
    return "\n".join(out)


for a in AREAS:
    html = PAGE.format(nav=NAV, kicker=a["kicker"], title=a["title"],
                       narrative=a["narrative"], extra=a["extra"],
                       groups=groups_html(a["labels"]))
    (ROOT / a["file"]).write_text(html)
    n = sum(1 for it in ITEMS if label_of(it) in a["labels"])
    print(f"wrote {a['file']}  ({n} items)")
