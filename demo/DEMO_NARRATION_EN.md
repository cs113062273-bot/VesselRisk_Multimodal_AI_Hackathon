# VesselRisk — 7:00 English narration

Voice: en-US-AriaNeural via edge-tts. Scene times match DEMO_TIMELINE.json; unused time stays silent.

## 00:00–00:15 · S01

This is VesselRisk: coronary risk prediction, interactive anatomy, and model evidence.

## 00:15–00:25 · S02

First, I choose the fifty-nine-year-old example with diabetes and hypertension. It fills all fifty-five inputs.

## 00:25–00:35 · S03

History, symptoms, ECG, labs, and echo cover all inputs. Key inputs collects the main measurements.

## 00:35–00:47 · S04

Search works across groups. I change age, then reset the example to its original values.

## 00:47–00:59 · S05

The example returns four probabilities. The anatomy updates its colors, and the heart begins orbiting.

## 00:59–01:07 · S06

Positive uses a fifty-percent research cutoff. The displayed probability is not blockage severity.

## 01:07–01:15 · S07

Labels, the selector, and explanation tabs stay synchronized for each artery.

## 01:15–01:25 · S08

I rotate, zoom, and pan. The labels remain attached to the anatomical surface.

## 01:25–01:35 · S09

Orbit and pause control motion. X-ray and vessel isolation reveal the coronary branches.

## 01:35–01:50 · S10

The expanded view includes an anatomy guide for each artery. Reset restores the camera. Colors represent probability on reference anatomy.

## 01:50–02:02 · S11

SHAP connects the background probability to this result. Red raises it; teal lowers it. Contributions use percentage points.

## 02:02–02:12 · S12

Compare candidate models and the range across fitted models. This range is not a confidence interval.

## 02:12–02:22 · S13

All fifty-five contributions are available, with model, calibration, response time, and the held-out result source.

## 02:22–02:35 · S14

I export the example, then import and reset a blank-identity profile. The second test uses manual inputs.

## 02:35–02:45 · S15

An empty height blocks prediction. Restoring height and weight automatically recalculates BMI.

## 02:45–02:55 · S16

Age nine hundred ninety-nine is rejected by the API. I correct it to ninety.

## 02:55–03:15 · S17

This synthetic profile is a ninety-year-old woman, one hundred sixty centimeters, sixty kilograms, with hypertension and no diabetes. Blood pressure is one hundred forty-five; pulse, seventy-six.

## 03:15–03:35 · S18

I enter no typical chest pain, fasting glucose one hundred, LDL one hundred ten, HDL fifty, ejection fraction fifty-five, and RWMA category zero.

## 03:35–03:44 · S19

I check smoking and obesity, and inspect the source of the remaining default values.

## 03:44–03:54 · S20

I review the remaining groups. Edited inputs mark the previous explanation as stale and block export until prediction.

## 03:54–04:07 · S21

The new profile returns fresh probabilities. Age ninety triggers a warning because it exceeds the observed cohort age range.

## 04:07–04:18 · S22

This profile uses the full-cohort model. Ten fitted models show variation, and I export the complete case.

## 04:18–04:31 · S23

Model evidence makes the evaluation inspectable: the workflow, four targets, discrimination, calibration, and missed positives.

## 04:31–04:40 · S24

The overview switches between recall and AUC. Selecting a target opens its validation evidence.

## 04:40–04:50 · S25

Each target has separate metrics, fold variation, and uncertainty estimates from nested validation.

## 04:50–05:00 · S26

Interactive ROC, precision-recall, and calibration plots expose the underlying evaluation points.

## 05:00–05:12 · S27

Calibration details include patient counts, intervals, a training baseline, and results before averaging the repeated validation runs.

## 05:12–05:22 · S28

Candidate comparison and the confusion matrix show exactly where the LCX classifier succeeds and makes errors.

## 05:22–05:31 · S29

Raw and calibrated results are compared alongside the nested selection protocol and reproducible seed.

## 05:31–05:41 · S30

For LCX, an alternative research threshold reduces misses from sixty-nine to nineteen, while increasing false positives.

## 05:41–05:51 · S31

RCA shows the same tradeoff. The exact table preserves each operating point; workspace classification remains at fifty percent.

## 05:51–05:59 · S32

Additional model experiments and all ten outer folds are available for inspection.

## 05:59–06:13 · S33

Global SHAP ranks influential inputs. Stability tests compare changed seeds, computation budgets, and backgrounds, including the largest observed change.

## 06:13–06:26 · S34

Robustness includes subgroup checks, feature ablations, and actual false positives and false negatives. The page also states the study limitations.

## 06:26–06:42 · S35

Provenance covers the dataset, leakage checks, model parameters, hashes, software versions, and anatomy sources. The evidence can be downloaded.

## 06:42–06:52 · S36

The scope panel links the six-page technical report, including methods, results, and limitations.

## 06:52–07:00 · S37

The case remains available. VesselRisk combines prediction, anatomy, explanations, and reproducible evidence for research.
