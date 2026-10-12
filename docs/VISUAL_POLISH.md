# VesselRisk — competition-grade visual polish

> Historical implementation/verification record. The current desktop-only UI, renamed Model evidence and validation scope are documented in `review/COMPLETION_SUMMARY.md` and `review/BUILD_VALIDATION.json`; older layouts and test counts below are not current-version claims.

2026-10-02. Scope: presentation, recording legibility and interaction feedback. The existing workspace / Evidence Lab structure, brand, product features and scientific wording remain intact.

## 1. Visual issues found

- Many supporting labels were 7–10 px and low contrast. Probability values were brighter than their white backgrounds could support, and SHAP measurement labels could truncate.
- Selected arteries were distinguished mostly by a pale teal fill, close to the low-probability color. Anatomy labels, selection state and probability encoding competed for meaning.
- The heart shared vertical space with a large header; its interaction hint sat over the apex. The body lighting flattened surface detail.
- Evidence tables, axes, uncertainty notes and failure counts were difficult to scan at recording size. The confusion matrix did little to distinguish correct and incorrect cells.
- The mobile anatomy container measured 290 px high while its canvas measured only 150 px. A settled browser check confirmed this, beyond the existing journey's visibility assertions.
- Edited-input feedback was too quiet beside the still-visible old result.

Inspected the live workspace, all four Evidence Lab sections, existing review/demo screenshots, six-page report and five-minute demo script. Recorded both 1440 × 1000 and 1920 × 1080 before touching the product.

## 2. Changes implemented

| Area | Implemented change |
|---|---|
| Workspace | Modestly wider explanation column, consistent input alignment, larger labels and units, darker supporting copy; established three-column layout retained. |
| Heart | Reclaimed header space at recording widths; restrained lighting adjustment; camera moved slightly back so the enlarged display keeps the complete anatomy visible; hint moved below the model. Canvas now fills its actual container, including mobile. |
| Selection | White artery outline and checkmark; matching selector border; navy underline on target tabs and focused probability. Projected artery buttons expose `aria-pressed`. Probability bands and mesh-to-artery mappings are unchanged. |
| Local explanation | Measurement labels 11–12 px, signed values 11 px, units 10 px; stronger coral/teal bars around a visible zero line; long labels wrap. Approximate SHAP values, order, normalization and additivity display are unchanged. |
| Evidence Lab | Table data 12 px / headers 11 px on desktop, stronger row separation, larger chart labels, readable notes, clearer metric hierarchy, 30 px confusion counts and muted warm error cells. |
| Threshold evidence | All operating-point rows remain visible and equally styled. FP/FN values are easy to find; no row is presented as a confirmed winner. |
| Provenance / failures | Larger protocol text, registry and failure-table values; stronger leakage pass/blocked labels and source information. |
| Feedback | Amber stale-result status; clearer active controls; short transitions. SHAP bars update directly instead of animating through intermediate lengths. Probability numbers never animate. |

Product edits are limited to `web/app/polish.css`, its import in `web/app/layout.tsx`, and presentation / accessibility attributes in `web/components/HeartViewer.tsx`. No dependencies or architecture changes.

## 3. Why these changes improve judging

- **First minute:** the actual anatomy carries more visual weight, while the selected artery is identifiable independently of its probability color.
- **Explanation:** a viewer can follow target → probability → measured input → signed contribution without decoding faint labels. Existing uncertainty language is easier to read.
- **Evidence:** section headings, aligned numeric columns and error cells guide the eye to comparisons and tradeoffs. Evidence density and methodological qualifications remain available.
- **Demo reliability:** selected states, edited-input feedback, keyboard selection and the corrected mobile canvas make the same working product easier to demonstrate.

Research informed restraint rather than a redesign:

