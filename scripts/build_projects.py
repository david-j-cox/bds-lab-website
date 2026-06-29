#!/usr/bin/env python3
"""Build data/current-projects.js (window.CURRENT_PROJECTS) for the topic map's
in-progress overlay. These are ACTUAL discrete projects, not broad themes.

Sources, merged:
  1. Local "papers in review" -- folders in ~/Dropbox/Projects/Manuscripts Under
     Review/ (only when that folder is present, i.e. run on Dave's machine).
     Committed into the data file so they persist when the weekly cloud job runs.
  2. ClickUp tasks (optional): if CLICKUP_API_TOKEN and CLICKUP_LIST_ID are set,
     pull open tasks from that List. The token is read from env, never stored.

Each project gets a cluster id (the topic-map research-area clusters) so the map
can place it near where it fits.
"""
import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW_DIR = Path.home() / "Dropbox" / "Projects" / "Manuscripts Under Review"

# topic-map cluster ids: 0 Translating/non-lab  1 Ethics  2 Basic principles
#   3 Quantitative/computational/statistical methods  4 Clinical decision-making
#   5 Research methodologies  6 Artificial organisms  7 Substance use
# Most specific keywords first.
LINE_TO_CLUSTER = [
    ("brunt", 6), ("vaisala", 6), ("väisälä", 6), ("molecular", 6), ("artificial organism", 6), (" ao", 6), ("artificial life", 6),
    ("assent", 1), ("undue influence", 1), ("consent", 1), ("ethic", 1),
    ("medication", 4), ("bpharm", 4), ("dose", 4), ("clinical", 4),
    ("sample size", 3), ("feature set", 3), ("algorithm", 3), ("cluster analys", 3), ("multiscale", 3),
    ("embedding", 3), ("machine learning", 3), ("nlp", 3), ("llm", 3), ("computational", 3), ("analytic", 3), ("quantitative", 3), ("tensor", 3), ("ai", 3), ("data", 3),
    ("matching", 2), ("momentum", 2), ("discount", 2), ("probabilist", 2), ("choice", 2), ("resurgence", 2), ("reoccurrence", 2), ("operant", 2), ("respondent", 2), ("variability", 2), ("contingenc", 2), ("instruction following", 2),
    ("measurement", 5), ("design", 5), ("methodolog", 5),
    ("substance", 7), ("drug", 7),
    ("non-lab", 0), ("translat", 0), ("organization", 0), ("managerial", 0),
]

ACRONYMS = {"ai": "AI", "ba": "BA", "bpharm": "BPharm", "mlm": "MLM", "nlp": "NLP",
            "llm": "LLM", "llms": "LLMs", "mpr": "MPR", "ao": "AO", "aos": "AOs", "aba": "ABA", "ml": "ML"}


def cluster_for(text):
    t = (text or "").lower()
    for kw, cid in LINE_TO_CLUSTER:
        if kw in t:
            return cid
    return 2  # default: basic principles


def clean_title(name):
    s = re.sub(r"[-_]", " ", name)
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)        # camelCase
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", s)   # ACRConvo -> ACR Convo
    s = re.sub(r"\s+", " ", s).strip()
    if name.replace("-", "").replace("_", "").islower():
        s = " ".join(ACRONYMS.get(w.lower(), w.capitalize()) for w in s.split())
    s = s.replace("B Pharm", "BPharm").replace("Brunt Väisälä", "Brunt-Väisälä")
    return s


# Local folders to keep off the map (title substrings, lowercase).
EXCLUDE_TITLE = ["managerial turn"]


def scan_review():
    """Local papers in review; None if the Dropbox folder isn't here (cloud run)."""
    if not REVIEW_DIR.exists():
        return None
    out = []
    for d in sorted(REVIEW_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name.startswith("__archived") or d.name.lower().startswith("shelved"):
            continue
        title = clean_title(d.name)
        if any(x in title.lower() for x in EXCLUDE_TITLE):
            continue
        out.append({"title": title, "desc": "", "cluster": cluster_for(title),
                    "category": "Under review", "source": "local"})
    return out


def existing_local():
    """Keep previously-committed local projects when the folder isn't reachable."""
    f = ROOT / "data" / "current-projects.js"
    if not f.exists():
        return []
    txt = f.read_text()
    try:
        data = json.loads(txt[txt.index("["):txt.rindex("]") + 1])
    except ValueError:
        return []
    return [p for p in data if p.get("source") == "local"]


def parse_clickup():
    token, list_id = os.environ.get("CLICKUP_API_TOKEN"), os.environ.get("CLICKUP_LIST_ID")
    if not (token and list_id):
        print(f"ClickUp: token set={bool(token)}, list_id set={bool(list_id)} -> skipping ClickUp pull.")
        return []
    url = f"https://api.clickup.com/api/v2/list/{list_id}/task?include_closed=false&subtasks=false"
    req = urllib.request.Request(url, headers={"Authorization": token})
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=30).read())
    except Exception as e:
        print(f"ClickUp fetch failed ({e}); keeping local projects only.")
        return []
    line_field = os.environ.get("CLICKUP_LINE_FIELD", "research line").lower()
    out = []
    for task in data.get("tasks", []):
        if (task.get("status", {}) or {}).get("type", "") in ("closed", "done"):
            continue
        line = ""
        for cf in task.get("custom_fields", []):
            if line_field in (cf.get("name", "") or "").lower():
                v = cf.get("value")
                if isinstance(v, int):
                    opts = (cf.get("type_config", {}) or {}).get("options", [])
                    line = next((o.get("name", "") for o in opts if o.get("orderindex") == v or o.get("id") == v), "")
                else:
                    line = str(v or "")
        if not line:
            line = " ".join(t.get("name", "") for t in task.get("tags", []))
        out.append({"title": task.get("name", "").strip(),
                    "desc": (task.get("description") or task.get("text_content") or "").strip()[:400],
                    "cluster": cluster_for(line or task.get("name", "")),
                    "category": (task.get("status", {}) or {}).get("status", "").title(),
                    "source": "clickup"})
    return out


def main():
    local = scan_review()
    if local is None:
        local = existing_local()
    projects = local + parse_clickup()
    seen = {}
    for p in projects:
        if p["title"]:
            seen[p["title"].lower()] = p
    merged = list(seen.values())
    (ROOT / "data" / "current-projects.js").write_text(
        "window.CURRENT_PROJECTS = " + json.dumps(merged, ensure_ascii=False) + ";\n")
    n_cu = sum(1 for p in merged if p["source"] == "clickup")
    print(f"current projects: {len(merged)} (local {len(merged) - n_cu}, clickup {n_cu})")


if __name__ == "__main__":
    main()
