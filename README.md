# kingswanzy2020.github.io

Ahmed Tetteh's portfolio: a landing page and 29 case studies, one per project.
Static HTML and CSS — no JavaScript, no framework, nothing to build at serve time.

- `index.html` — landing page: intro, experience, selected work, the full
  case-study archive, certifications (with Credly verification links) and contact.
- `assets/site.css` — the one stylesheet every page uses (dark navy / teal).
  Diagram colours are the `--c-*` and `--dg-*` tokens at the top.
- `assets/img/ahmed.jpg` — profile photo used by the avatar on every page.
  Until it exists, the avatar shows the initials "AT".
- `assets/thumbs/` — diagram thumbnails for the "Selected work" list.
- `<slug>/index.html` — one case study per directory. Each has the same
  sections: spec sheet, numbered architecture diagram, wiring table and legend,
  a measured / observed / by-design ledger, proof screenshots, what broke, and
  the source repo. Images extracted from my NextWork write-ups live in
  `<slug>/img/`; everything else is loaded from the
  [Projects](https://github.com/kingswanzy2020/Projects) repo.
- `tools/casegen/` — the generator for the case studies added in October 2026
  and for the landing page. Content is data in `content/*.py`; run
  `python3 tools/casegen/build_site.py` to rebuild. It also restyles the five
  original hand-built pages (`eks`, `terraform-gitops`, `argocd-pipeline`,
  `fastapi-react`, `delivery-scoreboard`) and adds previous/next links to all.
- `add-real-icons.sh` — swaps a page's placeholder diagram glyphs for real
  vendor logos once they're in `assets/icons/` (see the script's header).
- `.github/workflows/deploy.yml` — deploys on every push to `main` via
  GitHub Pages (Actions source).

Live at: https://kingswanzy2020.github.io/
