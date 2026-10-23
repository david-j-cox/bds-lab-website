#!/usr/bin/env python3
"""Build a "literary" PDF (Georgia, running heads, small-caps opener) of an
essay from its Word manuscript, for self-hosted pieces such as the Operants
essays in documents/.

    python3 scripts/literary/make_literary.py scripts/literary/pieces/<piece>.json [--out PATH]

Each piece's JSON names the source .docx, the output PDF, how many leading
paragraphs to drop (title block, byline, epigraph), the opener and epigraph
markup, the words set in small caps at the start, and the colophon notice.
The manuscript's conventions: a paragraph that is all bold is a section head,
an all-italic paragraph is a centered refrain, "**References**" starts the
sources, and an "[Author Note]: ..." paragraph goes to the colophon.

Needs pandoc and Google Chrome (headless print to PDF).
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def html(md):
    out = subprocess.run(["pandoc", "-f", "markdown", "-t", "html"], input=md,
                         capture_output=True, text=True, check=True).stdout.strip()
    return re.sub(r"^<p>|</p>$", "", out)


def build(cfg):
    md = subprocess.run(["pandoc", str(Path(cfg["source"]).expanduser()), "-t", "markdown", "--wrap=none"],
                        capture_output=True, text=True, check=True).stdout
    paras = [p.strip() for p in md.split("\n\n") if p.strip()][cfg["skip"]:]
    body, refs, note, in_refs = [], [], None, False
    for p in paras:
        if p.startswith("**References**"):
            in_refs = True
            continue
        if p.startswith("[Author Note]"):
            note = p.split(":", 1)[1].strip()
            continue
        if in_refs:
            refs.append(html(p))
            continue
        m = re.fullmatch(r"\*\*(.+)\*\*", p)
        if m:
            body.append(f"<h2>{html(m.group(1))}</h2>")
            continue
        if re.fullmatch(r"\*[^*]+\*\.?", p):
            body.append(f'<p class="refrain">{html(p.rstrip("."))}</p>')
            continue
        body.append(f"<p>{html(p)}</p>")
    lead = cfg["lead"]
    if not body[0].startswith(f"<p>{lead}"):
        sys.exit(f"first paragraph does not start with {lead!r}; check 'skip' and 'lead': {body[0][:120]}")
    body[0] = body[0].replace(f"<p>{lead}", f'<p class="first"><span class="lead">{lead}</span>', 1)
    back = ""
    if refs:
        back += '<h2>Notes and Sources</h2><div class="src">' + "".join(f"<p>{r}</p>" for r in refs) + "</div>"
    back += ('<h2>About This Version</h2><div class="colophon">' + f"<p>{cfg['notice']}</p>"
             + (f"<p>{note}</p>" if note else "")
             + "<p>David J. Cox, Ph.D., M.S.B., BCBA-D. Endicott College; Mosaic Pediatric Therapy.</p></div>")
    css = (HERE / "lit.css").read_text().replace("var(--short)", f'"{cfg["short"]}"')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{cfg["title"]}</title><style>{css}</style></head><body>
<div class="opener">{cfg["opener"]}<div class="rule"></div><div class="by">David J. Cox</div></div>
{cfg.get("epigraph", "")}<div class="text">{"".join(body)}</div>
<div class="coda">* * *</div>
<div class="back">{back}</div>
</body></html>'''


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cfg = json.loads(Path(args[0]).read_text())
    out = Path(args[args.index("--out") + 1]) if "--out" in args else ROOT / cfg["out"]
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "piece.html"
        page.write_text(build(cfg))
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={out}", page.as_uri()], capture_output=True, check=True)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
