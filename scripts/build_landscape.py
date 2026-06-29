#!/usr/bin/env python3
"""Build data/landscape.json for the 'Integrating principles' combination matrix.

Axis = a curated ~40 core processes spanning the field's most-studied operant /
respondent processes (catalog-driven) and the lab's decision-making dimensions
(hand-placed). Field co-occurrence comes from the Behavioral Process Catalog;
lab cells are hand-mapped to the lab's combination studies. Both the process
list and the lab mappings are first-draft curation, meant to be corrected.
"""
import json
from pathlib import Path
from collections import Counter
from itertools import combinations

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT.parent / "catalog-of-principles-and-processes" / "data.json"
OUT = ROOT / "data" / "landscape.json"

# Curated axis. group: 'field' = classic operant/respondent (catalog has data);
# 'decision' = the lab's choice/discounting region (catalog under-tags it).
PROCESSES = [
    # --- operant principles / processes (catalog) ---
    ("reinf_pos", "Positive reinforcement", "field"),
    ("reinf_neg", "Negative reinforcement", "field"),
    ("punish_pos", "Positive punishment", "field"),
    ("punish_neg", "Negative punishment", "field"),
    ("extinction", "Extinction", "field"),
    ("stim_control", "Stimulus control", "field"),
    ("discrim", "Discrimination", "field"),
    ("generalization", "Generalization", "field"),
    ("contrast", "Behavioral contrast", "field"),
    ("temporal", "Temporal control", "field"),
    ("cond_reinf", "Conditioned reinforcement", "field"),
    ("avoidance", "Avoidance", "field"),
    ("momentum", "Behavioral momentum", "field"),
    ("matching", "Matching", "field"),
    # --- respondent processes (catalog; replaces the 'respondent' umbrella) ---
    ("autoshaping", "Autoshaping", "field"),
    ("cond_suppression", "Conditioned suppression", "field"),
    ("cond_inhibition", "Conditioned inhibition", "field"),
    ("second_order", "Second-order conditioning", "field"),
    # --- the lab's combination dimensions (catalog under-tags these) ---
    ("delay_disc", "Delay discounting", "lab"),
    ("prob_disc", "Probability discounting", "lab"),
    ("effort", "Effort / response cost", "lab"),
    ("amount", "Reward amount", "lab"),
    ("sign", "Gains vs losses", "lab"),
    ("econ_context", "Economic context / budget", "lab"),
    ("verbal", "Verbal behavior", "lab"),
    ("foraging", "Foraging", "lab"),
]
IDS = [p[0] for p in PROCESSES]

# Map catalog process strings -> canonical id (for field co-occurrence).
# Schedules and resurgence are procedures, not processes, and are excluded.
ALIAS = {
    "reinforcement: positive": "reinf_pos", "positive reinforcement": "reinf_pos",
    "reinforcement: negative": "reinf_neg", "negative reinforcement": "reinf_neg",
    "punishment: positive": "punish_pos", "punishment": "punish_pos",
    "punishment: electric shock": "punish_pos", "punishment: electric shocks": "punish_pos",
    "punishment: negative": "punish_neg",
    "extinction": "extinction",
    "stimulus control": "stim_control",
    "discrimination learning": "discrim", "discrimination training": "discrim",
    "discrimination": "discrim", "temporal discrimination": "discrim",
    "stimulus generalization": "generalization", "generalization": "generalization",
    "generalization gradient": "generalization",
    "behavioral contrast": "contrast",
    "temporal control": "temporal", "temporal relations": "temporal",
    "conditioned reinforcement": "cond_reinf", "conditioned reinforcer": "cond_reinf",
    "avoidance": "avoidance",
    "behavior momentum": "momentum", "behavioral momentum": "momentum",
    "matching": "matching", "matching law": "matching", "undermatching": "matching",
    "generalized matching law": "matching",
    "autoshaping": "autoshaping",
    "conditioned suppression": "cond_suppression",
    "conditioned inhibition": "cond_inhibition",
    "second-order conditioning": "second_order",
    "response effort": "effort", "foraging": "foraging",
}

