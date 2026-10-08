# VesselRisk final audit results

Completed 2026-10-02. **Keep the deployed models.** The final bounded nested search did not demonstrate a material, consistent improvement. The high-confidence product/provenance fixes are implemented and verified. No claim of a dataset ceiling, independent confirmation or clinical validation is justified.

## Before / after deployed results

All original classifier bundles, OOD artifact, registry and headline evidence remain byte-for-byte unchanged. Predictions, SHAP computation and the workspace threshold remain unchanged.

| Target | AUC before = after | Recall before = after | F1 before = after | Brier before = after |
|---|---:|---:|---:|---:|
| CAD | .9250 | .9213 | .9087 | .0943 |
| LAD | .8388 | .8644 | .8270 | .1573 |
| LCX | .7278 | .4202 | .5025 | .2064 |
| RCA | .7318 | .3947 | .4663 | .2014 |

The pre-existing research thresholds also remain unchanged: LCX recall/F1 .840/.641, RCA .868/.631, with false positives 93/101 versus 30/34 at 0.50. They are not new model improvements from this audit.

## Final bounded experiment: complete outcome

**These are archived research results, not deployed changes.** All metrics below use threshold 0.50; probability ranking and calibration are evaluated separately.

| Target / policy | AUC | Accuracy | Precision | Recall | F1 | AP | Brier |
|---|---:|---:|---:|---:|---:|---:|---:|
| LCX frozen baseline | .727850 | .673267 | .625000 | .420168 | .502513 | .574641 | .206423 |
| LCX expanded inner selection | .731092 | .693069 | .647727 | .478992 | .550725 | .591236 | .203713 |
| RCA frozen baseline | .731830 | .660066 | .569620 | .394737 | .466321 | .576796 | .201354 |
| RCA expanded inner selection | .732711 | .646865 | .542169 | .394737 | .456853 | .591928 | .200552 |

| Target | AUC delta [95% conditional paired interval] | Brier delta [95% conditional paired interval] | AUC / Brier improving folds |
|---|---|---|---|
| LCX | +.003243 [-.015255, +.021883] | -.002710 [-.008248, +.002398] | 5/10 / 5/10 |
| RCA | +.000882 [-.016616, +.020004] | -.000802 [-.006111, +.004215] | 2/10 / 4/10 |

Predeclared opportunity criterion: AUC +.02 with no more than .005 Brier regression and improvement on at least 7/10 folds; or Brier -.01 with no more than .005 AUC regression and improvement on at least 7/10 folds. **Neither target passes.** This is a descriptive opportunity flag, not an inferential test or deployment gate. Intervals straddle zero; failure to show improvement is not proof of equivalence.

LCX F1 improved .0482 and recall .0588 in the research policy, worth reporting, but discrimination gain is small and fold consistency insufficient. RCA accuracy, precision and F1 regressed; its recall did not change. The original production system suffers none of these regressions because no experimental estimator was promoted.

All secondary family results are retained, without picking a winner:

| Inner-tuned family | LCX AUC / Brier | RCA AUC / Brier |
|---|---|---|
| Elastic net | .724790 / .206519 | .747888 / .195777 |
| HistGradientBoosting | .714103 / .209497 | .743201 / .197791 |
| CatBoost | .726891 / .206583 | .733129 / .202187 |

RCA elastic net is a plausible future lead: delta AUC +.0161, paired conditional interval [-.0061, +.0386]; delta Brier -.0056, interval [-.0121, +.0009]. Those are secondary, unadjusted comparisons on reused patients. Replacing the selected policy with this family after seeing the table would be outer-score-based selection. No such replacement was made. CatBoost's categorical handling did not uncover a clear missing source of vessel signal.

Repeat AUCs underline the aggregation distinction:

| Target / policy | Repeat 1 | Repeat 2 | Mean-probability pooled AUC |
|---|---:|---:|---:|
| LCX baseline | .709308 | .723191 | .727850 |
| LCX expanded | .715062 | .724470 | .731092 |
| RCA baseline | .722315 | .726074 | .731830 |
| RCA expanded | .724728 | .723939 | .732711 |

The fold-trained prevalence reference has Brier .238510 for LCX and .234698 for RCA. Thus the existing models contain useful predictive information, even though vessel discrimination is modest. Pooled AUC of fold-varying constant prevalence predictions need not equal .50; it is not interpreted as a useful ranking model.

## Exact protocol and scope

1. Freeze protocol and runner; record SHA-256 of every original artifact before fitting. Preserve the original 303 rows, 55 predictors and target labels. CAD/LAD are not retrained.
2. Reuse each target's exact stored five outer folds, repeated twice (seed 2026). Each patient receives one held-out prediction per repeat.
3. Within each outer training partition, run three-fold stratified CV with seed 2026 + fold index. Add eight predeclared configurations to the original six: four elastic nets, two conservative histogram boosters, two shallow ordered CatBoost fits. All preprocessing and CatBoost categorical target statistics are fit inside the appropriate training partition.
4. Rank by the unchanged **raw inner OOF AUC - .25 x Brier** objective. Select family/parameters only from training labels. Fit fixed sigmoid calibration with three folds inside outer training, `ensemble=False`. No external early-stopping set, feature search, new threshold or calibration search.
5. Use frozen original trials/fits as the equivalent baseline; their reproduced predictions match saved OOF to 1e-12. Compute the expanded policy and each inner-tuned new family on outer test patients. Do not feed these scores back into the search.
6. Average each patient's two probabilities, compute all required classification metrics/AP/Brier, and also report separate repeats and folds. Compute 2,000 paired, patient-stratified bootstrap resamples using seed 2026.
7. Bootstrap intervals are conditional on fixed fitted predictions, omit retraining/development-selection uncertainty, and involve predictions from overlapping training folds. Secondary comparisons are unadjusted for multiplicity. No independent-fold t-test or external-validity claim is made.
8. Stop after the declared batch. No follow-up grid, seed hunt, outcome-selected blend or promotion. Retain only the reproducible research archive, not candidate weights or production dependencies.

