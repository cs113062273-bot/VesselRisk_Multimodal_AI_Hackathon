# VesselRisk

VesselRisk estimates overall coronary artery disease (CAD) and stenosis in the LAD, LCX, and RCA from 55 clinical inputs. Results appear beside an interactive 3D heart, with the measurements that contributed to each prediction. **Model evidence** shows how the models were trained and tested.

This is a desktop research and education application. It is not a diagnosis, treatment recommendation, or substitute for diagnostic imaging.

![VesselRisk patient workspace](demo/screenshots/patient-workspace.png)

## Run locally

Install **Python 3.13** and **Node.js 24**, including npm. Trained models, the source workbook, and 3D assets are included. Running the application does not require a cloud account, API key, or retraining.

1. Download this repository as a ZIP and extract it, or clone it:

   ```powershell
   git clone https://github.com/cs113062273-bot/VesselRisk_Multimodal_AI_Hackathon.git
   cd VesselRisk_Multimodal_AI_Hackathon
   ```

2. Open a terminal in the folder containing this README. For the first launch, run:

   ```powershell
   python scripts/start.py --setup
   ```

   This creates `.venv`, installs the pinned Python and npm dependencies, builds the frontend, and starts both services. Installation needs internet access. Wait for API startup to finish and Next.js to report that it is ready.

3. Open **http://localhost:3000**. API documentation is at **http://127.0.0.1:8000/docs**.

4. Press **Ctrl+C** in the terminal to stop both services. For later launches, run:

   ```powershell
   python scripts/start.py
   ```

The launcher works on Windows, macOS, and Linux. Use `python3` if that is the name of your Python 3.13 command. If the default ports are occupied, run `python scripts/start.py --port 3001 --api-port 8001` and open http://localhost:3001.

## Try the application

- **Example prediction:** select an `Example(Optional)` profile and click **Predict coronary risk**. The example fills all 55 fields. Its displayed prediction uses a model trained without that patient.
- **Custom inputs:** edit the form or import [this synthetic profile](demo/CUSTOM_PROFILE_FINAL.json). Height and weight calculate BMI automatically. The profile is a software test case with no known clinical outcome; age 90 demonstrates the observed-range warning.
- **3D heart:** drag to rotate, scroll to zoom, or right-drag to pan. Select a vessel through its label, the dropdown, or a result tab. Orbit, X-ray, vessel isolation, anatomy guides, and an expanded view are available.
- **Explanation:** inspect the starting probability, signed SHAP contributions, input values, candidate model predictions, and variation across fitted models. After edits, the previous explanation is marked and export remains disabled until prediction runs again.
- **Model evidence:** compare all four targets, ROC/precision-recall/calibration curves, confusion matrices, calibration methods, thresholds, subgroup checks, failures, data provenance, and model hashes. These are fixed evaluation results; patient edits do not change them.
- **Export:** save patient results or model evidence as JSON. No patient database or external AI prediction service is used.

Vessel colors show estimated probability on reference anatomy. They do not show the location or severity of a blockage. Model ranges and unusual-profile warnings are descriptive checks, not clinical confidence intervals.

## Evaluation results

The supplied UCI workbook contains **303 patients and 55 input columns**. `Cath`, `LAD`, `LCX`, and `RCA` are excluded from every model's inputs. The original labels are retained, including one row with conflicting overall CAD and LAD labels.

Evaluation uses stratified **5-fold outer cross-validation, repeated twice**. Within each training fold, 3-fold selection compares logistic regression, random forest, and XGBoost. Preprocessing and sigmoid calibration use training data only. Each patient's two held-out probabilities are averaged before calculating the table below. The classification cutoff is 0.50.

| Target | ROC-AUC | Accuracy | Precision | Recall | F1 | Average precision | Brier |
|---|---:|---:|---:|---:|---:|---:|---:|
| CAD | 0.925 | 0.868 | 0.896 | 0.921 | 0.909 | 0.967 | 0.094 |
| LAD | 0.839 | 0.789 | 0.793 | 0.864 | 0.827 | 0.868 | 0.157 |
| LCX | 0.728 | 0.673 | 0.625 | 0.420 | 0.503 | 0.575 | 0.206 |
| RCA | 0.732 | 0.660 | 0.570 | 0.395 | 0.466 | 0.577 | 0.201 |

These are internal results from a small referral cohort, not external clinical validation. LCX and RCA miss many positive cases at 0.50. Threshold comparisons show the cost of increasing recall: more false positives. Bootstrap intervals in the app and report are conditional on the fitted predictions and exclude retraining and selection uncertainty. The evaluated selection procedure and the single model displayed for a patient are distinguished in the documentation.

## Documentation and source

- [Six-page technical report](report/VesselRisk-Track-A.pdf): data preparation, models, evaluation, explanations, 3D mapping, and usage.
- [Data and model card](docs/DATA_MODEL_CARD.md): labels, validation details, input handling, and limits.
- [Architecture](docs/ARCHITECTURE.md): the training, API, frontend, and 3D pipeline.
- [Explanation and calibration checks](docs/RELIABILITY_AUDIT.md) and [vessel/threshold experiment](docs/VESSEL_REFINEMENT.md).
- [Technical references](docs/RESEARCH.md) and [licenses and attribution](ATTRIBUTIONS.md).

The main code is in `ml/`, `api/`, and `web/`. Model weights and evaluation records are in `ml/artifacts/`; input definitions are in `data/data_dictionary/features.json`. Real BodyParts3D geometry and vessel mappings are in `web/public/anatomy/`. The API checks the source workbook and model hashes before loading the estimators.

## Reproduce and verify

After setup, use the project's Python environment:

```powershell
# Windows
.venv\Scripts\python -m ml.evaluate
.venv\Scripts\python -m pytest
```

On macOS/Linux, use `.venv/bin/python`. Evaluation checks frozen metrics and hashes. Tests cover target leakage, fold separation, predictions, input validation, and API behavior.

Frontend checks run from `web/`:

```powershell
npm run typecheck
npm run lint
npm run build
npx playwright install chromium
npx playwright test
```

Start the application before local browser tests. Tests use desktop Chromium with software-rendered WebGL. The CI workflow starts its own services.

Optional retraining uses `python -m ml.train` in the pinned environment. It replaces model/evaluation artifacts; refresh the dependent research evidence with `python -m ml.refine_vessels` and `python -m ml.reliability`, then restart the API. Retraining is not needed to try the included application. Rebuild the report with `python scripts/build_report.py`; capture current product screenshots with `node scripts/capture_review.mjs` while the application is running.

`python scripts/start.py --dev` starts development mode. Docker configuration is supplied through `compose.yaml`; container execution has not been verified on this Windows host.

## Attribution and AI assistance

Original code is MIT licensed. The UCI dataset and BodyParts3D anatomy retain CC BY 4.0 licenses; bundled fonts retain OFL licenses. See [ATTRIBUTIONS.md](ATTRIBUTIONS.md) for sources and modifications.

OpenAI Codex assisted research, implementation, debugging, tests, UI, and report drafting. Microsoft Edge TTS (`edge-tts`, Prabhat) generated the demo narration. The prediction service uses trained statistical models, not a generative AI model.
