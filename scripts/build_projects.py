#!/usr/bin/env python3
"""Build data/current-projects.js (window.CURRENT_PROJECTS) for the topic map's
in-progress overlay.

Sources, merged:
  1. Local projects parsed from projects.html (always).
  2. ClickUp tasks (optional): if CLICKUP_API_TOKEN and CLICKUP_LIST_ID are set in
     the environment, pull open tasks from that List and append them. The token is
     read from the environment and never written to disk.

Each project is tagged with a cluster id (the topic-map's research-area clusters)
so the map can place it near where it fits.
"""
import json
import os
import re
import html
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# topic-map cluster ids (data/corpus.json meta.clusters):
#   0 Translating to non-lab  1 Ethics  2 Basic principles & interactions
#   3 Quantitative/computational/statistical methods  4 Clinical decision-making
#   5 Research methodologies  6 Artificial organisms  7 Substance use
# Local project title keyword -> cluster id.
LOCAL_CLUSTER = [
    ("vector embeddings", 3),
    ("complex multiple control", 2),
    ("quantitative analyses of the multiple control", 3),
    ("creating artificial organisms", 6),
    ("temporally extended behavioral repertoires", 2),
    ("behavioral economics to describe and predict ethical", 1),
    ("quantitative models in non-laboratory", 0),
    ("behavioral reoccurrence", 2),
    ("clinical-ethical decision-making", 4),
    ("doing more with the data", 3),
    ("ai literacy", 3),
]
# Map a free-text "research line" (e.g., a ClickUp field) to a cluster id.
LINE_TO_CLUSTER = {
    "translating": 0, "non-laboratory": 0, "applied": 0,
    "ethics": 1, "ethical": 1,
    "basic": 2, "principles": 2, "interaction": 2, "choice": 2,
    "quantitative": 3, "computational": 3, "statistic": 3, "methods": 3, "machine learning": 3, "ai": 3, "data": 3,
    "clinical": 4,
    "methodolog": 5, "measurement": 5, "design": 5,
    "artificial organism": 6, "ao": 6,
    "substance": 7,
}


def cluster_for_line(text):
    t = (text or "").lower()
    for k, cid in LINE_TO_CLUSTER.items():
        if k in t:
            return cid
    return 2  # default: basic principles


def parse_local():
    h = (ROOT / "projects.html").read_text(encoding="utf-8")
    out = []
    cat = None
    # walk categories and items in document order
    for m in re.finditer(r'category-title[^>]*>(.*?)</|project-title[^>]*>(.*?)</[^>]*>.*?project-description[^>]*>(.*?)</p>', h, re.S):
        if m.group(1) is not None:
            cat = re.sub("<[^>]+>", "", m.group(1)).strip().title()
            continue
        title = html.unescape(re.sub(r"\s+", " ", re.sub("<[^>]+>", "", m.group(2)))).strip()
        desc = html.unescape(re.sub(r"\s+", " ", re.sub("<[^>]+>", "", m.group(3)))).strip()
        cid = next((c for kw, c in LOCAL_CLUSTER if kw in title.lower()), 2)
        out.append({"title": title, "desc": desc, "cluster": cid, "category": cat or "", "source": "local"})
    return out


def parse_clickup():
    token = os.environ.get("CLICKUP_API_TOKEN")
    list_id = os.environ.get("CLICKUP_LIST_ID")
    if not (token and list_id):
        return []
    url = f"https://api.clickup.com/api/v2/list/{list_id}/task?include_closed=false&subtasks=false"
    req = urllib.request.Request(url, headers={"Authorization": token})
    data = json.loads(urllib.request.urlopen(req, timeout=30).read())
    out = []
    line_field = os.environ.get("CLICKUP_LINE_FIELD", "research line").lower()
    for task in data.get("tasks", []):
        status = (task.get("status", {}) or {}).get("type", "")
        if status == "closed" or status == "done":
            continue
        line = ""
        for cf in task.get("custom_fields", []):
            if line_field in (cf.get("name", "") or "").lower():
                v = cf.get("value")
                # dropdown values come back as an index into type_config.options
                if isinstance(v, int):
                    opts = (cf.get("type_config", {}) or {}).get("options", [])
                    line = next((o.get("name", "") for o in opts if o.get("orderindex") == v or o.get("id") == v), "")
                else:
                    line = str(v or "")
        if not line:
            line = " ".join(t.get("name", "") for t in task.get("tags", []))
        out.append({
            "title": task.get("name", "").strip(),
            "desc": (task.get("description") or task.get("text_content") or "").strip()[:400],
            "cluster": cluster_for_line(line or task.get("name", "")),
            "category": (task.get("status", {}) or {}).get("status", "").title(),
            "source": "clickup",
        })
    return out


def main():
    projects = parse_local() + parse_clickup()
    # de-dupe by lowercased title (ClickUp wins if titles collide)
    seen, merged = {}, []
    for p in projects:
        seen[p["title"].lower()] = p
    merged = list(seen.values())
    js = "window.CURRENT_PROJECTS = " + json.dumps(merged, ensure_ascii=False) + ";\n"
    (ROOT / "data" / "current-projects.js").write_text(js)
    n_cu = sum(1 for p in merged if p["source"] == "clickup")
    print(f"current projects: {len(merged)} (local {len(merged) - n_cu}, clickup {n_cu})")


if __name__ == "__main__":
    main()
