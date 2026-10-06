# casegen

Generates the case-study pages and the landing page.

- `gen.py` — page template and the SVG diagram renderer (node cards, dashed
  containers, numbered arrows). Diagram coordinates are explicit per page.
- `content/*.py` — one dict per case study: copy, spec sheet, diagram,
  ledger, screenshots, failures, source.
- `build_site.py` — the archive order, featured list, experience and
  certifications, then writes every page.
- `thumbs.js` — screenshots each featured page's diagram (Playwright) for
  `assets/thumbs/`; crop/resize to 480×300.

```bash
python3 tools/casegen/build_site.py
```
