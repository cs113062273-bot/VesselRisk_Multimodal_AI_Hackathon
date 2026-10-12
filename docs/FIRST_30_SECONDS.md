# VesselRisk: first-visit review

> Historical implementation/verification record. The current desktop-only UI, renamed Model evidence and validation scope are documented in `review/COMPLETION_SUMMARY.md` and `review/BUILD_VALIDATION.json`; older layouts and test counts below are not current-version claims.

Reviewed 2026-10-02 against the supplied first-30-seconds proposal. The current project name is VesselRisk; existing branding, grey form fields and previous visual refinements were preserved.

This is an expert walkthrough using real browser interactions, not a timed study of unfamiliar judges. The time windows below describe the intended order of attention, not guaranteed completion times or prediction latency.

| Attention window | What the visitor should understand | Finding and action |
|---|---|---|
| 0–5 seconds | What goes in and what comes out | Replaced the generic subtitle with “55 clinical inputs → four calibrated estimates → interactive coronary anatomy.” The existing large heart remains the central visual. |
| 5–10 seconds | What to do first | The previously sparse explanation panel now offers three short steps: predict the prepared profile, select an artery, inspect evidence. This panel disappears when a real prediction arrives. There is still one primary Predict button, and no automatic or fabricated prediction. |
| 10–20 seconds | Why the heart is interactive | Confirmed LCX selection updates the matching explanation and X-ray preserves the selected state. Existing artery controls, camera, anatomy and probability colors needed no further changes. |
| 20–30 seconds | Where to verify the system | Replaced the decorative workspace breadcrumb with four restrained evidence labels. “Held-out evaluation” opens Evidence Lab. The lab now explains the evaluation method above its existing metrics. |

## What changed

- Workspace subtitle explicitly connects clinical inputs, estimates and anatomy.
- Header evidence labels: **Calibrated models · Leakage guard · Held-out evaluation · Reference anatomy**. They describe the system, not an individual prediction's provenance or clinical certification.
- Initial explanation state uses an ordered, readable guide without adding a new workflow or competing CTA.
- Evidence Lab adds **How was this evaluated?** followed by 5 × 2 outer CV, 3-fold inner selection, calibration within training folds and repeat-averaged held-out predictions. These details were checked against the frozen evidence artifact. Existing metrics, intervals, protocol explanations and limitations remain.

Product edits are limited to `web/app/page.tsx`, `web/components/ExplanationPanel.tsx`, `web/components/EvidenceLab.tsx` and `web/app/polish.css`. No ML, API, geometry, camera, probability mapping, dependencies or model-selection changes.

## What was deliberately not adopted

- No further enlargement of the heart: the previous refinement already made it the centerpiece, and extra enlargement risks cropping.
- No “clinical command center” claim: a research prototype should retain its visible scope.
- No blanket “HELD-OUT CV” prediction badge: custom profiles use a full-cohort model; held-out evaluation is a separate source of evidence.
- No claim that this project is scientifically superior to previous winners. Public promotional material does not establish such a comparison.
- No chatbot, voice, scan upload, decorative animation or additional model experiments.
- No invented score or promise of winning. The walkthrough assesses clarity, not ranking.

The [Intel winner article](https://community.intel.com/t5/Blogs/Tech-Innovation/Artificial-Intelligence-AI/Meet-the-Winners-Top-Projects-from-the-Advent-of-Multimodal-AI/post/1671116) was checked. It discusses visual direction and integrated workflows in a different event; it supports those design references, not a transferable scoring formula. Earlier same-ecosystem source checks and their limitations remain documented in [RESEARCH.md](RESEARCH.md).

## Verification and captures

- Typecheck, lint and production build passed.
- Existing desktop/mobile Playwright journeys: 2 passed, including prediction, vessel interaction, evidence, changed inputs and export.
- Eight before and eight after screenshots: ready state, actual prediction, linked LCX/X-ray, Evidence Lab; each at 1440 × 1000 and 1920 × 1080. No page errors or horizontal overflow.
- Canonical ten review screenshots and the five demo screenshots were refreshed from the current application.
- First-look evidence link and initial-state mobile layout checked separately.
- Frozen scientific/API/data/anatomy hashes rechecked unchanged.

See the [before/after comparison](../review/first-30-seconds/index.html). Baseline screenshots were captured from the development preview, so its small framework indicator appears in some before images; after captures use the production build. That indicator is not part of the product changes. FPS is a live measurement and naturally varies.

The [before-source snapshot](../review/first-30-seconds/before-source.zip) preserves the current VesselRisk sources as they were before this pass. To undo only this pass, restore the four product files listed above from that archive and rebuild; do not use the older CardioVision snapshot to revert this newer branding.
