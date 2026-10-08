# System architecture

```mermaid
flowchart LR
    Workbook[Supplied UCI workbook] --> Schema[Schema and leakage guard]
    Schema --> CV[Repeated nested stratified validation]
    CV --> LR[Logistic regression]
    CV --> RF[Random forest]
    CV --> XGB[XGBoost]
    LR --> Cal[Training-fold sigmoid calibration]
    RF --> Cal
    XGB --> Cal
    Cal --> Artifacts[Four models / folds / OOF evidence / registry]
    Artifacts --> API[FastAPI validated prediction service]
    Patient[55 clinical inputs] --> API
    API --> Predictions[CAD / LAD / LCX / RCA]
    API --> SHAP[Probability SHAP / agreement / OOD]
    Predictions --> Heart[Real BodyParts3D coronary meshes]
    SHAP --> Inspector[Target-specific explanation inspector]
    Artifacts --> Lab[Model Evidence Lab]
    API --> Export[Auditable local JSON export]
```

`ml/schema.py` owns source feature meaning and fail-closed leakage validation. `ml/modeling.py` owns fold-local pipelines, search, calibration and calibrated-probability SHAP. `ml/train.py` exports reproducible scientific evidence; checkpoint files are local intermediates and excluded from submission. `api/service.py` loads verified model artifacts and preserves held-out demo separation. `api/main.py` exposes the service through validated requests and documented endpoints.

Next.js serves the UI and proxies `/api/*` to FastAPI, avoiding browser CORS configuration. The heart renderer loads local geometry and independently colors/selects coronary branches. A projected label overlay follows the real artery mesh centroid through rotation. The patient form exposes all 55 columns; the initial view is a compact key-input subset with tabs for the rest. Edited inputs immediately mark existing results as stale; probability, heart and explanations update together only after a successful prediction.

The Evidence Lab reads the same evidence JSON used to generate the technical report. Model curves render without data interpolation animation, so a target switch cannot transiently display a scientifically misleading curve. Displayed performance is internal nested OOF evidence, distinct from deployed full-cohort model identity. Full SHA-256 values and feature dictionaries can be inspected/exported.

Anatomy source derivative is pinned to `ashemag/human-atlas` commit `1c38bf35c254a891200d3cedecfd57abebe83d8d`, itself from BodyParts3D 4.0. Exact mesh IDs, source names, changes and binary hash are in `web/public/anatomy/manifest.json`. Geometry remains anatomically sourced; no lesion position is fabricated.
