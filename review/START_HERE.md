# Track A 審查包：先看這三件事

Current snapshot: 2026-10-09. See [reliability evidence](../docs/RELIABILITY_AUDIT.md), [model investigation](../docs/FINAL_AUDIT_RESULTS.md), and [English Devpost copy](../docs/DEVPOST_COPY.md). Current screenshots, report and ZIP include the reliability changes. Exact build/test and extracted-package outcomes are recorded in `BUILD_VALIDATION.json`. Final video/entry publication remain outstanding.

1. 開 `index.html`：先看實際主畫面、10 張截圖、四模型的真實結果，以及主要方法／限制。可離線開啟。
2. 看 `COMPLETION_SUMMARY.md`：已完成、未完成、已知弱點、run／test／build status，以及 30%／25%／20%／15%／10% 審查對照。
3. 實際 run 專案：根目錄 `python scripts/start.py --setup`，開 http://127.0.0.1:3000。直接預測、點血管，再看 Evidence Lab。

## 包內內容

- 完整 frontend、backend、ML pipeline、trained artifacts、原始資料、3D assets。
- build/run scripts、Dockerfiles／Compose、package lock、requirements、CI、tests 均保留。
- **production `.next` build 已保留**；只排除 `.next/cache`／`.next/dev` 等可重建 cache。
- 原始 README、six-page report、demo script、docs、licenses 與 supplied Track A specification 均保留。
- 本文件、completion summary、完整結果表、CSV／JSON，以及 10 張實際截圖位於 `review/`。
- `../experiments/reliability/results.json` 包含 local SHAP 敏感度及校準證據；`../ml/artifacts/integrity.json` 核對完整推論檔案組。
- `FILE_MANIFEST.json` 可核對 package 中每個檔案的 byte size 與 SHA-256。

只排除可重裝 dependencies（`.venv`、`node_modules`）、cache／temporary research downloads、測試暫存、VCS metadata、env／log files，以及本次輸出的 ZIP，避免重複打包或夾帶本機設定。沒有刪掉 source、models、3D assets、lockfiles 或 build/run configuration。這是可建置的完整 repo snapshot，非只剩 screenshots 的簡化版。

`web/.next` 是本次 Windows production build；跨環境請使用 `--setup` 重新建置，不要假設既有 output 在所有平台都能直接重用。

## 最重要的科學注意事項

Headline metrics 是 repeated nested OOF selection-policy 結果，非 final full-cohort model 的外部 test。Deployed family 與各 outer fold 選出的 family 不一定相同。CI 與 fold SD 的限制寫在結果表內。

最後限縮優化另列於 `RESEARCH_THRESHOLDS.csv`／JSON：higher recall/F1 的 training-only operating points 與 0.50、expanded search 同時列出，含更多 false positives 的代價。原 deployed models 沒有替換；`../docs/VESSEL_REFINEMENT.md` 是完整方法與保留／拒絕理由。

LCX／RCA recall 明顯弱於 CAD／LAD；沒有外部臨床驗證。這些應列入審查，而不是只看 CAD AUC。

原始六頁報告：`../report/VesselRisk-Track-A.pdf`。
Demo script：`../demo/DEMO_SCRIPT.md`。
完整方法／限制：`../docs/DATA_MODEL_CARD.md`。
