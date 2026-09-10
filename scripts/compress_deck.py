#!/usr/bin/env python3
"""Shrink a self-contained deck by re-encoding its embedded images to WebP.

The AO lab update is a single portable HTML file that gets shared as a file, so
the images stay inline as data URIs rather than being extracted to a folder.
Only their encoding changes: PNG and JPEG go through cwebp, animated GIF through
gif2webp, and anything that fails to get smaller is left exactly as it was.

    python3 scripts/compress_deck.py ao-lab-update.html

Writes in place after copying the source to <name>.orig.html, or pass -o to
write elsewhere and leave the input untouched. Requires cwebp and gif2webp
(brew install webp).
"""
import argparse
import base64
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

URI = re.compile(r"data:image/(png|jpeg|jpg|gif);base64,([A-Za-z0-9+/=]+)")
QUALITY = 82
MAX_DIM = 1600  # deck slides never render wider than this


def have(tool):
    return shutil.which(tool) is not None


def to_webp(kind, raw, tmp):
    """Return WebP bytes, or None if conversion failed or did not help."""
    src = tmp / f"in.{kind}"
    dst = tmp / "out.webp"
    src.write_bytes(raw)
    if dst.exists():
        dst.unlink()
    if kind == "gif":
        cmd = ["gif2webp", "-q", str(QUALITY), "-quiet", str(src), "-o", str(dst)]
    else:
        cmd = ["cwebp", "-q", str(QUALITY), "-quiet",
               "-resize", str(MAX_DIM), "0", str(src), "-o", str(dst)]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    if not dst.exists():
        return None
    out = dst.read_bytes()
    return out if 0 < len(out) < len(raw) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("-o", "--out", type=Path, help="write here instead of in place")
    args = ap.parse_args()

    for tool in ("cwebp", "gif2webp"):
        if not have(tool):
            sys.exit(f"{tool} not found; brew install webp")

    html = args.path.read_text(encoding="utf8", errors="replace")
    matches = list(URI.finditer(html))
    print(f"{args.path.name}: {len(html)/1e6:.1f} MB, {len(matches)} embedded images")

    out_parts, cursor = [], 0
    saved = converted = skipped = 0
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for i, m in enumerate(matches, 1):
            kind, b64 = m.group(1), m.group(2)
            raw = base64.b64decode(b64)
            webp = to_webp("gif" if kind == "gif" else "png", raw, tmp)
            out_parts.append(html[cursor:m.start()])
            if webp is None:
                out_parts.append(m.group(0))
                skipped += 1
            else:
                enc = base64.b64encode(webp).decode("ascii")
                out_parts.append("data:image/webp;base64," + enc)
                saved += len(raw) - len(webp)
                converted += 1
            cursor = m.end()
            if i % 25 == 0:
                print(f"  {i}/{len(matches)} ...")
        out_parts.append(html[cursor:])

    result = "".join(out_parts)
    dest = args.out
    if dest is None:
        backup = args.path.with_suffix(".orig.html")
        if not backup.exists():
            shutil.copy2(args.path, backup)
            print(f"  original copied to {backup.name}")
        dest = args.path
    dest.write_text(result, encoding="utf8")
    print(f"converted={converted} left-as-is={skipped} image bytes saved={saved/1e6:.1f} MB")
    print(f"{dest.name}: {len(html)/1e6:.1f} MB -> {len(result)/1e6:.1f} MB "
          f"({100 - len(result)*100//len(html)}% smaller)")


if __name__ == "__main__":
    main()
