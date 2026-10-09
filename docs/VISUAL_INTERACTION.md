## First-opening orbit and status cleanup

Removed the prediction-status strip beneath the heart, including its unused styles and icon. Prediction completion is visible through populated estimates and the enabled export action; dirty and busy explanations remain in the explanation panel. Orbit starts only on the first workspace mount in a page session. Target selection, Reset and returning from Evidence Lab do not restart it. Manual Orbit remains available.

## Consistent camera scale and credit placement

Initial, Reset and all four target views share the same camera-distance constant. Target views use the same vertical focus center as manual controls, leaving space above the heart. BodyParts3D / DBCLS attribution is aligned to the lower right in normal and expanded anatomy.

## Taller field scroll area follow-up

The patient panel now has an 840px minimum height on desktop rather than fitting its footer into the viewport. At 1536x730, the actual scroll area between search and prediction status is 448px, up from 216px. The footer remains reachable by ordinary page scrolling. The anatomy column keeps its own viewport-based height so the taller form does not enlarge the heart. Body-field order and calculated BMI are retained.

## Probability placement follow-up

Removed the four cards above the heart and their component/styles. The explanation tabs now show all four exact probabilities. A compact target dropdown replaces the artery heading, shows the full vessel name, and synchronizes with explanation tabs and anatomical labels. Overall CAD returns to a front overview with no individual artery selected; vessel probabilities still determine their colors. CAD classification and its research cutoff remain available in the CAD explanation. Expanded anatomy retains the selected estimate because the explanation panel is outside the expanded view. Desktop captures at 1440x900, 1536x730 and 1920x900 show a 50px toolbar, all four probabilities fitting their tabs, and no horizontal overflow.

# Coronary visualization and explanation update

## Desktop input space follow-up

The old panel height subtracted 210px even after the heading moved into the header. The desktop panel now reserves 122px for the 88px header, 18px top spacing and 16px bottom spacing, without an arbitrary height cap. Removed the case-summary minimum-height gap; inputs scroll within the remaining space and the prediction footer stays available.

## Remove duplicated artery cards

Removed the three LAD/LCX/RCA selector cards below the canvas and their bar/comparison-caption styles. Artery selection remains available through the 3D labels, top probability cards and explanation tabs; these still synchronize the camera and explanation. The canvas fills the freed space. Removed the cards' previous-prediction state, difference formatter and comparison styles as well. Expanded view retains the current selected-artery probability.

## Desktop-only directive, 2026-10-09

The user explicitly requires desktop-only development from this point forward. `View explanation` was removed because the explanation is already visible beside the heart. Mobile edit/back shortcuts, automatic result scrolling, phone-only CSS blocks, portrait camera fitting and mobile browser journeys were removed. Vessel selection continues to update the explanation directly. Earlier mobile checks below are historical; they are no longer part of the supported interface or test suite. The persistent rule is in root `AGENTS.md`.

## Compact anatomy viewer follow-up

- The viewer now opens with a single toolbar: selected artery code/name, anatomy information, explanation navigation and expand. The normal view uses the probabilities already shown in the overview; expanded view adds the selected probability to its toolbar.
- Removed the decorative artery heading and the separate CAD classification row. Positive/negative is shown inside the Overall CAD card, with the research cutoff behind an information button. Unchanged predictions no longer display "No change" or redundant comparison markers.
- Course, usual supply and the source link appear in a non-modal popover. It closes on Escape, outside click or vessel selection. It overlays the canvas without changing its position or size and stays above projected artery labels. Escape closes an open popover before exiting expanded mode.
- The viewer's explanation action selects the corresponding vessel explanation. Mobile retains an edit-inputs shortcut. Portrait canvases adapt camera projection to keep the reference heart in view when expanded.
- Build and lint passed; all 14 browser journeys passed. Four affected journeys were rerun successfully after correcting popover stacking and portrait projection. Visual review covered desktop, mobile, expanded mode and 320px width; toolbar height measured 46–50px, with no horizontal overflow.

## Evidence charts follow-up

- Validation opens with a four-target comparison: ROC-AUC dots with conditional bootstrap intervals, or recall at the fixed 0.50 cutoff. Both use a full zero-to-one scale. Selecting a row opens that target's existing evidence.
- LCX and RCA threshold comparisons plot missed positives and false positives together, with a shared zero-based patient-count scale within each comparison. Only the two operating points of the frozen baseline policy are paired; expanded model-search results remain in the expandable exact-metrics table.
- Values come directly from the existing evidence response. LCX: missed positives 69 to 19, false positives 30 to 93. RCA: missed positives 69 to 15, false positives 34 to 101. Recall gains do not imply a new clinical cutoff or better underlying ranking.
- The six-page report replaces its research operating-point table with vector count bars and uses current application captures. Existing ROC, calibration, SHAP, subgroup and ablation evidence is retained without duplicate charts.
- Production build and lint passed. All 12 browser journeys passed, including chart selection, metric switching, frozen-policy counts and mobile overflow checks. The six rendered report pages were visually inspected. Captures are `demo/screenshots/evidence-overview*.png` and `evidence-thresholds-*.png`.

