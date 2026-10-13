# Archived final model opportunity audit

The predeclared expansion did not clear its materiality/consistency criteria. No fitted candidate weights were saved, no candidate was added to the application, and production dependencies/artifacts remain unchanged. The runner and negative evidence are retained only to make every attempted candidate reviewable and reproducible; do not continue searching this archive based on its outer results.

This is a development comparison on previously inspected patients, not independent confirmation. All candidate results are in `results.json`; the application retains its original models.

Files:

- `protocol.json`: fixed eight configurations and analysis/deployment rules, written before execution.
- `execution.json`: protocol/runner fingerprints, baseline file fingerprints and library versions recorded before fitting.
- `LCX-folds.json`, `RCA-folds.json`: every trial, inner OOF probabilities, absolute inner/outer indices, selected specification and fold metrics.
- `results.json`: all repeat/pooled outputs, paired conditional intervals and one record per patient.
- `verify.py`: reconstructs saved metrics, winners, splits and hashes without fitting models. It writes `verification.json` locally when run.

Verify without CatBoost or retraining:

```powershell
.venv\Scripts\python -m experiments.final_audit.verify
```

Reproduce in a **separate clean project copy** with the original frozen artifacts and no generated audit JSON except `protocol.json`. Install pinned project requirements plus `experiments/final_audit/requirements.txt` into an isolated environment, then run:

```powershell
python -m experiments.final_audit.run
python -m experiments.final_audit.verify
```

The runner refuses to overwrite `results.json`. CatBoost is an experiment-only dependency; the application does not need it. No external service receives patient data. Execution uses the CPU with two threads.
