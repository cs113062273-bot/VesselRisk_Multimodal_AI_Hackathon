# 1. CURRENT SCORE ESTIMATE

Audit date: 2026-10-02. Provisional strict estimate before changes: **88/100**, plausible judging range 84-92. This is reviewer judgment, not an official subscore formula or ranking prediction. The supplied `Track A.pdf`, especially pages 2-3, is the requirement authority.

| Official category | Estimate | Reason for deductions |
|---|---:|---|
| Predictive Performance | 24/30 | Strong internal methodology and CAD; modest LCX/RCA discrimination, low default recall, substantial sampling uncertainty |
| 3D Visualization | 23/25 | Real anatomy and complete interaction; static anterior indicator survives rotation; continuous legend misrepresents discrete colors |
| Clinical Interpretability | 17/20 | Correct probability attribution, but few permutation samples; single displayed model versus averaged headline metrics is easy to miss |
| System Integration | 14/15 | Complete native local workflow; exported bundle hash alone does not identify its selected estimator; startup does not check workbook pairing |
| Technical Implementation | 10/10 | Compact working architecture, pinned models, source, build and evidence; no architectural expansion justified |

The software-quality estimate does not waive required deliverables: a script is not the required 3-10 minute YouTube demonstration. Its absence is a submission-completeness risk, not a deduction that can be precisely quantified from the official PDF.

# 2. TRUE BOTTLENECKS

- LCX/RCA AUC .728/.732 and recall .420/.395 are genuine limitations. Lower thresholds reduce false negatives by raising false positives, not by improving ranking.
- The original and later searches reuse the same patients. Nested CV protects fold-level selection, but later outer-score-driven development is not independent confirmation. New split seeds would not create a fresh cohort.
- The headline aggregates two held-out probabilities per patient. The deployed and demonstration predictions use one fitted model. The difference is an estimand/presentation limitation, not discovered target leakage.
- Two local SHAP permutation cycles with 16/20 background rows give approximate attributions. Sum reconstruction does not establish convergence. The global rank stability statistic mixes patient, model and sampling differences; it is descriptive.
- Static orientation markers and a gradient legend can mislead during a good-looking 3D demo. Mesh IDs, artery grouping, licenses and generic-anatomy caveats are otherwise appropriate.
- Source regeneration resolves upstream `main`, despite a pinned delivered asset. API startup verifies model bundles but did not verify the workbook against them. Both can undermine reproduction without changing a single model coefficient.
- Mandatory video, actual repository/entry links and team attribution remain unfinished. Public hosting and Docker execution are not explicit requirements in the supplied PDF.

# 3. MODEL OPTIMIZATION VERDICT

**More consistent with B (limited data/target signal) than clear evidence of A (a correctable modeling failure), but a ceiling is not established.** This is a reasoned inference, not a measured Bayes error. See the primary-source comparison in `MODEL_OPTIMIZATION_RESEARCH.md` and the completed audit results in `FINAL_AUDIT_RESULTS.md`.

The earlier ExtraTrees/RBF-SVM rejection only rules out that small expansion under its procedure. It does not exhaust shrinkage, categorical boosting, nonlinear effects or safer probability objectives. One final eight-configuration investigation has expected value; repeated adaptive searching does not.

No forbidden targets were found in fitted predictors. Calibration and thresholds stay inside outer training partitions. The threshold inner predictions refit the already chosen specification: they exclude each inner-validation row from fitting/calibration, but not from the preceding outer-training specification selection. Outer evaluation still tests that complete threshold procedure; the inner threshold score is not an unbiased validation estimate.

# 4. PROPOSED EXPERIMENTS

One fixed batch, declared in `experiments/final_audit/protocol.json` before its results:

- Elastic net: four configurations covering strong shrinkage, sparse shrinkage and one balanced-weight comparison.
- HistGradientBoosting: two conservative leaf counts, fixed shrinkage and no validation-driven early stopping.
- CatBoost: two shallow ordered-boosting configurations with native categorical inputs; isolated dependency, no change to production requirements.

Use original six candidates plus the eight declared additions, identical stored outer splits, the original inner objective, and training-only fixed sigmoid calibration. Report every candidate's inner score, all fold selections, both repeats, pooled metrics and paired conditional intervals. No model, feature, calibration or cutoff is selected using outer results. No automatic promotion. CAD/LAD and research thresholds are not searched again. Negative experiments remain archived for reproducibility and are not integrated into the product.

# 5. MUST FIX BEFORE SUBMISSION

Correct the orientation/legend semantics, exported estimator identity, workbook pairing check and anatomy source pin. Clarify averaged evaluation versus the single displayed estimator. Keep the report, screenshots and review ZIP synchronized. Finish the real YouTube recording and final entry links/author review; do not describe these as completed.

# 6. HIGH-VALUE POLISH

Make the opening 20 seconds a timed prediction-to-artery-to-explanation interaction. Use measured outputs and readable screen zoom. Keep the threshold story short and show false positives beside sensitivity. Draft Devpost copy around inspectable anatomy and evidence, with AI disclosure in both README and Built With as required by the [event rules](https://multimodal-ai-hackathon-2026-7.devpost.com/rules).

The report already has six coherent pages. The title/tagline and existing hero composition work. Prior winners' public materials support a concrete workflow, architecture and demonstrable outputs as presentation strategy; they do not establish a winning feature count or a score threshold.

# 7. DO NOT TOUCH

Keep original production artifacts, default 0.50 classification, target exclusion, actual source labels, SHAP additivity, separately selectable vessels, local asset packaging, complete Evidence Lab and the product's current design. No replacement architecture, authentication, chatbot, cosmetic redesign or additional feature surface is warranted.
