# Colour cards: browse, choose and grow the library

Read when the user asks to view, select, recall, save or name a palette. Colour principles and production acceptance remain in [palette-system.md](palette-system.md). This is a colour-card interface, not a scientific plotting backend.

## User-facing usage

Open the [visual colour-card library](../assets/palettes/catalog.html): it works locally without a server, network request or installation. Search by Chinese name, stable ID or HEX; filter preferred combinations; select a card and copy its ready-to-send instruction. If clipboard access is unavailable, select the instruction and copy manually. Selection in the page does not execute plotting code or alter project files.

Example user requests:

- “打开色卡库，让我选配色。” → open the local cards; show names, roles and candidate status.
- “调用杏雨青荷。” → resolve `apricot_jade`, show the card and use its actual values with real group names in the current project.
- “这张改成雾海玫瑰。” → update the relevant project's mapping, preserve data and related panel identities, rerender through the selected RStudio/Origin route and rerun affected QA.
- “推荐一套浅暖的四组配色。” → inspect category/mark requirements, propose a documented extension or faceting; do not silently cycle a three-colour card.
- “把这张参考里的配色收进色卡库，命名为……” → inspect the reference, record values/provenance/roles, add a candidate and rebuild the browser.

When a requested name does not exist, report the nearest relevant existing options or create a new card only from supported evidence; never silently substitute. A palette-browser request alone needs no data, R installation or new scientific figure.

