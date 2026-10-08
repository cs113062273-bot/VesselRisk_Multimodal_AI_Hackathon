# CODEX MASTER BRIEF — Multimodal AI Hackathon 2026 / Track A

## Mission

You are the primary implementation agent for a solo submission to **Multimodal AI Hackathon 2026 — Track A: Cardiovascular Risk Visualization & Prediction**.

The goal is **not** to produce a prototype, scaffold, proof-of-concept, or half-finished demo. Build the project end-to-end to a **submission-ready, polished, reproducible competition entry** that only needs final human review and visual/text refinement.

Optimize for the official judging rubric and aim for **Track A winner-level quality**.

You are allowed to use the internet for research and downloads. If you do not know how to implement something, **research it yourself first**, prioritizing official documentation, primary sources, published papers, and the original source of any asset/library. Do not stop merely because a package, 3D asset, modeling technique, deployment step, or evaluation method is unfamiliar.

Do not ask the user routine implementation questions that you can resolve yourself. Make a defensible engineering choice, document it, test it, and continue. Ask only if blocked by something that truly requires the user, such as credentials, inaccessible private resources, or a consequential ambiguity that cannot be resolved from the provided materials or authoritative sources.

---

## Supplied materials

Read all of these before changing or generating code:

1. **`Track A (1).pdf`** — official Track A specification. This is the highest-priority source of truth.
2. **`extention of Z-Alizadeh sani dataset.xlsx`** — the supplied/public UCI dataset to use as the primary dataset.
3. **The supplied VesselRisk architecture/design image** — follow its architecture, product structure, UX direction, and quality bar closely.
4. **`instruction(1).md`** — detailed strategy and implementation expectations.

If sources conflict, use this priority:

**Official Track A PDF > actual dataset > architecture/design image > instruction document > your implementation judgment.**

Do not silently reinterpret the official task.

---

## Competition background

Track A challenge:

> Build an interactive 3D visualization system that predicts coronary artery disease and overall cardiac risk from patient physiological and clinical data, mapping predictions onto an interactive 3D human anatomical model.

The official judging weights are:

- **Predictive Performance — 30%**
- **3D Visualization — 25%**
- **Clinical Interpretability — 20%**
- **System Integration — 15%**
- **Technical Implementation — 10%**

Every major implementation choice should map back to one or more of these scoring categories.

The project should look and behave like a credible finished product, not a hackathon toy.

---

## Primary data and labels

Inspect the provided XLSX yourself and build a formal data dictionary.

The workbook contains **303 patient records and 59 columns**. The relevant target columns are:

- `Cath` → overall CAD label (`CAD` / `Normal`)
- `LAD` → LAD stenosis label
- `LCX` → LCX stenosis label
- `RCA` → RCA stenosis label

### Hard leakage rule

The official problem statement explicitly requires:

**`LAD`, `LCX`, `RCA`, and `Cath` must NEVER be input features for any of the CAD/vessel prediction models.**

Implement a programmatic **LeakageGuard** that fails loudly if any forbidden target field enters preprocessing, feature selection, training, inference, or evaluation.

Do not rely on a manually maintained column list alone; add tests.

Do not manufacture anatomical lesion locations. The dataset supports **vessel-level risk prediction**, not pixel-level or point-level lesion localization.

---

## Required ML system

Build four defensible classification tasks:

1. Overall CAD
2. LAD stenosis
3. LCX stenosis
4. RCA stenosis

At minimum implement and compare:

- Logistic Regression as a transparent baseline
- Random Forest
- XGBoost and/or LightGBM
- Another suitable tabular baseline only if it adds value

Use a statistically defensible validation strategy for the small dataset.

### Non-negotiable ML quality requirements

- All preprocessing occurs **inside training folds**
- Any class balancing / class weights / resampling occurs **inside training folds only**
- Hyperparameter tuning must not leak validation/test information
- Report at least:
  - Accuracy
  - Precision
  - Recall
  - F1
  - ROC-AUC
- Also add where meaningful:
  - PR-AUC
  - Brier score
  - calibration curves
  - confusion matrices
  - confidence intervals / repeated-fold dispersion
- Compare probability calibration approaches when justified
- Produce per-target model selection evidence
- Persist exact model artifacts, metadata, feature schema, library versions, random seed, training configuration, and model hash/version
- Create reproducible scripts, not notebook-only logic

Prefer an honest, rigorous result over an implausibly high score.

### Advanced winner-level evaluation

Where statistically meaningful, include:

