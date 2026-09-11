# Prompt: add another case study

Paste this into a new session when you want to add another project to the
site, filling in the placeholders first.

---

Add another case study to my GitHub Pages site (`~/kahmedt-site/site-deploy`,
deploys to `kingswanzy2020.github.io`). The project is `<PROJECT-SLUG>` — it
already exists in my GitHub account:
- Write-up: `kingswanzy2020/Projects` at `<CATEGORY>/<PROJECT-SLUG>/README.md`
- Source code: `kingswanzy2020/<SOURCE-REPO>` (branch: `<main or other — specify if not main>`)

Steps:

1. **Gather source material.** Fetch the write-up README from the Projects
   repo path above, and the source repo's own README too (it often has extra
   detail the write-up doesn't). Note any mermaid diagram in the write-up —
   that's the basis for the architecture diagram.
2. **Determine status honestly.** Is this live, decommissioned, or something
   else (e.g. a local script that was never a hosted service)? Take this only
   from what the READMEs actually say. If neither README states it, ask —
   don't assume "decommissioned" just because other case studies are.
3. **Check for proof images.** Look for a `Screenshots/` folder alongside the
   write-up in the Projects repo, and any externally-hosted images embedded
   in the write-up markdown. Curl-check every image URL resolves before
   using it.
4. **Match the design system exactly** — reuse `eks/index.html` (or any
   existing case study) as the reference: extract its CSS and identity-bar
   markup programmatically (read the file, slice out the fragments) rather
   than retyping them, to guarantee byte-exact reuse. Every page needs: the
   spec sheet under the masthead, an architecture diagram with numbered
   edges, a "how the components communicate" wiring table + legend, and the
   verification ledger split into **Measured / Observed / By design** —
   don't relabel or soften that split, it's the whole differentiator of the
   site.
5. **Draw a new, original diagram** from this project's own README — don't
   reuse another case study's diagram shape or layout. Follow the
   established SVG conventions (box + colored header cap + icon slot + tag
   pill, numbered circles on edges, dashed scope boundaries for logical
   groupings). Reuse icon filenames across diagrams where the same tool
   already has one (check `add-real-icons.sh`'s file list first — e.g.
   `kubernetes.svg`, `github.svg`, `engineer.svg` are already in use).
   Validate the SVG is well-formed and visually sanity-check it (e.g. render
   via headless Chrome to a screenshot) before wiring it into the page —
   check for lines crossing through box interiors or label text.
6. **Write the ledger honestly.** A KPI-table claim like "100%" or "zero X"
   in the write-up is not automatically "Measured" — only mark something
   Measured if the README actually describes generating the condition and
   recording a result. Otherwise it's Observed (you checked existing
   state/logs/history) or By design (the config guarantees it, untested).
   Don't force a Measured row that isn't backed by an actual described test.
7. **"What actually broke" is optional.** Only include it if the source
   material documents real failures. Don't invent one for symmetry with
   other pages.
8. **Update the shared files:** add a new card to the landing page
   (`index.html`) linking to `<PROJECT-SLUG>/`, add the new icon filenames to
   `add-real-icons.sh`'s documented file list, and update the repo
   `README.md`'s file listing.
9. **Verify before opening the PR:** confirm the new page is well-formed
   HTML, screenshot it (light and dark) to check layout, and confirm all
   internal/external links and images resolve.
10. **Don't push to main.** Do this on a new branch and open a PR. Post the
    PR link, and call out anything found thin or overstated in the
    README(s) — where a claimed result isn't actually backed by a described
    test.
