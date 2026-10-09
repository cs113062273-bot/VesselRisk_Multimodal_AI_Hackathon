# VesselRisk current review snapshot

Updated 2026-10-09 (Asia/Taipei). This snapshot supersedes older review-package descriptions and test counts. It is a review package, not evidence that the competition entry or video has been published.

## Current deliverables

- Four frozen trained models and nested held-out evaluation; all target labels excluded from inputs.
- Horizontal Patient profile above a heart canvas, explanation and risk analytics. Four probabilities stay in synchronized explanation tabs.
- Real licensed coronary meshes, artery selection, rotate/zoom, X-ray, isolation and expanded view. Reference anatomy shows vessel-level probability.
- Calibrated-probability SHAP, three-model comparison, calibration evidence and Evidence Lab.
- Protocol-bound checkpoints and pre-deserialization checks for models, OOD, registry, evidence and schema.
- Frozen local explanation sensitivity audit: four predefined held-out profiles, four targets, seed/computation/background comparisons. Calibration group counts, descriptive intervals, training-prevalence baseline and separate-repeat metrics.
- Input origins tracked across cases, defaults, edits, imports and BMI calculation; exports snapshot origins with submitted values.
- Current ten desktop screenshots, six-page report, five-minute demonstration script, Devpost draft, license/data/model documentation, trained weights, sources and production build.

## Evidence and validation

Exact validation commands and outcomes are recorded in `BUILD_VALIDATION.json`. Archive contents and every file's size/hash are listed in `FILE_MANIFEST.json`; the archive also has a SHA-256 sidecar. The packaging script requires the reliability files and verifies the complete archive CRC and file hashes.

Use `python scripts/start.py --setup` on first installation; then `python scripts/start.py`. The included `.next` output is a Windows production build; rebuild through `--setup` in other environments. No inference credentials or retraining are needed.

## Scientific limits

Headline ROC-AUC is CAD .925, LAD .839, LCX .728, RCA .732. LCX/RCA default-threshold recall remains .420/.395. Exploratory research thresholds increase false positives; model probabilities and original weights were retained.

Brier error reduction from a training-only prevalence baseline is 53.9%, 35.2%, 13.5% and 14.2%. Intervals are conditional on fitted predictions. Local SHAP top-five factors overlap 75% on average after background changes; this measures sensitivity, not universal explanation reliability.

The cohort has 303 patients and no external clinical validation or longitudinal outcomes. Anatomy is generic and provides no lesion coordinates or stenosis severity. Independent target models can disagree. See `../docs/RELIABILITY_AUDIT.md` and the full model evidence.

## Still outstanding

- Actual 3-10 minute demonstration recording and judge-accessible YouTube upload.
- Submitter's team/author review, public repository/video links and competition submission.
- Docker execution and remote deployment have not been verified. The supplied task does not require a public deployment.

OpenAI Codex assisted implementation, investigation, testing and documentation. No generative model performs disease prediction or medical advice.
