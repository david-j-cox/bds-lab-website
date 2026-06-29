#!/usr/bin/env python3
"""Build data/current-projects.js (window.CURRENT_PROJECTS) for the topic map's
in-progress overlay, from ClickUp.

Set CLICKUP_API_TOKEN (env var / repo secret). The script discovers the lists
named in CLICKUP_LISTS (default "Research Projects,Writing") *by name* across the
workspace -- so no list IDs to dig up -- pulls their open tasks, drops obvious
to-do / action items, and tags each project with a research-area cluster id
(inferred from the title) so the map can place it near where it fits.
"""
import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.clickup.com/api/v2/"

# topic-map cluster ids: 0 Translating/non-lab  1 Ethics  2 Basic principles
#   3 Quantitative/computational/statistical methods  4 Clinical decision-making
#   5 Research methodologies  6 Artificial organisms  7 Substance use
# Most specific keywords first.
LINE_TO_CLUSTER = [
    ("brunt", 6), ("vaisala", 6), ("väisälä", 6), ("molecular dynamic", 6), ("artificial organism", 6),
    ("artificial life", 6), ("aos", 6), (" ao ", 6), ("dead man test", 6), ("imitate", 6),
    ("assent", 1), ("undue influence", 1), ("consent", 1), ("equity", 1), ("ethic", 1), ("moral", 1),
    ("medication", 4), ("bpharm", 4), ("dose", 4), ("clinical", 4), ("autism", 4), ("treatment", 4),
    ("sample size", 3), ("feature set", 3), ("algorithm", 3), ("cluster analys", 3), ("multiscale", 3),
    ("embedding", 3), ("machine learning", 3), ("diffusion model", 3), ("nlp", 3), ("llm", 3),
    ("computational", 3), ("analytic", 3), ("quantitative", 3), ("tensor", 3), ("big data", 3),
    ("citation analysis", 3), ("bibliometric", 3), ("financial literacy", 3), ("ai", 3), ("data", 3),
    ("matching", 2), ("momentum", 2), ("discount", 2), ("probabilist", 2), ("reinforcement", 2),
    ("choice", 2), ("preference", 2), ("resurgence", 2), ("reoccurrence", 2), ("operant", 2),
    ("respondent", 2), ("variability", 2), ("contingenc", 2), ("instruction following", 2),
    ("generaliz", 2), ("same processes", 2), ("levels in operant", 2),
    ("measurement", 5), ("design", 5), ("methodolog", 5), ("immersion", 5),
    ("substance", 7), ("drug", 7), ("nicotine", 7),
    ("non-lab", 0), ("translat", 0), ("organization", 0), ("managerial", 0), ("verbal communit", 0),
    ("birding", 0), ("conservation", 0), ("welfare", 0), ("ecology", 0),
]

# Titles that are action items / milestones, not projects.
TASK_RE = re.compile(
    r"^\s*(get|submit|complete|finish|start|revise|respond|reply|send|email|schedule|upload|"
    r"download|check|fix|format|edit|set up|follow up|reach out|write up|read|review|add|update|"
    r"prepare|book|pay|renew|order|print|file|meet|call|ping|draft|outline|plan)\b",
    re.I)
# Milestone / status / file rows that aren't projects.
JUNK_RE = re.compile(
    r"\.(png|jpe?g|gif|pdf|docx?|pptx?|csv|xlsx?|mov|mp4)\s*$"
    r"|\bedits?\s+done\b|\bdraft\s+done\b|\b(proposal\s+)?submitted\s*$"
    r"|^(intro|introduction|methods?|results?|discussion|abstract|references?|conclusion)\b",
    re.I)

# List names to skip even if discovered (safety).
EXCLUDE_TITLE = ["managerial turn"]


def cluster_for(text):
    t = " " + (text or "").lower() + " "
    for kw, cid in LINE_TO_CLUSTER:
        if kw in t:
            return cid
    return 2  # default: basic principles


def api(token, path):
    req = urllib.request.Request(API + path, headers={"Authorization": token})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def discover_lists(token):
    """Map of lowercased list name -> (id, display name) across the workspace."""
    out = {}
    for team in api(token, "team").get("teams", []):
        for space in api(token, f"team/{team['id']}/space?archived=false").get("spaces", []):
            sid = space["id"]
            for l in api(token, f"space/{sid}/list?archived=false").get("lists", []):
                out[l["name"].strip().lower()] = (l["id"], l["name"].strip())
            for f in api(token, f"space/{sid}/folder?archived=false").get("folders", []):
                for l in f.get("lists", []):
                    out[l["name"].strip().lower()] = (l["id"], l["name"].strip())
    return out


def parse_clickup():
    token = os.environ.get("CLICKUP_API_TOKEN")
    if not token:
        print("ClickUp: no token set -> skipping.")
        return []
    names = [n.strip() for n in (os.environ.get("CLICKUP_LISTS") or "Research Projects,Writing").split(",") if n.strip()]
    try:
        catalog = discover_lists(token)
    except Exception as e:
        print(f"ClickUp list discovery failed ({e}).")
        return []
    print("ClickUp lists found:", ", ".join(sorted(v[1] for v in catalog.values()))[:400])
    out = []
    for name in names:
        hit = catalog.get(name.lower())
        if not hit:
            print(f"ClickUp: list '{name}' not found.")
            continue
        lid, lname = hit
        try:
            tasks = api(token, f"list/{lid}/task?include_closed=false&subtasks=false").get("tasks", [])
        except Exception as e:
            print(f"ClickUp: fetch '{name}' failed ({e}).")
            continue
        kept = 0
        for t in tasks:
            if (t.get("status", {}) or {}).get("type", "") in ("closed", "done"):
                continue
            title = (t.get("name") or "").strip()
            if not title or TASK_RE.match(title) or JUNK_RE.search(title):
                continue
            if any(x in title.lower() for x in EXCLUDE_TITLE):
                continue
            out.append({"title": title, "desc": (t.get("description") or "")[:400],
                        "cluster": cluster_for(title),
                        "category": (t.get("status", {}) or {}).get("status", "").title() or "Current",
                        "source": "clickup", "list": lname})
            kept += 1
        print(f"ClickUp '{lname}': kept {kept} of {len(tasks)} open tasks.")
    return out


def existing():
    f = ROOT / "data" / "current-projects.js"
    if not f.exists():
        return []
    txt = f.read_text()
    try:
        return json.loads(txt[txt.index("["):txt.rindex("]") + 1])
    except ValueError:
        return []


def main():
    projects = parse_clickup()
    if not projects and existing():
        print("Built 0 projects; keeping existing file unchanged.")
        return
    seen = {}
    for p in projects:
        if p["title"]:
            seen[p["title"].lower()] = p
    merged = list(seen.values())
    (ROOT / "data" / "current-projects.js").write_text(
        "window.CURRENT_PROJECTS = " + json.dumps(merged, ensure_ascii=False) + ";\n")
    print(f"current projects: {len(merged)}")


if __name__ == "__main__":
    main()
