# Can LCX/RCA materially improve?

Reviewed 2026-10-02. Separate official constraints, published claims and inference. This is a focused primary-source review, not a systematic review or proof of an achievable ceiling.

## Official task and source data

The supplied Track A PDF excludes LAD, LCX, RCA and Cath from **every** predictor. We follow that stronger rule regardless of wording on dataset websites. The actual workbook has 303 rows and 55 eligible inputs. The [UCI extension](https://archive.ics.uci.edu/dataset/411/extention+of+z+alizadeh+sani+dataset) supports CAD and individual-vessel tasks; it does not supply external validation or lesion coordinates. No additional patient cohort was substituted or merged.

## Published comparisons and their limits

| Primary study | Published result | Relevance and why it is not a like-for-like benchmark |
|---|---|---|
| [Alizadehsani et al., 2020, Expert Systems, DOI 10.1111/exsy.12573](https://www.iitis.pl/sites/default/files/pubs/Alizadehsani2020Hybrid.pdf) | Table 7: LAD/LCX/RCA best accuracy 86.64/83.47/82.85%; LCX sensitivity/specificity 90.96/75.22%; RCA 87.01/74.60% | Same 303-patient class counts (177/119/114); strongest nearby comparison. Reports accuracy, not ROC-AUC or calibration. |
| [Alizadehsani et al., 2018, CMPB, DOI 10.1016/j.cmpb.2018.05.009](https://www.sciencedirect.com/science/article/abs/pii/S0169260717314189) | CAD accuracy 96.40%, sensitivity 100%, specificity 88.1% | Abstract describes 500 patients, not this 303-row workbook, and overall CAD after combining vessel predictions. Not a vessel-AUC comparator. |
| [Khozeimeh et al., 2023, ALEC, DOI 10.1016/j.compbiomed.2023.106841](https://www.sciencedirect.com/science/article/pii/S0010482523003062) | 97.01% CAD accuracy with active learning/SVM | A label-query/pseudo-labeling method and overall CAD endpoint. Cannot transfer its number to fully supervised nested LCX/RCA ROC-AUC. |

**2020 methodological reading:** Sections 3.4 and 3.4.2 describe clinical discretization, 10-fold validation, training-based feature ranking, a validation-selected assurance threshold and genetic SVM optimization. The inspected text does not unambiguously establish a separate outer evaluation protecting all those decisions. We therefore cannot treat its best-of-search table as equivalent to repeated nested evaluation. This is uncertainty about comparability, not proof of misconduct or target leakage. The study itself finds stronger feature signal for LAD than LCX/RCA. Its feature thresholds/selection were not copied as though they were independent prior knowledge: that paper studied the same patients.

**ALEC qualification:** Its [open full text](https://digibug.ugr.es/bitstream/10481/81916/1/1-s2.0-S0010482523003062-main.pdf) also describes exploratory plots using other vessel labels as features. Such plots would violate this challenge if turned into predictors; this observation is not an allegation that every reported classifier used those features. The different evaluation task is enough to rule out a direct numerical comparison.

## What the existing evidence actually says

The frozen models span regularized linear, bagged-tree and boosted-tree estimators; a previous bounded ExtraTrees/RBF-SVM expansion did not materially improve the nested policy. LCX/RCA fold-AUC SDs are both about .058, and the conditional pooled intervals are wide. Their lower prevalence also means approximately 91-95 positive training examples per outer fold, before inner fitting/calibration reduces the fit sample further. These facts support caution about flexible searches.

Fixed sigmoid calibration is defensible for a small cohort, but does not guarantee improvement. LCX Brier is .2062 raw versus .2064 sigmoid, a slight regression; RCA improves .2048 to .2014. Changing calibration after reading outer comparisons would select on those results. [Scikit-learn calibration guidance](https://scikit-learn.org/1.7/modules/calibration.html) explains fold separation and small-sample overfitting concerns. The existing threshold tradeoff follows the distinction between probability estimation and decision policy described in [threshold guidance](https://scikit-learn.org/1.7/modules/classification_threshold.html).

## Why this final experiment is bounded as it is

Elastic net probes an actual gap in the original two-C L2 search: stronger and partly sparse shrinkage, with/without balanced weighting. Shallow boosting probes conservative nonlinear fits. [CatBoost's original paper](https://proceedings.neurips.cc/paper/2018/hash/14491b756b3a51daac41c24863285549-Abstract.html) motivates ordered boosting and training-only categorical statistics; it does not promise gains here. Most categorical fields are low cardinality, so its advantage over one-hot encoding may be small. [Scikit-learn's ensemble documentation](https://scikit-learn.org/1.7/modules/ensemble.html) explicitly cautions that histogram binning is not always advantageous on small datasets.

The expanded policy competes all declared candidates **inside each training fold**, preserving the baseline objective. It is not an outer-AUC contest between families. A gain on reused patients remains development evidence. [Cawley and Talbot, JMLR 2010](https://jmlr.org/papers/v11/cawley10a.html) explain why overfitting the selection criterion can rival algorithm differences. No new seed or nominal split can remove previous researcher exposure to this cohort.

No feature-group search, PCA, hard discretization, synthetic data, post-hoc calibration selection, stacking or target-derived features are added. These enlarge the search, discard information, or require more cross-fitting than the evidence currently justifies. Correlated-target learning can be leakage-safe in principle if every auxiliary prediction and model-selection step is nested; actual labels or in-sample auxiliary predictions cannot be used. It is not an established route to better vessel signal here. Fixed-shape interactions remain a future hypothesis, not a proven improvement.

## Prior-winner evidence versus presentation strategy

The [organizer announcement](https://www.linkedin.com/posts/ihubiitmandi_multimodalai-hackathon-iitmandi-activity-7406989681428656128-irXj) names Smart Scribe/Ult4 first and Yoga Maya/Dropout Society fifth in the prior event. The [Smart Scribes repository](https://github.com/Kartavya728/Smart-Scribes) and linked 15-page presentation expose workflow diagrams and annotated role-specific screens. The [YogMaya repository](https://github.com/Aman071106/dropout_society) includes demonstration/install materials and reported performance claims. Neither repo is a verified competition-time snapshot, their numbers were not reproduced, and video playback was not independently reviewed.

**Presentation inference:** VesselRisk already meets that visible completeness standard with a real input/output flow, evidence and runnable materials. The remaining opportunity is a readable, tightly paced recorded demonstration, not copying their feature breadth. No comparative claim of superior score or guaranteed winning polish is supported.

## Judgment

Before the new batch, **B is the more plausible working explanation, with low confidence in any numerical ceiling**. The original search is too narrow to declare modeling exhausted; the papers are too different to establish that .85+ vessel AUC is attainable here. The completed batch and conditional uncertainty are reported in `FINAL_AUDIT_RESULTS.md`. Even a negative result only rules out that declared search at this sample size and protocol. Independent patients are required for a strong generalization claim.
