# Email signature books banner

Builds the "Selected Books" banner used in the Gmail signature. The banner is
hosted on the website and referenced by URL, so the signature HTML stays tiny
and the image updates everywhere the moment a new render is pushed.

## Files

- `banner.html` - the editable banner layout (title, covers, call-to-action).
- `covers/` - the book cover images. Covers 1-5 are the publisher covers; cover
  6 is generated from `cover-math-modeling.html`.
- `cover-math-modeling.html` - the custom cover for the Mathematical Modeling
  book (no publisher cover yet). Edit here to restyle it.
- `render.sh` - renders the custom cover, then `banner.html` to
  `images/email-signature-books.png`, both at 2x.
- `signature.html` - the full Gmail signature that references the hosted banner.

## Update the banner

1. Edit `banner.html` (add a cover to `covers/` and a matching `<img>`, or
   change the text). If you change the banner's width/height in the CSS, update
   the matching `--window-size` in `render.sh`.
2. Re-render:

   ```
   bash scripts/email-signature/render.sh
   ```

3. Commit and push. The live URL is:
   https://www.behavioral-data-science.org/images/email-signature-books.png

## Update the Gmail signature

Open `signature.html` in a browser, copy the rendered result, and paste it into
Gmail > Settings > See all settings > Signature. The banner image loads from the
website, so you only need to do this once; future banner changes appear
automatically.
