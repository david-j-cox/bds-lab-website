#!/usr/bin/env python3
"""Term vocabulary for detecting behavioral processes in article text.

Used by build_landscape.py to place both the field's literature and the lab's
own work on the combination matrix. Detection is deterministic phrase matching
over title + abstract: no embeddings, no API, no build dependency.

Curation rules that keep precision usable:
  - Prefer multi-word technical phrases over bare nouns. "avoidance" alone
    catches ordinary English; "avoidance responding" does not.
  - A phrase belongs to exactly one process. Where a term is genuinely
    ambiguous across two processes (the classic case is "response cost", which
    means lost reinforcers in applied work and physical effort in basic work),
    it is assigned to its dominant sense and the other process gets narrower
    terms. Otherwise every such article manufactures a false co-occurrence.
  - Procedures are not processes. Schedules of reinforcement, differential
    reinforcement, single-subject designs, and assessment methods are absent.
  - A few phrases carry a second, non-behavioral meaning in this literature:
    "resistance to change" in organizational writing, "time-out" as a computer
    or sports term, "income level" as a demographic. Those are listed as gated
    terms and only count when the text also carries a behavioral anchor.
"""
import re

# process id -> (display label, group, [phrases])
# group: 'field' = classic operant/respondent, 'lab' = the lab's choice region.
PROCESSES = [
    ("reinf_pos", "Positive reinforcement", "field", [
        r"positive reinforcement", r"food reinforc\w*", r"appetitive reinforc\w*",
    ]),
    ("reinf_neg", "Negative reinforcement", "field", [
        r"negative reinforcement", r"escape (?:contingenc\w*|responding|behavior)",
        r"escape[- ]maintained",
    ]),
    ("punish_pos", "Positive punishment", "field", [
        r"positive punishment", r"punish\w* .{0,25}shock", r"shock .{0,20}punish\w*",
        r"contingent (?:shock|stimulation)", r"aversive stimulation",
    ]),
    ("punish_neg", "Negative punishment", "field", [
        r"negative punishment", r"response cost",
        r"loss of (?:tokens|points|reinforcers)",
    ], [r"\btime[- ]?out\b"]),
    ("extinction", "Extinction", "field", [
        r"\bextinction\b", r"extinction burst", r"\bresurgence\b",
        r"spontaneous recovery", r"\brenewal effect",
    ]),
    ("stim_control", "Stimulus control", "field", [
        r"stimulus control", r"discriminative stimul\w*", r"\bstimulus class\w*",
    ]),
    ("discrim", "Discrimination", "field", [
        r"discrimination (?:learning|training|task|performance)",
        r"conditional discrimination", r"matching[- ]to[- ]sample",
        r"successive discrimination", r"simultaneous discrimination",
    ]),
    ("generalization", "Generalization", "field", [
        r"stimulus generalization", r"generalization gradient",
        r"response generalization", r"generaliz\w* across (?:settings|stimuli|responses)",
    ]),
    ("contrast", "Behavioral contrast", "field", [
        r"behavio(?:u)?ral contrast", r"\bpositive contrast\b", r"\bnegative contrast\b",
    ]),
    ("temporal", "Temporal control", "field", [
        r"temporal control", r"peak (?:procedure|interval)", r"interval timing",
        r"timing behavio\w*", r"temporal bisection", r"temporal discrimination",
    ]),
    ("cond_reinf", "Conditioned reinforcement", "field", [
        r"conditioned reinforc\w*", r"secondary reinforc\w*", r"token reinforc\w*",
        r"token econom\w*",
    ]),
    ("avoidance", "Avoidance", "field", [
        r"avoidance (?:responding|behavio\w*|learning|task|contingenc\w*|schedule)",
        r"(?:sidman|free[- ]operant|signalled|signaled) avoidance",
        r"\bescape and avoidance", r"shock avoidance",
    ]),
    ("momentum", "Behavioral momentum", "field", [
        r"behavio(?:u)?ral momentum", r"\bresponse strength\b",
    ], [r"resistance to change"]),
    ("matching", "Matching", "field", [
        r"matching law", r"generalized matching", r"\bmelioration\b",
        r"\bundermatching\b", r"\bovermatching\b", r"concurrent schedul\w*",
        r"relative response rate",
    ]),
    ("autoshaping", "Autoshaping", "field", [
        r"autoshap\w*", r"sign[- ]tracking", r"goal[- ]tracking", r"\bomission (?:training|procedure)",
    ]),
    ("cond_suppression", "Conditioned suppression", "field", [
        r"conditioned suppression", r"suppression ratio", r"conditioned emotional response",
    ]),
    ("cond_inhibition", "Conditioned inhibition", "field", [
        r"conditioned inhibit\w*", r"summation test", r"retardation test",
        r"\binhibitory (?:conditioning|stimulus)",
    ]),
    ("second_order", "Second-order conditioning", "field", [
        r"second[- ]order conditioning", r"higher[- ]order conditioning",
        r"sensory preconditioning",
    ]),
    ("delay_disc", "Delay discounting", "lab", [
        r"delay discount\w*", r"temporal discount\w*", r"impulsive choice",
        r"delay,? (?:and|or|&) probability discount\w*",
        r"self[- ]control (?:choice|paradigm)", r"delay of (?:gratification|reinforcement)",
        r"hyperbolic discount\w*",
    ]),
    ("prob_disc", "Probability discounting", "lab", [
        r"probability discount\w*", r"probabilistic discount\w*", r"risky choice",
        r"risk[- ]sensitiv\w*", r"\bodds against\b",
    ]),
    ("effort", "Effort / response cost", "lab", [
        r"response effort", r"effort discount\w*", r"force requirement",
        r"physical effort", r"\beffort[- ]based (?:choice|decision)",
    ]),
    ("amount", "Reward amount", "lab", [
        r"rein(?:forcer|forcement) (?:magnitude|amount)",
        r"reward (?:magnitude|amount|size)", r"magnitude of rein(?:forcer|forcement)",
    ]),
    ("sign", "Gains vs losses", "lab", [
        r"gains? (?:and|versus|vs\.?) losses", r"loss aversion",
        r"monetary (?:loss|losses)", r"\bsign effect\b",
    ]),
    ("econ_context", "Economic context / budget", "lab", [
        r"behavio(?:u)?ral economic\w*", r"budget constraint", r"earnings budget",
        r"demand curve", r"\bunit price\b", r"reinforcer patholog\w*",
    ], [r"income (?:level|effect|constraint)"]),
    ("verbal", "Verbal behavior", "lab", [
        r"verbal behavio\w*", r"rule[- ]governed", r"instructional control",
        r"relational frame", r"derived relation\w*", r"stimulus equivalence",
    ]),
    ("foraging", "Foraging", "lab", [
        r"\bforaging\b", r"patch (?:leaving|residence|departure)",
        r"optimal foraging", r"prey (?:choice|selection)", r"\bgiving[- ]up time",
    ]),
]