- repeated and/or nested stratified cross-validation
- ablation experiments
- leakage audit experiment
- model agreement / disagreement
- uncertainty estimation
- simple out-of-distribution warning
- subgroup / robustness analysis
- failure-case review
- SHAP stability or explanation consistency analysis

Do not claim causal effects from observational feature attribution.

---

## Interpretability

Build both:

- **Global explanations**
- **Patient-level local explanations**

Use SHAP or another defensible technique.

For every CAD/LAD/LCX/RCA prediction, the interface should be able to answer:

- What is the predicted risk/probability?
- How well calibrated is the relevant model?
- Which features contributed most?
- Which direction did they move the model output?
- How much do candidate models agree?
- Is confidence limited?
- Is this patient profile poorly represented by the training data?

Explanations must be clearly framed as **model explanations, not clinical causality**.

Never present treatment advice.

---

## 3D visualization

The 3D experience is a core scoring component, not decoration.

You may download and use an appropriate open-source anatomical model.

Officially acceptable source directions include:

- **BodyParts3D / Database Center for Life Science**
- open-source `.gltf`, `.glb`, or `.obj` heart models
- NIH 3D Print Exchange
- suitable Three.js repositories
- Sketchfab only when licensing clearly permits the intended use

You have explicit permission from the user to download the required 3D assets.

### Asset requirements

Prefer a model in which **LAD, LCX, and RCA can be independently selected and visually controlled**.

If the best available model is not already segmented into those vessels, preprocess it as needed using legitimate tooling such as Blender, mesh conversion tools, or programmatic geometry processing.

Record the exact source, author/license, modifications, and attribution requirements.

### Required interactions

- smooth rotate
- zoom
- pan if useful
- select LAD / LCX / RCA
- dynamically map predicted vessel risk to the corresponding anatomical structure
- update visual state in real time after a new patient prediction
- clicking a vessel opens the matching prediction, uncertainty, and explanation
- do not falsely display a precise lesion location that the dataset does not provide

Use a browser-friendly stack such as **React Three Fiber / Three.js** unless a clearly better choice is justified.

The final app must remain responsive on a normal modern browser without requiring a dedicated GPU.

---

## Web product

Build a polished, coherent web application.

Preferred stack unless evidence suggests otherwise:

- **Frontend:** Next.js + TypeScript
- **3D:** React Three Fiber / Three.js
- **Backend:** FastAPI + Pydantic
- **ML:** Python, scikit-learn, XGBoost/LightGBM, SHAP
- **Charts:** a production-quality React charting library
- **Packaging:** Docker / docker compose

Core screens:

### 1. Patient-Level Dashboard
- clean patient data entry or selectable sample cases
- overall CAD result
- LAD / LCX / RCA probabilities
- interactive 3D heart
- vessel selection
- SHAP explanation
- confidence / uncertainty
- model agreement
- explicit clinical safety disclaimer

### 2. Model Evidence Lab
This is designed for judges and must be excellent.

Show:

**Data**
- dataset provenance
- 303-patient summary
- class distributions
- schema
- forbidden-feature/leakage audit

**Models**
- selected model per target
- baseline comparisons
- hyperparameters
- model version/hash

**Validation**
- ROC
- PR
- confusion matrices
- calibration curves
- Brier score
- cross-validation summary
- dispersion / intervals where appropriate

**Robustness**
- model disagreement
- OOD / low-confidence cases
- subgroup checks where statistically defensible
- failure cases

**Explainability**
- global SHAP
- local SHAP
- explanation stability if available

The application must expose the evidence behind its claims instead of merely displaying a risk number.

---

## Backend/API

Build a typed, testable model service, for example:

- `POST /predict`
- `POST /explain`
- `GET /model-info`
- `GET /health`

A prediction request should return enough structured information for the UI to render:

- CAD/LAD/LCX/RCA probabilities
- class labels
- calibrated confidence information
- model identifiers
- explanation data
- uncertainty/model-agreement data
- warnings/OOD flag if applicable

Do not couple the frontend to ad-hoc notebook output.

---

## Reproducibility and engineering quality

The repository must be clean enough for judges to clone and understand.

Aim for a structure similar to:

```text
vesselrisk/
├── data/
│   ├── raw/
│   ├── processed/
│   └── data_dictionary/
├── ml/
│   ├── schema/
│   ├── leakage_guard/
│   ├── preprocessing/
│   ├── training/
│   ├── calibration/
│   ├── evaluation/
│   ├── explainability/
│   ├── uncertainty/
│   └── artifacts/
├── api/
├── web/
├── assets/
│   └── anatomy/
├── experiments/
├── tests/
├── docs/
├── report/
└── demo/
```

