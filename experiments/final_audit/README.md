# Archived final model opportunity audit

The predeclared expansion did not clear its materiality/consistency criteria. No fitted candidate weights were saved, no candidate was added to the application, and production dependencies/artifacts remain unchanged. The runner and negative evidence are retained only to make every attempted candidate reviewable and reproducible; do not continue searching this archive based on its outer results.

This is a development comparison on previously inspected patients, not independent confirmation. The full outcome, including promising secondary results that were **not** used to choose a family, is in `../../docs/FINAL_AUDIT_RESULTS.md`.

Files:

- `protocol.json`: fixed eight configurations and analysis/deployment rules, written before execution.
- `execution.json`: protocol/runner fingerprints, baseline file fingerprints and library versions recorded before fitting.
- `LCX-folds.json`, `RCA-folds.json`: every trial, inner OOF probabilities, absolute inner/outer indices, selected specification and fold metrics.
- `results.json`: all repeat/pooled outputs, paired conditional intervals and one record per patient.
- `verification.json`: independent reconstruction of saved metrics, winners, splits and hashes; descriptive secondary intervals.

Verify without CatBoost or retraining:

```powershell
.venv\Scripts\python -m experiments.final_audit.verify
```

Reproduce in a **separate clean project copy** with the original frozen artifacts and no generated audit JSON except `protocol.json`. Install pinned project requirements plus `experiments/final_audit/requirements.txt` into an isolated environment, then run:

```powershell
python -m experiments.final_audit.run
python -m experiments.final_audit.verify
```

The runner refuses to overwrite `results.json`. During this audit CatBoost 1.2.8 was installed separately under `tmp/final-audit/extra-packages`, made visible only to that command with `PYTHONPATH`; it was not installed in the application's `.venv`. No external service receives patient data. CPU execution, two threads; measured runtime about 430 seconds on the audit host. Runtime may differ elsewhere.