2026-10-09. This update addresses the supplied Track A requirements for interactive anatomical risk mapping, interpretable patient measurements and integrated prediction updates. It does not assign a competition score.

## User-visible changes

- Selecting LAD, LCX or RCA from the anatomy, probability cards or explanation tabs guides the camera to an artery-specific view. Manual navigation interrupts guidance. Reset returns to the original view; auto-orbit, X-ray, vessel isolation and expanded view remain available.
- The selected artery has a full name and exact probability in the viewer. Label leaders terminate on sampled vertices of the actual artery trunk, rather than its bounding-box center. The anchor follows the camera-facing part of that trunk; it is not a lesion marker. The cards remain usable when a projected label is outside the view.
- Three proportional probability bars complement the existing three color bands. When the same profile is edited and predicted again, white ticks mark the preceding result and signed percentage-point differences show the change. Switching/resetting cases or importing another profile clears this comparison. Differences describe model response, not treatment effects.
- Overall CAD now explicitly shows the model's positive/negative classification and its 50% research cutoff.
- The explanation initially shows five factors with readable values (Yes/No, units, or explicitly named category codes). Model identity, calibration, fitted-model ranges, model comparisons and SHAP reconstruction remain in an expandable details section. Validation remains accessible through Evidence Lab.
- Removed repeated implementation badges, idle FPS and structure-count labels. The clinical disclaimer and anatomical attribution remain visible. Height and Weight retain the second input row; BMI is calculated automatically.
- The canvas renders on demand while idle, with continuous frames only during controls/animation. Camera guidance and probability bars respect reduced-motion preferences.

## Scientific boundaries

The same model probabilities, SHAP values, artifacts and reference geometry are used. There are still three vessel-level predictions; branches share the probability of their parent target. The 3D anatomy is not patient-specific, colors do not encode stenosis severity, and no lesion localization or blood-flow simulation is introduced.

The earlier near-perfect numerical self-rating in FINAL_AUDIT_RESULTS.md was withdrawn. Functional coverage and passing tests do not establish a judge's score.

## Review and verification

Production build includes TypeScript validation; ESLint is run separately. Browser checks cover real predictions and JSON exports, BMI and body-field placement on desktop/mobile, artery navigation, numeric comparison against API responses, comparison reset for a different patient, model-detail disclosure, orbit, full-screen exit, mobile reduced motion, and the existing Evidence Lab journey.

Final verification: production build and ESLint passed; all seven real-browser tests passed in 29.6 seconds using the production frontend and local model API. Desktop and mobile screenshots, including each focused vessel, were visually inspected. This is functional and visual verification, not a user study or a claim of performance on every device.

Actual captures are in `demo/screenshots/`: `patient-workspace.png`, `coronary-anatomy.png`, `focused-lad.png`, `focused-lcx.png`, `focused-rca.png`, `prediction-changes.png`, `mobile-workspace.png`, and `mobile-lcx.png`.

A source snapshot from before this update is kept locally at `tmp/visual-review/before.zip`. It covers the six existing UI/test files changed in the initial pass; it is not a complete repository backup.

## Follow-up: clearer results and navigation (2026-10-09)

- Editing inputs, loading another case or importing a profile now marks the explanation as a previous result until a successful prediction replaces it. The in-flight state explicitly says the explanation is updating.
- Each selected artery shows a concise reference course and usual supply region, with a source link. These descriptions are general anatomy, do not change with patient inputs, and do not map myocardial injury or lesion locations.
- Large probabilities remain in the overall summary and selected-artery viewer. Removed duplicate percentages from the explanation and lower artery selectors; retained selection, proportional bars and previous-prediction markers.
- Desktop input-panel height follows the viewport so the prediction action fits in a 1440 × 900 first view. Mobile predictions focus and scroll to results, with links to the matching explanation and back to inputs. Reduced-motion settings are respected.
- Measurement search spans all 55 inputs, displays each result's group, and restores the previously selected group when cleared.
- The explanation links to model validation with patient count and internal/external validation scope; it no longer presents AUC as a shorthand answer to individual-prediction reliability.

Validation: production build and ESLint passed. All 10 Playwright tests passed against the production app and actual API, including three new regression journeys for stale explanations, cross-group search and mobile navigation. Desktop, stale-result and mobile captures were visually reviewed. Existing BMI row order, derived BMI, export, camera focus, orbit and Evidence Lab checks also passed.
