# Final bounded LCX/RCA refinement

One development pass on 2026-10-02. Original model files, registry and headline evidence remain byte-for-byte unchanged. CAD/LAD were not searched again.

## Research operating points

| Target / point | Accuracy | Precision | Recall | F1 | Confusion [[TN,FP],[FN,TP]] |
|---|---:|---:|---:|---:|---|
| LCX fixed 0.50 | .673 | .625 | .420 | .503 | [[154,30],[69,50]] |
| LCX training-selected F1 | .630 | .518 | .840 | .641 | [[91,93],[19,100]] |
| RCA fixed 0.50 | .660 | .570 | .395 | .466 | [[155,34],[69,45]] |
| RCA training-selected F1 | .617 | .495 | .868 | .631 | [[88,101],[15,99]] |

Same probabilities: AUC remains LCX .728 / RCA .732; Brier remains .206 / .201. Higher sensitivity/F1 costs precision, specificity and accuracy. This is an operating-point tradeoff, not improved discrimination or a validated clinical cutoff. The workspace keeps its fixed 0.50 convention; Evidence Lab presents both points side by side.

For each frozen outer fold, refit the selected calibrated pipeline in 3-fold inner CV on **outer train only**. Each threshold-tuning prediction excludes that inner-validation patient from base-estimator fitting and calibration. Choose F1 on the predeclared .15:.01:.75 grid; ties prefer precision, then the higher cutoff. No outer-test label enters threshold selection.

Each patient has two held-out model predictions and two training-selected cutoffs. Pool the mean probability-minus-cutoff margin; classify when it is nonnegative. This avoids ambiguous two-vote ties. Fold cutoffs: LCX .28-.37; RCA .19-.32. Separate full-cohort inner-selected research cutoffs are .34 / .30; these do **not** replace the patient-specific outer-evaluation cutoffs.

## Bounded family experiment: rejected

Added only two families, two configurations each, with the original fold-local preprocessing and class weighting:

- ExtraTrees: 160 trees, leaf 2/5, max_features .8, balanced.
- RBF SVM: C .3/3, gamma scale, balanced; its internal probability calibration stays inside training data, followed by the predeclared sigmoid calibration procedure.

The expanded policy uses the same training-only inner score, AUC - .25 x Brier, to select parameters and then family. Individual family comparisons are descriptive; no family is chosen using pooled outer-test scores.

| Policy / family | LCX AUC | RCA AUC |
|---|---:|---:|
| Frozen nested baseline | .727850 | .731830 |
| Expanded nested search | .722872 | .733222 |
| ExtraTrees (inner-tuned) | .697068 | .710526 |
| SVM RBF (inner-tuned) | .717711 | .718184 |

Predeclared promotion gate: +.01 paired AUC and no more than +.005 Brier. Neither target passes, so no new model is deployed. Research-threshold retention required +.03 F1, +.10 recall and precision >= max(.45, baseline precision - .15); both pass. Declaration and all trial/split/inner-OOF evidence are in `experiments/vessel_refinement/`.

Threshold values use training-only labels, but the retention gate itself uses pooled outer-test labels. Its result is a development audit, not independent confirmation or evidence of an optimal threshold. Evidence Lab presents every fixed/exploratory operating-point row equally, without using `retained_research_threshold` to highlight a winner. The workspace remains at 0.50.

## Scope and reproducibility

This is one bounded post-baseline experiment reusing the original outer splits. The development comparison is not an untouched independent confirmation. Do not turn this into another round of outer-score-driven model or cutoff search. There is still no external clinical validation.

```powershell
python -m ml.refine_vessels
python -m ml.evaluate
```

After a fresh `python -m ml.train`, rerun the refinement to pair it with the new artifact fingerprints. API hides stale refinement evidence; the evaluator/tests flag a stale pairing. The experiment took about 66 seconds on this host, does not add dependencies and does not overwrite frozen production artifacts.

Critical checks verify inner/outer isolation, coverage, training-only F1 selection, pooled metric reconstruction, preserved fingerprints and false-positive tradeoffs. Model startup separately checks scikit-learn against the registry before unpickling; mismatch guidance points to `python scripts/start.py --setup`.
