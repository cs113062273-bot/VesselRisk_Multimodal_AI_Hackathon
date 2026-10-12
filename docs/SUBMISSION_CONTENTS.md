# Public source and submission contents

The public repository is a portable source distribution. A reviewer can download the GitHub source ZIP, extract it, and run `python scripts/start.py --setup` from the folder containing README.md. Setup downloads dependencies and builds the frontend. Subsequent launches use `python scripts/start.py`. Python 3.13 and Node.js 24 are recommended. Open http://127.0.0.1:3000.

## Retained

| Content | Why it is included |
|---|---|
| `api/`, `ml/`, `web/app`, `web/components`, `web/lib` | Application, prediction and explanation code |
| Four classifiers, OOD, registry, evidence and integrity manifest in `ml/artifacts/` | Predictions work without retraining; stored fold models also support held-out demos and fitted-model ranges |
| Original XLSX and `data/data_dictionary/features.json` | API cases, input controls, integrity checks and reproducible evaluation |
| `web/public/anatomy/` | Local 3D geometry, structure mapping and attribution |
| `experiments/reliability/`, `experiments/vessel_refinement/`, `experiments/final_audit/` | Evidence shown by the app and reproducible scientific checks; these are not disposable scratch results |
| Requirements, package lock, startup script, Docker/Compose files, tests and CI | Install, build, run and verify the application |
| Six-page report, model card, architecture, licenses and Track A specification | Required documentation and source provenance |
| Current product/review screenshots and demo narration | Explain the current application and support report regeneration |

## Local-only

These files remain on the author's computer but are removed from Git tracking and excluded from generated submission archives:

- `submission/`: generated full-project ZIP, checksum and extracted-package verification. Publish a ZIP as an optional release attachment rather than embedding another copy of the project in the repository.
- `review/visual-polish/` and `review/first-30-seconds/`: historical before/after screenshots and source rollback ZIPs.
- `CODEX_MASTER_BRIEF.md`, `instruction.md`, the supplied UUID-named design image, and `agent_server.py`: internal development references and an unrelated local coding-agent server.
- `docs/EXECUTION_PLAN.md`, `docs/FIRST_30_SECONDS.md`, `docs/VISUAL_INTERACTION.md`, `docs/VISUAL_POLISH.md`, and their two historical capture scripts: development history and rollback instructions.
- Browser-test screenshots in `demo/screenshots/`: retain only the six current product captures. Tests can regenerate their diagnostic captures.
- The original dataset ZIP: the unmodified extracted XLSX is retained instead.
- `review/RESEARCH_THRESHOLDS.json`: duplicate of `experiments/vessel_refinement/results.json`. The review CSV remains available.
- `review/FILE_MANIFEST.json`: generated for each optional archive, not maintained as a stale source-repository inventory.
- `.venv/`, `node_modules/`, `.next/`, QA renders, downloaded image caches, temporary files, logs, environment files, bytecode and training checkpoints.

The Git history is not rewritten by this cleanup. GitHub's source ZIP contains the current tree; a full clone can still fetch historical versions of removed files.

## Checks and optional archive

```powershell
python scripts/submission_files.py --tracked
python scripts/package_review.py
python scripts/verify_review.py --contents-only
```

The first command checks that required files are present in the Git index and that local-only files are excluded. The packager uses the same selection policy, includes a per-file hash manifest, and checks the archive CRC. The generated ZIP contains source and runtime assets, not a machine-specific Next.js build. Models and data are not changed by packaging.

For a full extracted-package check, use the pinned Python environment to run `python scripts/verify_review.py`. It installs fresh frontend dependencies and runs scientific/API checks and desktop browser journeys against the extracted source.

## Cleanup validation (2026-10-12)

Removed 118 local-only tracked files while retaining their local copies. The resulting source selection has 154 files (about 22.6 MiB), including a previously untracked required target-color module. From the extracted source archive: 30 scientific/API checks, frozen-metric verification, fresh `npm ci`, a fresh production build, and three desktop browser journeys passed. Python used the pinned existing environment, not a new Python installation. Protected model/data/anatomy/report hashes and local documentation links were checked. Details are recorded in `../review/BUILD_VALIDATION.json`.
