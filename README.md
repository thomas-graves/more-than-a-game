# More Than a Game — local beta
FIT3179 Data Visualisation 2 · Prepared 15 October 2026.

**All sports, population, opinion and facility attributes are synthetic. This beta
demonstrates layout and interactions; it is not ready for final submission.**
The real state outlines come from Natural Earth.

## View locally
In a terminal in this assignment directory, run:

~~~powershell
python -m http.server 8000 --bind 127.0.0.1
~~~

Visit http://127.0.0.1:8000/ in your browser. Stop with Ctrl+C.
Do not open index.html directly using file://: browsers block CSV/JSON loading.
VS Code Live Server also works. No npm installation or build step is needed.
Vega and Pure.css are local; Google Fonts are optional, with system fallbacks.

## Included
- A responsive, single scrolling page with 12 Vega-Lite visualisations.
- State choropleth, proportional-symbol and facility point maps.
- Coordinated map/state dots and age heat-map/profile views.
- Dropdowns, tooltips, legend highlighting and visible narrative findings.
- Small synthetic CSVs and consistent weighted headline JSON (provenance recorded here).
- Local library distributions and their original licence files.
- Source matrix, methodology notes and AI acknowledgement.
- Existing brief and PDFs preserved.

## Interactions
1. Switch club ranking between adults and children.
2. Choose a demographic on the state choropleth; click a state to highlight its
   comparison dot. Double-click to clear.
3. Change the sport on the proportional-symbol map; its size scale stays fixed.
4. Filter fictional Victorian facilities by sport.
5. Click an age heat-map cell or choose a sport above it to update the profile.
6. Click a gender legend item to highlight that category.
7. Click a scatterplot point to highlight its state.

## Files
- index.html: semantic story structure, annotations, sources and AI acknowledgement.
- css/layout.css: layout and responsive rules.
- css/style.css: typography and palette.
- js/embed.js: embedding, error handling, coordinated views and resizing.
- charts/*.json: 12 readable Vega-Lite specifications.
- data/: synthetic attributes and real geometry; see GEOGRAPHY.md.
- CHART_SOURCE_MATRIX.md: beta fields and intended final sources.
- scripts/build_beta.py: deterministic generator. Rerunning overwrites generated
  beta files; it preserves the existing project brief and PDFs.
- scripts/check_beta.py: structural/data integrity checks.
- scripts/browser_check.py: browser rendering and interaction checks.
- .beta-tools/: ignored development dependencies, original geometry and QA screenshots.

## Replace before submission
1. Open the actual sources; verify releases, sheets, fields and denominators.
2. Replace CSVs, headline figures and illustrative findings together. Keep the
   field names where sensible, or update corresponding JSON specifications.
3. Check reliability, uncertainty, missing data and methodology breaks.
4. Replace fictional facilities with verified Victorian or Casey records.
5. Verify state volunteering comparability; use the brief's fallback if needed.
6. Replace beta geography with the appropriate ABS TopoJSON where required.
7. Add your name, source dates and exact citations; review AI acknowledgement.
8. Align with the hand-drawn sketch, publish and test GitHub Pages while logged out.

## Data definitions
Adult = 15+; child = 0–14. Chart 1 uses active adults only.
Headline adult club and volunteer rates are weighted by synthetic adult population.
Gender subgroup rates are independently constructed; subgroup weights are not modelled.
Age/gender views show organised participation, not strictly clubs. Organiser, sport
and role categories can overlap. Opinion categories sum to 100% per statement.
Fictional facilities are not evidence of access or an actual facility directory.

## Verification
~~~powershell
python scripts/check_beta.py
~~~
Browser QA uses Playwright with installed Chrome:
~~~powershell
python scripts/browser_check.py
~~~
The site itself does not depend on Playwright. See the script's docstring for setup.

## GitHub Pages
Upload index.html, css/, js/, charts/, data/ and vendor/ to the repository root and
configure Pages for that branch/root. Relative paths support repository subpaths.
Keep specifications public alongside the page. Exclude .beta-tools/.
Creating local files does not publish a website.

## Classroom presentation copy
At the student's request for the teaching-staff beta review, the public interface
uses reader-facing copy and expected-source labels without beta banners.
The underlying numerical data and facility records are still synthetic.
The source lines show intended production providers, not verified extraction
provenance. They must be checked and replaced together with the data before the
final assignment. Exact source mappings remain unverified in CHART_SOURCE_MATRIX.md.
The student author name still needs to be added for the final submission.
scripts/prepare_presentation.py applies the display copy after the generator runs.

## Expanded facility layer
The synthetic Victorian facility layer has 1,065 records: soccer 210, Australian
football 275, cricket 140, netball 150, tennis 100 and basketball 190. The original
84 records are retained; added points are checked against the Victoria polygon,
including coastline and holes. Most added points cluster around Melbourne and
regional towns, with some rural locations. These are not real facility records.
Regenerate using scripts/expand_facilities.py; build_beta.py also invokes it.