- Revisited the [Smart Scribes repository](https://github.com/Kartavya728/Smart-Scribes) and its [15-slide presentation](https://drive.google.com/file/d/1ddnYoN5SRydPX6gg-2T6K_LbyNhOXlyg/view), especially the concrete input-to-output journey. Current repository contents are not a verified competition-time snapshot; video playback was not independently reviewed. No visual assets or code were copied.
- [OHIF's official overview](https://ohif.org/) emphasizes medical visualization and efficient custom workflows. It is a workflow reference, not evidence that VesselRisk is a clinically validated viewer.
- [Carbon's axes and labels guidance](https://www.carbondesignsystem.com/building-blocks/data-visualization/axes-and-labels) supports clear descriptors and faithful scales. Chart domains, ticks, data points and baselines were preserved; only their reading scale changed.

These are design judgments, not measured judge-comprehension or competition-outcome claims.

## 4. Before / after screenshots and verification

Open the [offline comparison page](../review/visual-polish/index.html). It switches between before, after and side-by-side views, at both recording sizes. Each version contains 26 real screenshots: workspace, explanation, LCX X-ray, RCA isolation, validation, comparison/confusion, operating thresholds, global SHAP, robustness, provenance, failure case, second patient and stale input.

Original-size examples:

| State | Before | After |
|---|---|---|
| Workspace, 1440 | [PNG](../review/visual-polish/before/1440-workspace.png) | [PNG](../review/visual-polish/after/1440-workspace.png) |
| Workspace, 1920 | [PNG](../review/visual-polish/before/1920-workspace.png) | [PNG](../review/visual-polish/after/1920-workspace.png) |
| Model comparison / confusion | [PNG](../review/visual-polish/before/1440-comparisons.png) | [PNG](../review/visual-polish/after/1440-comparisons.png) |
| Research thresholds | [PNG](../review/visual-polish/before/1440-thresholds.png) | [PNG](../review/visual-polish/after/1440-thresholds.png) |
| Provenance | [PNG](../review/visual-polish/before/1440-provenance.png) | [PNG](../review/visual-polish/after/1440-provenance.png) |

Live FPS and request latency naturally differ across runs; these screenshots are not performance benchmarks. Component captures may be taller after text enlargement. The comparison page links to the native PNGs so scaled previews do not conceal readability differences.

Validation performed on the production build:

- `npm run typecheck`, `npm run lint`, `npm run build`: passed.
- Existing Playwright desktop and mobile journeys: **2 passed**. Prediction, artery selection, X-ray/isolation, evidence, held-out outcomes, edited input and JSON export exercised. Existing tests unchanged.
- Final 26-state screenshot run: no page errors or horizontal overflow at either recording size; 10 canonical review screenshots also recaptured.
- Supplemental checks: all four Evidence Lab sections at 390 px without page overflow; keyboard artery selection; reduced-motion preference; offline comparison controls and loaded images. This is targeted QA, not a claim of a full accessibility audit.
- Settled mobile canvas after correction: **290 px container / 290 px canvas**.
- All **26 frozen scientific/API/data/anatomy files** match the before SHA-256 fingerprints. Model artifacts, API logic, metrics, validation and geometry mapping unchanged.
- Six-page report refreshed with real screenshots; every page rendered and inspected. Extracted PDF text is identical to the original report.

### Restore the before version

There is no Git repository in this workspace. The [before-source ZIP](../review/visual-polish/before-source.zip) preserves the original app sources, demo/review screenshots and report. The original science fingerprints are in [frozen-science.json](../review/visual-polish/frozen-science.json).

To restore this snapshot from the project root, first preserve any later edits you want to keep, then run:

```powershell
Expand-Archive -LiteralPath 'review/visual-polish/before-source.zip' -DestinationPath '.' -Force
Remove-Item -LiteralPath 'web/app/polish.css'
Set-Location web
npm run build
```

Restart the local frontend afterward. Regenerate the review package if you intend to distribute the restored build. The ZIP is a source/screenshot/report snapshot, not a dependency or environment backup.

## 5. Considered but rejected

- A new dark interface or different dashboard architecture: would disrupt the established hierarchy and brand.
- Larger zoom without framing changes: would crop anatomy and make rotation harder to follow.
- Strong glow, pulsing vessels or decorative motion: would distract from anatomy and blur probability versus selection semantics.
- Animated probability numbers or SHAP bar interpolation: would temporarily show values or lengths that do not correspond to the returned explanation.
- Hiding methodological notes or highlighting only favorable threshold rows: would reduce scientific transparency.
- Additional summaries, badges and result interpretations: would add clutter or alter scientific wording.

## 6. Remaining UI weaknesses

- Dense evidence and the lower explanation sections still require scrolling. Recording should pause on the relevant section rather than compress the entire page into one frame.
- Projected artery labels have no collision-avoidance system; unusual rotations or zoom levels can bring labels close together. The fixed artery selectors remain available.
- License and secondary metadata remain smaller than primary evidence. Native 1080p capture and deliberate framing are preferable to downscaled full-page screenshots.
- Readability has been visually checked, not tested through a blinded judge study or a compressed YouTube recording.

## 7. Final visual-polish score

**93 / 100 — subjective review score, not a competition result.**

| Dimension | Score |
|---|---:|
| Hierarchy and anatomy prominence | 24 / 25 |
| Typography and recording readability | 23 / 25 |
| Selection and interaction clarity | 23 / 25 |
| Evidence scanability and restraint | 23 / 25 |

The improvements concentrate on the first-minute product view and the evidence screens used in the five-minute demo. No scientific performance gain is implied.
