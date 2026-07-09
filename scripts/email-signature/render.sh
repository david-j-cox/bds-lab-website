#!/usr/bin/env bash
# Render the custom book cover and the books banner.
#   - cover-math-modeling.html -> covers/6-math-modeling.jpg (331x500 @ 2x)
#   - banner.html              -> images/email-signature-books.png (1462x268 @ 2x)
# Usage: bash scripts/email-signature/render.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
BANNER_OUT="$REPO/images/email-signature-books.png"
COVER_PNG="$HERE/covers/6-math-modeling.png"
COVER_JPG="$HERE/covers/6-math-modeling.jpg"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

render() { # html_path  w  h  out_png
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=2 \
    --window-size="$2","$3" \
    --default-background-color=00000000 \
    --screenshot="$4" \
    "file://$1" >/dev/null 2>&1
}

# 1) Custom Mathematical Modeling cover (matches publisher covers' 331x500 ratio).
render "$HERE/cover-math-modeling.html" 331 500 "$COVER_PNG"
sips -s format jpeg "$COVER_PNG" --out "$COVER_JPG" >/dev/null 2>&1
rm -f "$COVER_PNG"

# 2) Banner. If you change banner.html's width/height, update these numbers.
render "$HERE/banner.html" 1462 268 "$BANNER_OUT"

echo "Wrote $COVER_JPG"
echo "Wrote $BANNER_OUT"
sips -g pixelWidth -g pixelHeight "$BANNER_OUT" | grep pixel
