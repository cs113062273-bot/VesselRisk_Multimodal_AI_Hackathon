# Track A 審查包：先看這三件事

Current snapshot: 2026-10-09. See [reliability evidence](../docs/RELIABILITY_AUDIT.md), [model investigation](../docs/FINAL_AUDIT_RESULTS.md), and [English Devpost copy](../docs/DEVPOST_COPY.md). Current screenshots, report and ZIP include the patient/evidence separation, enriched heart viewer and reliability changes. Exact build/test and extracted-package outcomes are recorded in `BUILD_VALIDATION.json`. Final video/entry publication remain outstanding.

1. 開 `index.html`：先看實際主畫面、11 張截圖、四模型的真實結果，以及主要方法／限制。可離線開啟。
2. 看 `COMPLETION_SUMMARY.md`：已完成、未完成、已知弱點、run／test／build status，以及 30%／25%／20%／15%／10% 審查對照。
3. 實際 run 專案：根目錄 `python scripts/start.py --setup`，開 http://127.0.0.1:3000。直接預測、點血管，再看 Model evidence。

## 包內內容

- 完整 frontend、backend、ML pipeline、trained artifacts、原始資料、3D assets。
- build/run scripts、Dockerfiles／Compose、package lock、requirements、CI、tests 均保留。
- **不包含本機 `.next` 編譯結果**；首次執行 `python scripts/start.py --setup` 會安裝依賴並建置適合當前環境的前端。
- 原始 README、six-page report、demo script、docs、licenses 與 supplied Track A specification 均保留。
- 本文件、completion summary、完整結果表、CSV／JSON，以及 11 張實際截圖位於 `review/`。
- `../experiments/reliability/results.json` 包含 local SHAP 敏感度及校準證據；`../ml/artifacts/integrity.json` 核對完整推論檔案組。
- 執行 `python scripts/package_review.py` 產生的 ZIP 內含 `FILE_MANIFEST.json`，可核對每個檔案的 byte size 與 SHA-256；這個生成檔不納入 Git。

公開庫與 ZIP 排除可重裝 dependencies（`.venv`、`node_modules`）、編譯結果、cache、QA 圖片、舊介面前後對照／備份、內部開發指令、測試暫存、env／log files 和重複的專案 ZIP。保留應用程式 source、models、原始 XLSX、3D assets、lockfiles、report 和 build/run configuration。完整分類見 `../docs/SUBMISSION_CONTENTS.md`。

下載 GitHub 的原始碼 ZIP 後先解壓縮，在含 README 的專案根目錄執行 `--setup`；安裝時需要網路下載 Python/npm 依賴。推論本身不需要雲端服務、API key 或重訓。

## 最重要的科學注意事項

Headline metrics 是 repeated nested OOF selection-policy 結果，非 final full-cohort model 的外部 test。Deployed family 與各 outer fold 選出的 family 不一定相同。CI 與 fold SD 的限制寫在結果表內。

最後限縮優化另列於 `RESEARCH_THRESHOLDS.csv`；完整 JSON 保留於 `../experiments/vessel_refinement/results.json`，不重複複製到 review。Training-only operating points 與 0.50、expanded search 同時列出，含更多 false positives 的代價。原 deployed models 沒有替換；`../docs/VESSEL_REFINEMENT.md` 是完整方法與保留／拒絕理由。

LCX／RCA recall 明顯弱於 CAD／LAD；沒有外部臨床驗證。這些應列入審查，而不是只看 CAD AUC。

原始六頁報告：`../report/VesselRisk-Track-A.pdf`。
Demo script：`../demo/DEMO_SCRIPT.md`。
完整方法／限制：`../docs/DATA_MODEL_CARD.md`。