Deliver:

- one-command local startup where practical
- pinned environment / lock files
- deterministic seeds
- automated tests
- leakage tests
- API tests
- frontend smoke tests where practical
- lint/type checking
- CI configuration
- Docker setup
- clean README
- architecture documentation
- data card
- model card(s)
- license/attribution file
- known limitations
- failure modes
- reproducible training command
- reproducible evaluation command

Do not leave broken scripts, dead routes, unused scaffolding, TODO placeholders, fake metrics, or hard-coded demo-only outputs.

---

## Official deliverables

The final repository should make it straightforward to produce all official deliverables:

1. **Working web software prototype**
2. **Trained prediction pipeline and model artifacts**
3. **Clinical explanation dashboard**
4. **Project documentation, max 6 pages**
5. **3–10 minute YouTube demonstration video**

Also prepare:

- a strong README
- a 6-page report draft or report-ready content
- a demo script/storyboard
- key screenshots
- architecture diagram source if practical
- final submission checklist
- concise AI-tool disclosure for the README/Built With section

---

## Demo quality bar

The opening demo should immediately show the product.

Suggested flow:

1. Select or enter a patient
2. Run prediction
3. Display overall CAD + LAD + LCX + RCA
4. Update the 3D heart instantly
5. Click LAD/LCX/RCA
6. Show that vessel's calibrated probability, SHAP explanation, model agreement, and confidence
7. Open Model Evidence Lab
8. Show validation, calibration, leakage protection, and reproducibility evidence

Do not begin the demo with a long technology-stack explanation.

---

## Safety / scientific integrity

The UI must clearly state that the system is:

- for research / education / decision support
- not a clinical diagnosis
- not a substitute for formal diagnostic imaging
- not treatment advice

Never imply precise lesion localization from this dataset.

Never fake metrics, confidence, or evaluation output.

Never claim external clinical validation unless it was actually performed.

---

## What NOT to prioritize

Unless the official requirements change, do not waste time on low-scoring distractions such as:

- generic LLM chatbot
- voice assistant
- authentication/account system
- social features
- hospital database integration
- automatic medical diagnosis text
- raw ECG waveform modeling
- CT/MRI segmentation
- unrelated generative-AI features

A smaller number of deeply validated features is preferable to feature bloat.

---

## Autonomous execution behavior

Work continuously toward a submission-ready repository.

At the start:

1. Read every supplied file.
2. Inspect the XLSX schema and class distributions.
3. Audit the existing workspace.
4. Create/update a concrete execution plan.
5. Identify external assets/libraries that must be researched or downloaded.
6. Begin implementation.

During development:

- run code instead of assuming it works
- run tests after meaningful changes
- inspect actual outputs
- fix failures before moving on
- use web research when blocked or uncertain
- prefer authoritative sources
- verify licenses
- document decisions
- keep the project runnable
- periodically re-check the official rubric and the supplied design image
- improve weak scoring areas rather than adding random features

Do not stop at "the code is written." Continue until the complete system is tested end-to-end.

When something fails, debug it.

When a library choice is poor, replace it.

When the 3D asset is unsuitable, find or prepare a better one.

When model results are unstable, investigate and report the instability honestly.

When a feature would undermine scientific validity, do not implement it merely for visual effect.

---

## Definition of done

The project is not done until all of the following are true:

- Training runs successfully from the provided dataset
- Leakage tests pass
- CAD/LAD/LCX/RCA models are evaluated and persisted
- The selected probability outputs are appropriately calibrated or the reason not to calibrate is documented
- Explainability works for real predictions
- 3D LAD/LCX/RCA mapping works interactively
- New patient input updates model output + 3D + explanation end-to-end
- Model Evidence Lab shows real evaluation artifacts
- No fake/sample metrics remain in production UI
- Required safety disclaimer is visible
- The app runs from documented commands on a clean environment
- Tests/type checks/lint pass or remaining exceptions are explicitly justified
- README and technical documentation are complete
- Model/data/license attribution is complete
- A max-6-page report draft or report-ready content exists
- A 3–10 minute demo script/storyboard exists
- The repository is coherent enough to submit as-is after human polish

The final standard is:

> **A trustworthy, leakage-audited, calibrated, uncertainty-aware, anatomically mapped CAD risk visualization system whose claims are traceable to real validation evidence.**

Build toward that standard. Do not settle for a scaffold.
