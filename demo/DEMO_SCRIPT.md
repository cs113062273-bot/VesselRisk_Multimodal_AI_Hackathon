# VesselRisk: five-minute desktop demonstration

Updated 2026-10-09. This script follows the current UI. Record at 1440 x 1000 or 1920 x 1080. Use `python scripts/start.py`; run the opening prediction once before recording to confirm readiness. Begin with the first case (54-year-old man, smoker with chest pain), expanded Patient profile and the first-opening orbit. Read values from the live application.

| Time | Live actions | Suggested English narration |
|---|---|---|
| 0:00-0:45 | Show the patient profile and four main measurements. Predict. The profile collapses above the heart, explanation and analytics. | "VesselRisk turns clinical measurements into four coronary estimates. This held-out profile gives 94.9% overall CAD, 90.4% LAD, 17.7% LCX and 18.6% RCA. The probabilities appear in the explanation tabs, and the coronary arteries update with them." |
| 0:45-1:25 | Select LCX and RCA in the viewer dropdown or explanation tabs. Rotate/zoom; show X-ray and Vessels only; restore the normal view. | "Each coronary artery is real, independently selectable BodyParts3D anatomy. Selecting a target synchronizes its view, explanation and analytics. The color indicates vessel-level probability; it does not locate a lesion or measure how severely a vessel is narrowed." |
| 1:25-2:05 | Select LAD, point to patient values and signed contributions. Open Model & calculation details. Show Three models, one profile. | "These contributions explain the same calibrated probability displayed above. Their sum plus the background reconstructs the estimate. This checks the calculation, while the three-model chart shows disagreement. The displayed model excluded this example patient." |
| 2:05-2:50 | Evidence Lab, Validation, CAD then LCX. Show metrics, calibration and Calibration evidence. | "Validation uses five outer folds repeated twice, with selection and calibration confined to training partitions. CAD AUC is .925, LAD .839, LCX .728 and RCA .732. Calibration groups include patient counts and descriptive intervals. Compared with a training-prevalence baseline, Brier error falls about 54%, 35%, 13% and 14%. These are internal results, not external validation." |
| 2:50-3:25 | On LCX scroll to Research operating thresholds; open exact metrics. Then RCA. | "At the default threshold, LCX and RCA recall are .420 and .395. Exploratory training-selected cutoffs detect more positives but substantially increase false positives. AUC and probability quality remain unchanged. We show this tradeoff rather than present a lower threshold as a better model." |
| 3:25-4:05 | Interpretability, Local explanation stability; then Robustness, Where the model failed. | "We also measured explanation sensitivity on four predefined held-out profiles. Changing the training background preserved only three or four of the five leading factors in some cases. This quantifies a limitation; it does not prove that every explanation is stable. Failure examples remain visible in Evidence Lab." |
| 4:05-4:40 | Return to Patient workspace, expand profile, edit Age or Weight. Show input-origin counts and derived BMI. Predict again, Export case. | "Every prediction uses all 55 inputs. The summary distinguishes cohort records, defaults, user entries, imports and calculated values. Editing marks the previous result stale. Predicting again updates the heart and explanation, and the export snapshots the inputs, their origins and exact model reference." |
| 4:40-5:00 | End on the heart with all three result regions visible. | "The complete package includes trained models, fold evidence, licensed anatomy, reproducible startup and a six-page report. Checkpoints verify the training protocol, and inference files are checked before loading. This is research and education software on a small internal cohort, with no patient-specific lesion map or treatment advice." |

## Recording checks

- Official duration is 3-10 minutes; this script targets five. Show actual live operations and avoid reading every metric aloud.
- Case labels describe patient characteristics. Do not look for removed "Mixed vessel estimates", "Lower CAD estimate", "Reveal outcomes" or status strips.
- The workspace uses one fitted model; headline evaluation averages two held-out predictions per patient. Explain the distinction once.
- SHAP additivity and sensitivity are separate checks. Background sensitivity changes the reference explanation; four profiles do not establish population-wide stability.
- Verify clear audio, readable text and judge-accessible YouTube visibility. The final recording, upload and public link are outstanding until actually completed.

No final video or YouTube URL is represented by this script. Keep the submission checklist open until the actual recording and link are verified.