For a standalone handoff, the versioned download contains `index.html` and the full PNG overview. The same self-contained page can be deployed on GitHub Pages. See the [download and source build instructions](../README.md#构建与发布). The curated source credits accompany both files.

## One source of truth

[assets/palettes/catalog.json](../assets/palettes/catalog.json) is the editable registry; [catalog.html](../assets/palettes/catalog.html) is its generated visual view. Do not hand-edit HTML or duplicate palette constants in this guide. Historical observation records preserve what was seen, not the current selectable registry. Existing R `academic_palettes()` presets remain separate legacy alternatives. New scaffolds pin the current registry in `data/palettes/catalog.json`; `figure_config(palette_id = "rose_mist")` resolves that card into named group colours and records its version. Existing projects are not silently migrated.

From the skill root, these standard-library-only commands support retrieval and regeneration:

```sh
python3 scripts/palette_catalog.py --list
python3 scripts/palette_catalog.py --show apricot_jade
python3 scripts/palette_catalog.py --show 雾海玫瑰
python3 scripts/palette_catalog.py --build
```

List/show are read-only; build validates the registry and replaces only the generated HTML. Invalid registry or unknown name returns exit 2; successful retrieval/build returns 0. The helper does not use the network, render data plots, install packages or change a project. In another working directory resolve the actual installed skill root first.

## Adding a named card during future learning

1. Follow the existing [reference-learning protocol](reference-learning-protocol.md). Identify what the colours encode, why their hierarchy works, appropriate mark/background types, and where it would fail. Save a new card when it adds a useful combination; equivalent values/roles should normally gain a source or alias rather than a duplicate.
2. Use explicit HEX/RGB from supplied labels, accessible source code or an authoritative colour specification when available. For appearance-only screenshots, do not claim exact original HEX: create a clearly labelled inspired proposal, or mark pixel samples as rendered/approximate and record the sampling/compositing limitation. Never promote an unavailable value to an exact source colour.
3. Name the card with a readable Chinese name and unique stable ASCII ID; preserve old IDs. Store main/secondary roles and a semantic kind. Back up before edits; for material changes increment `version`, record the reason and preserve the prior revision in the backup/provenance. Project copies remain pinned to their chosen values/version, never silently migrate old figures.
4. Save the fields below, check HEX/RGB/uniqueness/source-link validity with the helper, then rebuild the HTML. Reopen the cards and verify swatches, names, roles, filter/search and instruction selection. Add the source to the existing source index; do not bundle the original figure or private identifying paths.
5. Newly learned cards start as `candidate`. Actual data-mark inspections can justify `reviewed-in-context` only with dated evidence, tested dimensions/background/marks and CVD/grayscale scope recorded in `review_evidence`. It is not universal approval. Reject or deprecate misleading/redundant mappings; do not add every attractive screenshot indiscriminately.

Required record fields (match current JSON): `id`, `name`, `version`, `aliases`, `kind`, `priority`, `main`, `support`, `source_colors`, `rgb`, `recommended_categories`, `background`, `text`, `status`, `uses`, `limits`, `source`, `validation`. `source_colors` records the exact registered values even for a declared inspired proposal; it does not by itself imply original author colours. Explain the value basis in `source.value_basis`.

- `kind`: categorical / sequential / diverging / cyclic / emphasis. Record ordered anchors, centre policy and endpoint behaviour as appropriate in additional `mapping` metadata; no categorical card becomes a continuous scale merely by interpolation.
- `source`: skill-local observation record, figure/sheet identifier when applicable, source label, value basis, review date; include public source URL/figure/version when applicable. Keep source authors separate from Raphael He's library curation.
- `validation`: registry results and actual-figure/CVD/grayscale status; store evidence and contextual limits for checks actually run. `priority` denotes selection preference, not test quality. No reference-only learning can certify future figures.

## Production handoff and process checks

Use the single [selection and QA workflow](palette-system.md). Confirm the palette once for the entire figure set at step 6, unless already specified/confirmed or explicitly delegated; reuse the saved decision on every related figure and resumed session. Do not ask once per image. Read the selected JSON card, bind main colours to verified names, wire values to actual R configuration/layers, save ID/version/values/roles in the project's existing manifest, execute and inspect the selected RStudio/Origin route. A palette ID alone does not change colours. Source/additional fill arrays are not spare group colours by default.

Behavioural examples: (a) a known three-group dataset + “杏雨青荷” → exact card lookup, stable group mapping, shapes and contrast checks, project-level validation; (b) “拿杏雨青荷画有正负值的热图” → preserve stylistic intent but select a separately defined diverging mapping after establishing centre/units; never stretch three category colours across numbers; (c) a screenshot with no labelled colour codes → named inspired candidate with explicit uncertainty, not a recovered exact palette. These are decision checks, not rendered-figure validation.

## Verification scope (2026-11-05)

Before the default/remix update below, the library contained ten candidate cards, with three preferred combinations including the default. Registry/role/RGB/source-link checks, CLI name/alias lookup, unknown-name rejection and generated-HTML data consistency passed locally.

An offline component test now compiles and executes the exact generated inline JavaScript against a minimal in-memory DOM and a stub clipboard. Run [the reusable test](../scripts/test_palette_catalog.cjs) with an available Node runtime:

```sh
node scripts/test_palette_catalog.cjs
```

If Node is not on PATH, locate an existing bundled runtime and invoke its executable; do not install a dependency merely to run this check. On 2026-11-05 the configured Codex bundled runtime ran this command successfully: **18 checks passed, exit 0**. Coverage: initial/default order; each card's ID/name/alias lookup, main/support HEX binding and versioned selection instruction; trimmed case-insensitive HEX search; preferred filter; empty results; clipboard-success logic; denied/missing clipboard fallback; unchanged registry after selection.

These tests use DOM/clipboard doubles, not a real browser, and do not validate CSS layout, physical clicks, keyboard focus behaviour, system clipboard permissions or final-size accessibility. Automated browser access remains blocked by the embedded browser protocol policy; no alternate browser/server was used to bypass it. User-supplied recording evidence below now covers the visible local-preview layout and scrolling, but not the unrecorded interactions. The earlier JavaScript syntax uncertainty is resolved by successful offline compilation/execution. No actual scientific figure or colour-vision/grayscale acceptance is claimed.

### User-recorded visual check (2026-11-05)

Evidence: user-supplied `录屏2026-11-05 09.19.16.mov`, duration 12.88 s, 2948 × 1894 px, SHA-256 `aa2e9b384b5102fde4129732ff3a84d358f63c771ea24bbb88148dbee9f0ec2a`. Reviewed 13 approximately one-second-spaced frames plus source-resolution frames at 2.5 s and 6.5 s. The visible environment is a local HTML preview with Codex controls; this is not evidence of a separate Safari/Chrome test. Recording/images are not bundled into the skill.

| Check | Observed evidence | Status and scope |
|---|---|---|
| Initial page and card count | Opening view shows title, search/filter controls, 10/10 count and default apricot card first | PASS in recorded viewport |
| Card layout and legibility | Three columns, separated cards, readable names/IDs, main/support swatches, HEX labels and selection buttons | PASS for visible collapsed cards at the recorded desktop size; no obvious internal overlap/overflow |
| Scroll coverage | Approximately 2–9 s traverses all four rows; final row contains the tenth card and page footer | PASS for visible scroll/display; last-row empty columns are expected with ten cards in three columns |
| Search, filter, details, selection, copy | No demonstrated input/filter change, expanded details, selected-card instruction or clipboard result | NOT OBSERVED in this recording; existing offline tests remain the only functional evidence |
| Other widths, keyboard operation, actual figure colours | Not shown | NOT AUDITABLE from this recording |

The host's floating Codex input bar temporarily overlays the bottom of the preview; scrolling brings card contents into view. Do not attribute that host UI to the catalogue CSS. Screen-recorded swatches support a layout review, not a colour-calibrated measurement or CVD/grayscale certification. No page change was justified by this evidence; only the verification record was updated.

### User-supplied Safari screenshot (2026-11-05)

The screenshot named `截屏2026-11-05 09.24.48.png` shows Safari displaying the local colour-card HTML. Visible evidence confirms successful loading, title/curator text, search/filter controls, the 10/10 counter, and the first three cards with names, main/support swatches and HEX labels. The visible desktop layout has no obvious internal overlap or text overflow. **Safari opening and visible first-screen rendering: PASS, based on user-supplied evidence.** This supplements the earlier local-preview recording; the earlier recording alone did not establish Safari compatibility. The restriction encountered by the agent applied to its automation tool, not the user's browser or the file's ability to open. Search/filter changes, selection, clipboard results, off-screen cards in Safari and other viewport sizes are not demonstrated by this still screenshot. Existing offline tests and the earlier scroll recording retain their respective scopes; no full interactive or scientific colour-accessibility certification is implied.

### Default and related combinations (2026-11-05)

The user selected 雾海玫瑰 (`rose_mist`) as the default recommendation for new figure sets. Existing project choices remain pinned; no per-figure re-prompt or silent recolouring. The registry now contains 13 candidates: the ten original selections plus 玫瑰杏灰 (`rose_apricot_slate`), 玫瑰青砂 (`rose_jade_sand`) and 浅藤杏雾 (`lavender_apricot_mist`). These three newly arranged combinations reuse explicitly printed HEX from the supplied sheets; they are not attributed to the source illustrator as existing palettes. Their source records identify the contributing sheets and new role assignment.

The earlier recording/Safari acceptance concerns the previous ten-card revision only. New-card layout and actual-figure/CVD/grayscale review remain unverified; registry and offline interaction checks are reported separately.

Updated-registry checks on 2026-11-05: build/validation passed for 13 cards; the offline DOM test passed 21 checks (exit 0). The test now accepts multiple legitimate substring-search results and checks the requested card explicitly, rather than assuming every ID is a unique substring. This does not change page search behaviour. Skill structure validation also passed.