# Lab combination studies -> process pairs (hand-mapped; correct as needed).
LAB = [
    (["delay_disc", "prob_disc"], "Effects of delay and probability combinations on discounting (Cox & Dallery, 2016)", "10.1016/j.beproc.2016.08.002"),
    (["delay_disc", "prob_disc"], "Further comparison of 5-trial adjusting delay and probability tasks (Miranda et al., 2018)", "10.1016/beproc.2018.08.004"),
    (["effort", "prob_disc"], "Combined effects of effort and probability on monetary discounting (Drugan-Eppich & Cox, 2026)", "10.1002/jeab.70118"),
    (["delay_disc", "prob_disc"], "Influence of second outcome on monetary discounting (Cox & Dallery, 2018)", "10.1016/j.beproc.2018.05.012"),
    (["delay_disc", "sign"], "Influence of second outcome on monetary discounting (Cox & Dallery, 2018)", "10.1016/j.beproc.2018.05.012"),
    (["prob_disc", "sign"], "Influence of second outcome on monetary discounting (Cox & Dallery, 2018)", "10.1016/j.beproc.2018.05.012"),
    (["delay_disc", "sign"], "Multiplicative vs additive hyperbolic discounting, gains and losses (Bialaszek et al., 2020)", "10.1371/journal.pone.0233337"),
    (["prob_disc", "sign"], "Multiplicative vs additive hyperbolic discounting, gains and losses (Bialaszek et al., 2020)", "10.1371/journal.pone.0233337"),
    (["econ_context", "delay_disc"], "Economic context and reward amount on delay and probability discounting (Anderson et al., 2023)", "10.1002/jeab.868"),
    (["econ_context", "prob_disc"], "Economic context and reward amount on delay and probability discounting (Anderson et al., 2023)", "10.1002/jeab.868"),
    (["amount", "delay_disc"], "Economic context and reward amount on delay and probability discounting (Anderson et al., 2023)", "10.1002/jeab.868"),
    (["verbal", "prob_disc"], "Verbal behavior and risky choice in humans (Cox & Dallery, 2018)", "10.1016/j.beproc.2018.09.002"),
    (["econ_context", "prob_disc"], "Predicting choice under positive and negative earning budgets (Cox, preprint)", "10.13140/RG.2.2.36414.86086"),
]


def short_authors(authors):
    last = [a.split(",")[0].strip() for a in (authors or []) if a.strip()]
    if not last:
        return ""
    if len(last) == 1:
        return last[0]
    if len(last) == 2:
        return f"{last[0]} & {last[1]}"
    return f"{last[0]} et al."


def main():
    catalog = json.loads(CATALOG.read_text())
    from collections import defaultdict
    articles, art_index = [], {}
    field_refs = defaultdict(list)
    for e in catalog:
        ids = set()
        for p in (e.get("process") or []):
            cid = ALIAS.get((p or "").strip().lower())
            if cid in IDS:
                ids.add(cid)
        if len(ids) < 2:
            continue
        k = e.get("url") or (e.get("title", ""), e.get("year"))
        if k not in art_index:
            art_index[k] = len(articles)
            articles.append({
                "t": (e.get("title") or "")[:160],
                "a": short_authors(e.get("authors")),
                "y": e.get("year"),
                "u": e.get("url") or "",
            })
        ai = art_index[k]
        for a, b in combinations(sorted(ids), 2):
            field_refs[(a, b)].append(ai)

    def key(a, b):
        return tuple(sorted((a, b)))

    lab = {}
    for procs, study, doi in LAB:
        for a, b in combinations(sorted(set(procs)), 2):
            lab.setdefault(key(a, b), []).append({"study": study, "doi": doi})

    out = {
        "processes": [{"id": i, "label": l, "group": g} for i, l, g in PROCESSES],
        "articles": articles,
        "field": [{"a": a, "b": b, "n": len(r), "refs": r} for (a, b), r in field_refs.items()],
        "lab": [{"a": a, "b": b, "studies": s} for (a, b), s in lab.items()],
    }
    OUT.write_text(json.dumps(out))
    print(f"processes={len(PROCESSES)} articles={len(articles)} "
          f"field-pairs={len(out['field'])} lab-pairs={len(out['lab'])}")
    (ROOT / "data" / "landscape.js").write_text("window.LANDSCAPE = " + json.dumps(out) + ";\n")


if __name__ == "__main__":
    main()
