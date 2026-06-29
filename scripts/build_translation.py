#!/usr/bin/env python3
"""Build data/translation.json for the Applied-domains 'translation map'.

Left = fundamentals (what gets translated); right = applied domains (where it
lands). Each applied paper is a bridge from one fundamental to one domain.
Mappings are a first-draft curation (match each paper by a title substring),
meant to be corrected.
"""
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
corpus = {it["id"]: it for it in json.loads((ROOT / "data" / "corpus.json").read_text())["items"]}
assign = json.loads((ROOT / "data" / "labels.json").read_text())["assign"]
APPLIED = {"Translating Basic Principles to Non-Laboratory Settings",
           "Ethics & ethical decision-making", "Clinical Decision-Making", "Substance use"}

FUNDAMENTALS = [
    ("beh_econ", "Behavioral economics and discounting", "principle"),
    ("matching", "Matching Law", "principle"),
    ("reinforcement", "Reinforcement and reinforcer assessment", "principle"),
    ("verbal", "Verbal behavior", "principle"),
    ("ethics_fn", "Functional account of ethical behavior", "principle"),
    ("stim_control", "Stimulus control and equivalence-based instruction", "principle"),
    ("design", "Experimental design and measurement", "method"),
    ("modeling", "Quantitative, computational, and AI modeling", "method"),
]
DOMAINS = [
    ("ethics", "Professional and research ethics"),
    ("clinical", "Clinical decision-making"),
    ("autism", "Autism and ABA service delivery"),
    ("substance", "Substance use and addiction"),
    ("baseball", "Sports (baseball)"),
    ("animal", "Animal behavior and training"),
    ("org", "Organizations and value-based care"),
    ("ai", "AI in practice"),
    ("health", "Public and sexual health"),
]

# (title substring, fundamental, domain) -- first match wins.
MAP = [
    ("balanced outcomes measurement", "design", "org"),
    ("practice parameters for ai use", "modeling", "ai"),
    ("qualitative analysis of expert interviews on safety", "design", "clinical"),
    ("promises and possibilities of ai", "modeling", "ai"),
    ("what's the big idea", "design", "autism"),
    ("staff training strategies that minimize", "reinforcement", "org"),
    ("choice with ethical outcomes", "beh_econ", "ethics"),
    ("apa health advisory", "ethics_fn", "ai"),
    ("ethical behavior analysis in the age of ai", "ethics_fn", "ai"),
    ("starting the conversation around the ethical use", "ethics_fn", "ai"),
    ("examination of ethical decision-making models", "ethics_fn", "ethics"),
    ("ethical decision-making and ebps", "ethics_fn", "ethics"),
    ("ethical principles and values guiding modern", "ethics_fn", "ethics"),
    ("practical ethics for effective treatment of autism spectrum", "ethics_fn", "autism"),
    ("research ethics in behavior analysis- from laboratory", "ethics_fn", "ethics"),
    ("research ethics in behavior analysis", "ethics_fn", "ethics"),
    ("creative destruction approach to replication", "ethics_fn", "ethics"),
    ("guide to establishing ethics committees", "ethics_fn", "org"),
    ("proposed process for risk mitigation during the covid", "ethics_fn", "health"),
    ("explicit ethical statements in telehealth", "ethics_fn", "autism"),
    ("ethical considerations in interdisciplinary treatments", "ethics_fn", "autism"),
    ("still lost in translation", "ethics_fn", "autism"),
    ("how to identify ethical practices in organizations", "ethics_fn", "org"),
    ("lost in translation- a reply to shyman", "ethics_fn", "autism"),
    ("from interdisciplinary to integrated care of the child", "ethics_fn", "autism"),
    ("practical ethics for effective treatment of asd (1st", "ethics_fn", "autism"),
    ("practical ethics for effective treatment of asd (2nd", "ethics_fn", "autism"),
    ("predicting changes in substance use following psychedelic", "modeling", "substance"),
    ("kratom", "design", "substance"),
    ("proof of concept demonstration for how to evaluate clinical decision", "modeling", "clinical"),
    ("algorithmic approach to recommending hours", "modeling", "autism"),
    ("delay discounting and teacher decision-making", "beh_econ", "clinical"),
    ("evaluation of statement accuracy on ethical decision-making", "ethics_fn", "ethics"),
    ("influence of televisibility and harm probability", "beh_econ", "clinical"),
    ("toward collapsing the is-ought distinction", "ethics_fn", "ethics"),
    ("challenges ahead- concepts, analytics, and ethics of vbc", "modeling", "org"),
    ("intelligence driven system to predict asd outcomes", "modeling", "autism"),
    ("efficacy of edible and leisure reinforcers with domestic dogs", "reinforcement", "animal"),
    ("discounting under severe weather threat", "beh_econ", "health"),
    ("proof of concept analysis of decision-making with time-series", "modeling", "clinical"),
    ("descriptive and normative ethical behavior appear", "ethics_fn", "ethics"),
    ("scaling n from 1 to 1,000,000", "matching", "ai"),
    ("sexual arousal discounting", "beh_econ", "health"),
    ("sexual discounting- a systematic review", "beh_econ", "health"),
    ("influence of eft and graphic warnign labels", "beh_econ", "substance"),
    ("verbal behavior related to drug reinforcement", "verbal", "substance"),
    ("dd and pd in cud", "beh_econ", "substance"),
    ("any reward will do", "reinforcement", "animal"),
    ("application of the matching law to pitch selection", "matching", "baseball"),
    ("aba for business and technology applications", "reinforcement", "org"),
    ("aba for clinical, educational, and training applications", "reinforcement", "clinical"),
]


def classify(title):
    t = title.lower()
    for sub, f, d in MAP:
        if sub in t:
            return f, d
    return None, None


def main():
    applied = [corpus[i] for i, l in assign.items() if l in APPLIED and i in corpus]
    papers, unmapped = [], []
    edges = {}
    for it in sorted(applied, key=lambda x: -(x["year"] or 0)):
        f, d = classify(it["title"])
        if not f:
            unmapped.append(it["title"][:60]); continue
        papers.append({"id": it["id"], "title": it["title"], "year": it["year"],
                       "doi": it.get("doi"), "fund": f, "domain": d})
        edges.setdefault((f, d), []).append(it["id"])

    out = {
        "fundamentals": [{"id": i, "label": l, "kind": k} for i, l, k in FUNDAMENTALS],
        "domains": [{"id": i, "label": l} for i, l in DOMAINS],
        "papers": papers,
        "edges": [{"fund": f, "domain": d, "papers": p} for (f, d), p in edges.items()],
    }
    (ROOT / "data" / "translation.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    (ROOT / "data" / "translation.js").write_text("window.TRANSLATION = " + json.dumps(out, ensure_ascii=False) + ";\n")
    print(f"papers mapped={len(papers)} unmapped={len(unmapped)} edges={len(edges)}")
    if unmapped:
        print("UNMAPPED:"); [print("  -", u) for u in unmapped]
    print("\ninfluence (fundamental -> # studies applied):")
    inf = Counter(p["fund"] for p in papers)
    fl = dict((i, l) for i, l, k in FUNDAMENTALS)
    for f, n in inf.most_common():
        print(f"  {n:2d}  {fl[f]}")


if __name__ == "__main__":
    main()
