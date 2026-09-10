# Behavioral Data Science Research Lab

behavioral-data-science.org

## What we study

Behavior analysis has uncovered dozens of behavioral principles, but principles rarely act one at a time. The lab studies how they combine and interact into the behavior of a whole organism: over time, across contexts, and from the molecular, moment-to-moment control of behavior up to its molar, aggregate patterns. That question runs across a basic, translational, and applied continuum. In the lab, human operant experiments and artificial organisms let us test how processes combine. Out of the lab, that work moves into settings of social significance (e.g., ethics, clinical and autism service delivery, substance use, and even baseball). A common methodological backbone runs through all of it: rigorous science, a growing pile of data, and quantitative analysis.

The throughline is integration: molecular to molar, basic to applied, and back again.

## Lines of research

**Integrating principles.** At any moment, what an organism does is jointly controlled by many variables at once (e.g., the size of an outcome, how long until it arrives, how likely it is, what it costs, and what came just before). Studying a principle alone describes a slice of behavior; studying how principles combine begins to describe behavior itself. Our combination studies start in the value of choice, crossing delay with probability, effort with probability, and amount with delay, and asking how an organism's earnings budget reshapes those functions.

**Artificial organisms.** One way to test how behavioral principles integrate is to build them. We construct artificial organisms that combine principles and processes under a set of assumptions, then watch what reproduces real behavior and where things break down. Where the lab studies how processes interact in living organisms, this program asks whether the same processes, assembled from first principles, can generate the same patterns.

**Applied and translational domains.** Basic behavioral science earns its keep when it changes behavior and decisions in settings that matter: professional ethics, clinical decision-making, autism service delivery, substance use, and baseball, among others. We take a fundamental we understand well (e.g., discounting, the matching law, reinforcement, or a functional account of behavior) and ask what it buys us in a real setting, and which fundamentals still carry weight once the controlled conditions of the lab are gone.

**Methodological backbone.** New questions need new tools. Behavior analysis has a powerful, time-tested toolkit in single-subject design, visual analysis, and descriptive statistics. To ask questions the field has not been able to ask before, we build and share tools that bring machine learning, modern statistics, and computational modeling to behavioral data.

## Ambitions

The combination space between behavioral processes is thin rather than empty, and it is thinnest where the halves of the field meet. Across 46,988 articles in 22 behavior-analytic journals, 72 of the 325 pairings of the processes we track have never been co-studied at all, and 186 rest on fewer than five papers. Pairings amongst the classic operant processes carry a median of six papers; those joining one of them to a decision dimension (e.g., delay discounting, response effort, economic context) carry a median of one. The goal is to keep narrowing the gap between what we can model in isolation and how behavior actually operates as a whole. On the applied side, the thin translations and sparser domains on the map are where the next work lives, and we are always looking for partners in settings we have not yet reached who have a problem behavioral science could help solve. On the methods side, the aim is a field that can ask and answer questions the standard toolkit leaves out of range, which means continuing to build and give away tools rather than keep them in house.

Underneath all three is the same bet: that a rigorous, quantitative, data-driven behavior analysis, integrated across its own subfields rather than splintered into basic versus applied camps, is the most useful version of the science we can build.

## About this repository

This repository is the source for the lab's public website, a static site built with plain HTML, CSS, and JavaScript. It includes an interactive topic map of the lab's publications, books, and preprints; per-line-of-research pages under `area-*.html`; and a current-projects feed pulled from ClickUp and refreshed weekly by `.github/workflows/refresh-projects.yml`.

```
bds-lab-website/
├── index.html                    # Homepage and topic map
├── about.html                    # Lab members
├── projects.html                 # Current projects
├── publications.html             # Publications
├── books.html                    # Books and course companions
├── area-*.html                   # One page per line of research
├── data/                         # Corpus, landscape, and project data (JSON/JS)
├── scripts/                      # Build scripts that generate the data/ files
└── documents/                    # CV
```

The site has no runtime dependencies and can be previewed by opening `index.html` directly in a browser. To regenerate a data file, run the matching `scripts/build_*.py` script, with three caveats worth knowing before you do:

- `build_corpus.py` reads PDFs from `~/Dropbox/Articles`, and it takes each article's title from the **filename**, so a typo there ships to the public topic map. Run `build_layout.py` after it to place the new items.
- `build_landscape.py` needs the sibling `thesis-scaffold` repo for its 46,988-article field corpus, and it reports the counts the "combination landscape" prose quotes. Re-run it and the prose may need rewording.
- `build_areas.py` is **stale and should not be run**. The `area-*.html` pages have been rewritten by hand since it last ran, and it would overwrite that prose.

Lab members are listed on the [About](about.html) page. If you work in one of the domains above and want a behavioral-science partner on a question, or if you want to bring one of our methods to a question in your own research, reach out through the site.
