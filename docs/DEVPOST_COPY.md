# VesselRisk

**Four coronary estimates. Real anatomy. Evidence you can inspect.**

## Inspiration

A probability alone does not explain which coronary vessel it refers to, which measurements influenced it, or how much trust it deserves. VesselRisk connects those questions in one research workspace.

## What it does

Enter a clinical profile, predict overall CAD and LAD/LCX/RCA stenosis, then rotate and select real coronary anatomy to inspect each estimate. The selected artery stays linked to its patient's measurements and signed SHAP contributions. Evidence Lab exposes validation, calibration, model comparisons, weak results, and held-out failures.

## How we built it

The supplied 303-patient workbook provides 55 eligible inputs. A programmatic guard blocks all four target columns during training and inference. Models are compared with 5-fold outer cross-validation repeated twice and training-only inner selection and calibration. A typed FastAPI service connects the trained models to Next.js and React Three Fiber. Local BodyParts3D assets preserve the source identity of independently selectable coronary branches.

## What we measured

Internal repeat-averaged nested OOF ROC-AUC is 0.925 for CAD, 0.839 for LAD, 0.728 for LCX and 0.732 for RCA. The vessel models have weaker recall at the fixed 0.50 research threshold. Exploratory training-selected thresholds increase sensitivity with substantially more false positives; they do not improve AUC or establish clinical operating points. Full metrics and methods are included in the six-page report and Evidence Lab.

## What makes the work inspectable

Every local explanation reconstructs the displayed calibrated probability. A frozen-model audit quantifies local SHAP sensitivity to seed, computation and training background on four predefined held-out profiles; it does not claim universal explanation stability. Calibration evidence includes group counts, descriptive intervals, a training-prevalence baseline and separate-repeat performance. Exports identify the exact estimator and each input's origin. Checkpoints bind to the training protocol, and the API verifies models, OOD and evidence before deserialization. Held-out demonstration models exclude the displayed patient. Source labels, including one contradictory record, remain unchanged. Split indices, model weights, reproducible commands, licensing and failure examples ship with the application.

## Limits and next steps

This is research and education software, not diagnosis, treatment advice or a replacement for diagnostic imaging. There is no external clinical validation. The 3D model is reference anatomy, with vessel-level probability rather than patient-specific lesions. The next scientific step is independent validation, not further tuning against already inspected outer results.

## Built With

Python, scikit-learn, XGBoost, SHAP, FastAPI, TypeScript, Next.js, React, React Three Fiber, Three.js, BodyParts3D, OpenAI Codex.

OpenAI Codex assisted research, implementation, debugging, verification and drafting. The application does not use a generative model for disease prediction or medical advice. The submitter is responsible for reviewing and explaining the code.

## Entry preparation (not public project copy)

- Use `demo/screenshots/patient-workspace.png` as the hero; follow it with the isolated coronary view and Evidence Lab.
- Add the actual public source repository link, team/author names and a judge-accessible 3-10 minute YouTube demo. These are not available in this workspace and must not be invented.
- Describe the final isolated model investigation from `docs/FINAL_AUDIT_RESULTS.md` only after reviewing its completed results. CatBoost is an audit-only dependency, not a deployed classifier.
- The local application is ready to demonstrate. A public deployment is optional under the supplied Track A PDF; the demonstration video is a required deliverable.
