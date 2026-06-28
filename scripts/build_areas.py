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
items = {it["id"]: it for it in corpus["items"]}
assign = json.loads((ROOT / "data" / "labels.json").read_text())["assign"]

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
    dict(
        file="area-integrating-principles.html",
        kicker="Basic research &middot; Human operant",
        title="Integrating behavioral principles",
        labels=["Basic Principles and Their Interactions"],
        narrative=(
            "Behavior analysis has identified dozens of principles, but principles rarely act one at "
            "a time. This line of work uses human operant experiments to study how individual processes "
            "&mdash; discounting, choice, reinforcement, resurgence, and the multiple control of behavior "
            "&mdash; combine and interact to produce the behavior of a whole organism, from moment-to-moment "
            "(molecular) control up to aggregate (molar) patterns. These controlled studies establish the "
            "raw material that everything else is built on."),
        extra="",
    ),
    dict(
        file="area-artificial-organisms.html",
        kicker="Basic research &middot; Artificial organisms",
        title="Artificial organisms",
        labels=["Artificial organisms"],
        narrative=(
            "&ldquo;What I cannot create, I do not understand.&rdquo; One way we test how behavioral "
            "principles integrate is to <strong>build it</strong> &mdash; constructing artificial organisms "
            "that combine principles and processes under different assumptions, then watching what reproduces "
            "real behavior and where things break down. Where the lab studies how processes interact in living "
            "organisms, this program asks whether the same processes, assembled from first principles, can "
            "generate the same patterns."),
        extra=('<div class="publication-links" style="margin-top:1.4rem">'
               '<a href="ao-lab-update.html" class="cyber-button" style="font-size:.85rem;padding:.7rem 1.2rem">'
               'Open the Lab Update &rarr;</a></div>'),
    ),
    dict(
        file="area-applied-domains.html",
        kicker="Translational &middot; Applied",
        title="Applied &amp; translational domains",
        labels=[
            "Translating Basic Principles to Non-Laboratory Settings",
            "Ethics & ethical decision-making",
            "Clinical Decision-Making",
            "Substance use",
        ],
        narrative=(
            "Basic science earns its keep when it changes behavior and decisions in settings that matter. "
            "This work carries validated combinations of principles out of the lab and into messier, socially "
            "important domains &mdash; translating basic principles to non-laboratory settings, ethics and "
            "ethical decision-making, clinical decision-making, and substance use. Out here, new constraints "
            "reveal which principles actually matter, and the problems we meet pose fresh basic questions."),
        extra="",
    ),
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
            "computational, and statistical methods we use to model behavior&ndash;environment relations, and the "
            "research methodologies &mdash; measurement, design, and analysis &mdash; that let us see interactions "
            "in the first place and move findings from one level of analysis to the next."),
        extra="",
    ),
]


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def paper_html(it):
    yr = it["year"] if it["year"] else "Book"
    meta = esc(it["authors"]) + (" &middot; " if it["authors"] else "") + str(yr)
    doi = it.get("doi")
    if doi:
        meta += f' &middot; <a href="https://doi.org/{esc(doi)}" target="_blank" rel="noopener">DOI</a>'
    return (f'                    <div class="project-item">\n'
            f'                        <h4 class="project-title">'
            f'<a href="index.html#paper={it["id"]}">{esc(it["title"])}</a></h4>\n'
            f'                        <p class="project-description">{meta}</p>\n'
            f'                    </div>')


def groups_html(labels):
    out = []
    for lab in labels:
        members = [items[i] for i, l in assign.items() if l == lab and i in items]
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
    n = sum(1 for i, l in assign.items() if l in a["labels"])
    print(f"wrote {a['file']}  ({n} items)")
