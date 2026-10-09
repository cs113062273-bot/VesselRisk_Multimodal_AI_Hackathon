# Verification record

## Current delivery snapshot, 2026-10-09

The current reliability audit and complete inference integrity checks supersede the earlier counts and UI descriptions below. Current commands, outcomes, screenshot timestamps and extracted-package validation are recorded in `../review/BUILD_VALIDATION.json`. The project now targets desktop only. The six-page report, ten review captures and demonstration script have been synchronized with the current interface; removed outcome-reveal controls are not part of the demonstration. Earlier entries below are historical records.

## Model recheck, 2026-10-09

The deployed four model bundles, OOD artifact and original evaluation evidence match the final-audit fingerprints byte for byte. Recomputed OOF AUC remains CAD .9250, LAD .8388, LCX .7278 and RCA .7318. Training/inference target guards, repeated held-out split coverage, exported estimator identity and calibrated-probability SHAP reconstruction were rechecked.

The archived experiment verifier initially rejected the registry because the product rename changed only `version` from `cardiovision-1.0` to `vesselrisk-1.0`. Reversing that exact field replacement reproduces the historical SHA-256. The verifier now records that migration explicitly while retaining the original expected fingerprints; any additional registry-byte change or model change still fails. A regression check covers altered training counts, unknown versions and changed model bytes. The underlying prediction models were not refitted.

All 20 scientific/API tests pass. Replaying the 40 saved outer models reproduces all 2,424 per-repeat held-out predictions exactly (maximum absolute difference zero), and every saved SHAP background is an exact subset of its model's training data. The archived LCX/RCA audit also passes all 160 inner-trial, selection, split, metric and paired-interval checks after the explicit display-version migration.

## Final audit verification (supersedes earlier counts below)

On 2026-10-02, all **19** scientific/API checks pass, including exact exported fold-model identity and rejection of an unpaired workbook before unpickling. Frozen OOF/threshold metrics and original artifact hashes verify unchanged. Typecheck, ESLint and production build pass. The two existing desktop/mobile software-WebGL Playwright journeys pass in **15.6 seconds**, with real exported model-member checks. Ten review screenshots were recaptured with no browser errors. The updated app ran through the one-command launcher on dedicated review ports 3001/8001.

The final audit batch ran once in 430 seconds: eight new configurations, LCX/RCA, ten outer folds each, three-fold inner selection/calibration, no deployed model replacement. `python -m experiments.final_audit.verify` independently recomputes every saved inner score, selection, split partition, fold/repeat/pooled metric and paired interval. All 160 new inner trials verify. CatBoost stayed in a temporary isolated dependency path; production requirements are unchanged. Full before/after evidence: [FINAL_AUDIT_RESULTS.md](FINAL_AUDIT_RESULTS.md).

The report remains six pages and was rebuilt from current screenshots/evidence. Anatomy generation now uses the shipped immutable revision; binary geometry was not changed or redownloaded. The review package is regenerated with its per-file hash manifest and archive checksum. Docker execution, public hosting, video recording/upload and final competition submission are not claimed.

Verified locally on Windows on 2026-10-02. Checks focus on scientific validity and the real demo path rather than a coverage target.

## Scientific and API evidence

- `python -m ml.train`: completed the full four-target, 5-fold × 2-repeat nested evaluation and persisted final models, all fitted outer models, split indices and OOF predictions. Recorded training time: about 158 seconds on the build host.
- `python -m ml.evaluate`: independently recomputes the frozen OOF metrics and verifies source/model hashes; writes `experiments/metrics.csv`.
- `python -m pytest`: 15 critical checks pass. They cover target exclusion, actual source labels, fold partitions and repeated OOF coverage, metric reconstruction, artifact integrity, calibrated-probability SHAP reconstruction, held-out demo isolation, edited-case handling, invalid prediction inputs, critical API paths and real coronary geometry.
- Internal ROC-AUC: CAD 0.925, LAD 0.839, LCX 0.728, RCA 0.732. The final README/report show all metrics, intervals and low vessel recall. No external clinical validation was performed.

## Product and production checks

- Locked `npm ci`, TypeScript, ESLint and the optimized Next.js production build pass.
- First-run dependencies were installed in a fresh `.venv`; the final `python scripts/start.py --setup` completed dependency installation, locked npm installation, production build and startup at ports 3000/8000. `pip check`, all 15 scientific/API tests, independent OOF evaluation and both browser journeys passed using that isolated Python environment. SciPy/Numba/LLVM/thread-pool versions are pinned to the training environment. The test client's upstream AnyIO deprecation warning is harmless; there are no failing checks.
- Startup prepares the real held-out opening case's SHAP explanations before reporting readiness, avoiding the compiler's cold cost on the first interaction. Outputs remain computed from the shipped models; no demo constants substitute for prediction.
- Final production browser journeys: 2 passed in 12.9 seconds. A separate local HTTP check measured a 5 ms cached opening-case response through the frontend proxy. This is a local cached-response observation, not a general cold-inference or deployment latency claim.
- Two Playwright journeys pass against the real production frontend and FastAPI service: desktop prediction → 3D selection/X-ray/isolation → target explanation → recorded outcome → Evidence Lab → edited prediction → JSON export; mobile real prediction/3D/evidence without horizontal overflow.
- Browser checks use Chromium with software WebGL, without a dedicated GPU. The viewer reports measured live FPS; performance varies by host and no universal FPS guarantee is made.
- The in-app browser runtime reported no available browser. Verification therefore used local headless Playwright; it did not rely on a signed-in session.
- All screenshots in `demo/screenshots/` come from actual production predictions. Chart transitions are disabled so switching targets cannot temporarily display another target's curve.
- Custom-port production startup and the request-time API proxy were checked at ports 3001/8001. Unknown proxy paths are rejected; backend errors are surfaced.

## Submission artifact checks

- The generated report has exactly six A4 pages. Every page was rendered and visually reviewed; layout overflow checks also run during generation.
- Data/anatomy attribution, source hashes, source IDs and license modifications are included. The anatomy contains 63 actual source meshes and 37,444 triangles, not synthetic vessel curves.
- Four completed model bundles, evidence, registry and OOD artifact are shipped. Interrupted-training checkpoints and partial evidence are excluded from the final artifacts.
- The report, five-minute storyboard, model/data card, architecture, prior-winner research and submission checklist are present.

## Limits of verification

Final bounded refinement on the same date:

- ExtraTrees/RBF-SVM search completed in 65.7 seconds on the exact frozen LCX/RCA splits. Neither expanded policy passed its predeclared promotion gate; deployed artifacts and headline metrics remain unchanged.
- Training-only F1 points: LCX precision/recall/F1 .518/.840/.641, RCA .495/.868/.631. Independent evaluator verified all four policy/point variants per target and their source fingerprints. False positives and lower accuracy remain visible.
- 18 scientific/API checks pass, including pre-unpickle sklearn mismatch, nested threshold split isolation and metric reconstruction.
- Typecheck, ESLint and production build pass. Both real desktop/mobile journeys pass in 15.2 seconds, including the new research rows and mobile overflow.
- The mismatch CLI was exercised with a simulated sklearn 1.8.0: it exited with three plain lines naming required 1.7.1 and the setup command, without a pickle traceback.
- The final six-page report adds p2/p4 vector diagrams and concise text; the demo uses a product-first sequence with one consolidated clinical-limits segment. No unrelated functionality was added.

Docker Compose packaging is supplied, but Docker is not installed on this host, so container execution is unverified. No remote deployment, account-based competition submission or YouTube upload was performed. The submitter must review authorship/narrative, record the final demo, verify public links and submit the entry.