# Entries are (id, label, group, strong_terms[, gated_terms]).
PROCESSES = [tuple(p) + ([],) if len(p) == 4 else tuple(p) for p in PROCESSES]

# Evidence that the surrounding text really is behavior-analytic. Only consulted
# for gated terms, so it never narrows an unambiguous match.
ANCHOR = re.compile(
    r"reinforc\w*|operant|contingenc\w*|schedule of|responding|behavio(?:u)?r analy\w*|"
    r"discriminative|\bpigeons?\b|\brats?\b|extinction",
    re.I,
)

STRONG = {p[0]: re.compile("|".join(p[3]), re.I) for p in PROCESSES}
GATED = {p[0]: re.compile("|".join(p[4]), re.I) for p in PROCESSES if p[4]}
IDS = [p[0] for p in PROCESSES]
LABELS = {p[0]: p[1] for p in PROCESSES}
GROUPS = {p[0]: p[2] for p in PROCESSES}


def detect(text):
    """Return the set of process ids whose vocabulary appears in text."""
    if not text or len(text) < 30:
        return set()
    found = {pid for pid, pat in STRONG.items() if pat.search(text)}
    pending = {pid for pid, pat in GATED.items() if pid not in found and pat.search(text)}
    if pending and ANCHOR.search(text):
        found |= pending
    return found
