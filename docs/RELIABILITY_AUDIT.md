# Frozen-model reliability audit

This audit adds evidence and integrity checks without refitting models, changing the 0.50 classification convention, or changing the historical `registry.json` / `evidence.json` files.

Run `python -m ml.reliability` in the pinned environment. Results are in `experiments/reliability/results.json`, including the full attribution vectors, seeds, background row indices, fold identifiers, timing, protocol and fingerprints. The API attaches matching results to `/evidence`; mismatched or missing diagnostics are omitted rather than attached to a different model. Export evidence includes these diagnostics.

## Probability quality

Six quantile bins retain the original calibration coordinates, adding patient and positive counts and descriptive 95% Wilson intervals for each observed fraction. These are conditional on the bins and fixed predictions: correlated cross-validation fits, retraining and selection uncertainty are not covered. Each patient appears once after averaging their two held-out probabilities.

The baseline predicts the positive fraction in each outer fold's training partition; its two held-out probabilities are averaged in exactly the same way. It never uses the evaluated patient's label to construct that patient's baseline. Brier intervals and paired differences use 2,000 patient resamples of fixed predictions. They are internal conditional diagnostics, not external validation.

| Target | Brier | Conditional 95% interval | Training-prevalence baseline | Relative Brier reduction |
|---|---:|---:|---:|---:|
| CAD | 0.0943 | 0.0735–0.1144 | 0.2047 | 53.9% |
| LAD | 0.1573 | 0.1339–0.1819 | 0.2429 | 35.2% |
| LCX | 0.2064 | 0.1896–0.2245 | 0.2385 | 13.5% |
| RCA | 0.2014 | 0.1830–0.2205 | 0.2347 | 14.2% |

LCX/RCA contain useful predictive information but show much smaller improvement over the baseline. These findings do not establish a theoretical performance ceiling. Separate-repeat metrics are also exposed so the benefit of averaging two held-out predictions is visible.

## Local SHAP sensitivity

Four existing demo rows (zero-based 2, 41, 68, 3) were fixed before measuring stability. For each of four targets, use the same held-out fold model as the workspace. All background samples come from that fold's training rows. These 16 case/target combinations are a small diagnostic sample, not a representative population study.

Compare two cycles with a changed seed; compare two with eight cycles under the same seed/background; compare two eight-cycle explanations under different training backgrounds. The latter comparison holds seed and computation fixed, isolating the background change. Record top-five set overlap, sign agreement for the reference top five, and largest change among all 55 contributions. Preserve full vectors for verification.

| Target | Top-five overlap: changed seed, mean | More cycles, mean | Different background, mean | Largest background contribution change |
|---|---:|---:|---:|---:|
| CAD | 85% | 90% | 75% | 10.7 pp |
| LAD | 95% | 95% | 75% | 6.2 pp |
| LCX | 95% | 95% | 75% | 3.9 pp |
| RCA | 95% | 100% | 75% | 8.4 pp |

The reference top-five directions were preserved in these comparisons, but membership and magnitudes changed. Background changes also change the reference probability and the explanation being asked of the model. This is sensitivity evidence, not proof that either background is correct. The audit does not select a new explanation setting or claim all patient explanations are stable.

## Integrity and input provenance

- Checkpoint reuse requires matching source data, target, seed, schema, repeat count, Python/dependency versions and training-source fingerprints. Older or mismatched checkpoints restart; replacement writes are atomic.
- `integrity.json` covers every inference model, OOD, registry, evidence and feature schema. API startup verifies the complete set before any estimator is deserialized. New text fingerprints normalize CRLF to LF; binary fingerprints use exact bytes. Historical evidence/registry line endings are pinned in `.gitattributes` to preserve older experiment fingerprints across operating systems.
- Training writes the integrity manifest. `python -m ml.integrity` is only an explicit packaging command for trusted files. A hash manifest detects mismatched files; it is not a cryptographic authenticity signature.
- Patient inputs track cohort record, cohort default, user entry, import and derived BMI. The summary counts origins; field hover identifies its origin. Prediction exports snapshot these sources alongside the exact submitted values. User-entered/imported does not mean independently verified clinical measurement.
- CI runs desktop Chromium target-synchronization, prediction/export, analytics and provenance tests. No mobile tests or layouts were added.

## Where to inspect

In the workspace, hover calibration points for sample counts and intervals. In **Evidence Lab → Validation**, expand **Calibration evidence** for counts, intervals, baseline comparisons and per-repeat performance. In **Interpretability**, expand **Local explanation stability** for sensitivity results. Detailed evidence stays in these expandable sections rather than adding another permanent workspace block.