Runtime: 430 seconds on this host. No inner convergence warnings. Expanded policy choices: LCX elastic net 6, XGBoost 2, CatBoost 1, histogram boosting 1; RCA elastic net 5, logistic 3, XGBoost 2. The independent verifier recomputes all 160 new trial scores, selection decisions, split coverage, fold/repeat/pooled metrics and intervals from saved evidence.

## Implemented fixes and evidence

| Improvement | Before | After | Validation / limitation |
|---|---|---|---|
| Dataset pairing | Startup could accept another same-shaped workbook | Hash checked against registry and evidence before unpickling | Changed-workbook regression check passes |
| Prediction identity | Bundle hash only | Artifact filename, exact member, training count and ordered-index hash exported | API reconstruction and real browser export checked |
| Evaluation clarity | Family label could be read as the source of headline metrics | Full-cohort label explicit; workspace distinguishes one model from averaged OOF | Desktop/mobile captures and six-page report verified |
| Anatomical orientation | Static anterior/left/right markers after orbit | Explicit **reset view** label; no false live orientation axes | Production browser capture reviewed |
| Color mapping | Continuous legend over three discrete colors | Three actual probability display bands | Browser journey and screenshot reviewed; no new clinical categories |
| Anatomy regeneration | Fetch latest upstream revision | Use the shipped immutable commit | Source pin equals manifest; existing mesh hashes remain unchanged; network regeneration not repeated |
| Submission presentation | Opening had no second-by-second cue; no entry copy | Timed 20-second opening and truthful Devpost draft | Script reviewed; final human recording still required |

These are integration, interpretability and reproducibility improvements, so they do not require or claim a new nested performance result. The only model change candidate was evaluated fairly within the declared nested procedure and **did not survive the materiality criteria**.

## Validation and changed files

- 19 scientific/API pytest checks pass; only the existing upstream AnyIO deprecation warning remains.
- `python -m ml.evaluate` reconstructs every original headline/threshold result and verifies frozen fingerprints.
- `python -m experiments.final_audit.verify` independently reconstructs the archived experiment.
- TypeScript, lint and production build pass. Both real Playwright journeys pass (15.6 seconds), including desktop/mobile, software WebGL, vessel routing, edits, threshold evidence and exact-model export.
- Ten review screenshots recaptured from production; no browser errors. Report rebuilt at six pages and visually checked. ZIP regenerated and verified by CRC, per-file hashes and required-file checks.

Source edits: `api/service.py`, `api/schemas.py`, `scripts/prepare_anatomy.py`, `tests/test_validity.py`, `web/lib/types.ts`, `web/components/HeartViewer.tsx`, `web/components/ExplanationPanel.tsx`, `web/components/EvidenceLab.tsx`, `web/app/contrast.css`, `web/e2e/demo.spec.ts`, `scripts/build_report.py`, `scripts/package_review.py`.

Documentation: `README.md`, `demo/DEMO_SCRIPT.md`, `docs/DATA_MODEL_CARD.md`, `docs/RESEARCH.md`, `docs/VERIFICATION.md`, `docs/SUBMISSION_CHECKLIST.md`, `review/START_HERE.md`, `review/COMPLETION_SUMMARY.md`; new `docs/FINAL_AUDIT.md`, this result file, `docs/MODEL_OPTIMIZATION_RESEARCH.md`, `docs/DEVPOST_COPY.md`, and `experiments/final_audit/`.

Generated deliverables: refreshed report, demo/review screenshots, review hub/manifest and submission ZIP/checksum. Original model artifacts and headline numerical evidence are unchanged. The workspace has no Git metadata; the pre-edit source snapshot and file hashes are preserved under `tmp/final-audit/` for local comparison, excluded from submission.

## Final score estimate and why not 100

**Approximately 91/100 for the reviewable software/evidence package**: Prediction 24/30, 3D 24/25, Interpretability 18/20, Integration 15/15, Technical 10/10. A reasonable subjective range is 87-94; the official rubric supplies weights, not a formula mapping AUC to points. Do not treat three estimated points as an empirical result or a competition ranking.

LCX/RCA remain only moderately discriminative; their default recall is weak. The evidence comes from 303 referral patients, not independent validation. Approximate SHAP, coarse/reference anatomy, a compact UI that needs readable recording zoom, and unvalidated uncertainty/OOD heuristics can still cost points. A better-performing rigorously evaluated rival could win. Native production and software WebGL were exercised; Docker execution remains unverified.

**Submission completeness remains separate:** team/author review, an actual public repository/entry link and the required judge-accessible 3-10 minute YouTube recording are outstanding. No public deployment, upload or submission was performed. The recording is the highest-value remaining competition task.

**A versus B:** after this batch, B remains the better working explanation for most of the LCX limitation; RCA shows some unconfirmed shrinkage headroom. Neither .728 nor .732 is a demonstrated ceiling. The credible next scientific step is independent validation of a frozen hypothesis, not more adaptive tuning on these outer results. See `MODEL_OPTIMIZATION_RESEARCH.md` for the sourced literature comparison.
