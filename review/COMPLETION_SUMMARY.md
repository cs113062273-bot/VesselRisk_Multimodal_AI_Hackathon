# VesselRisk current review snapshot

Updated 2026-10-09 (Asia/Taipei). This snapshot supersedes older review-package descriptions and test counts. It is a review package, not evidence that the competition entry or video has been published.

## Current deliverables

- Four frozen trained models and nested held-out evaluation; all target labels excluded from inputs.
- Horizontal Patient profile above a heart canvas and one patient-prediction panel. Four probabilities stay in synchronized explanation tabs; contribution accounting, top factors, candidate comparison and fitted-model ranges update with the patient.
- Real licensed coronary meshes, artery selection, rotate/zoom, X-ray, isolation and expanded view. Reference anatomy shows vessel-level probability.
- Surface-anchored probability labels, collision avoidance, selected-vessel silhouette and transient changes after prediction. Orbit starts on first opening and after each successful prediction.
- Independent Model evidence overview, validation, interpretability, robustness and provenance contain fixed cohort results; patient edits do not change them.
- Protocol-bound checkpoints and pre-deserialization checks for models, OOD, registry, evidence and schema.
- Frozen local explanation sensitivity audit: four predefined held-out profiles, four targets, seed/computation/background comparisons. Calibration group counts, descriptive intervals, training-prevalence baseline and separate-repeat metrics.
- Input origins tracked across cases, defaults, edits, imports and BMI calculation; exports snapshot origins with submitted values.
- Current eleven desktop screenshots, six-page report, five-minute demonstration script and English narration, Devpost draft, license/data/model documentation, trained weights and buildable source.

## Evidence and validation

Product validation commands and outcomes are recorded in `BUILD_VALIDATION.json`; older full-suite and extracted-runtime results are explicitly historical. Five focused desktop journeys passed, with one imported-profile prediction timing out initially and passing on retry. First-request latency has not been established. Generated archives include a `FILE_MANIFEST.json` and SHA-256 sidecar. The packaging script requires the runtime and reliability files and verifies the complete archive CRC and file hashes. Source cleanup and its validation are documented in `../docs/SUBMISSION_CONTENTS.md`.

Use `python scripts/start.py --setup` on first installation; then `python scripts/start.py`. Dependencies and the production frontend are installed/built locally. The repository and generated archive exclude `.next`, dependencies, local QA assets and historical backups. No inference credentials or retraining are needed.

## Scientific limits

Headline ROC-AUC is CAD .925, LAD .839, LCX .728, RCA .732. LCX/RCA default-threshold recall remains .420/.395. Exploratory research thresholds increase false positives; model probabilities and original weights were retained.

Brier error reduction from a training-only prevalence baseline is 53.9%, 35.2%, 13.5% and 14.2%. Intervals are conditional on fitted predictions. Local SHAP top-five factors overlap 75% on average after background changes; this measures sensitivity, not universal explanation reliability.

The cohort has 303 patients and no external clinical validation or longitudinal outcomes. Anatomy is generic and provides no lesion coordinates or stenosis severity. Independent target models can disagree. See `../docs/RELIABILITY_AUDIT.md` and the full model evidence.

## Still outstanding

- Actual 3-10 minute demonstration recording and judge-accessible YouTube upload.
- Submitter's team/author review, public repository/video links and competition submission.
- Docker execution and remote deployment have not been verified. The supplied task does not require a public deployment.

OpenAI Codex assisted implementation, investigation, testing and documentation. No generative model performs disease prediction or medical advice.
