# VesselRisk 完成報告／審查摘要

整理日期：2026-10-02（Asia/Taipei）。此文件說明實際交付與已驗證範圍，不代表已獲獎或已完成競賽送件。

## Final strict audit update

The additional predeclared elastic-net/HistGradientBoosting/CatBoost investigation is complete: LCX/RCA expanded-policy AUC .7311/.7327 versus .7278/.7318, with paired gain intervals including zero and insufficient fold consistency. Original production artifacts remain unchanged. RCA elastic net's .7479 AUC is an unconfirmed secondary lead, not a model selected for deployment. Full results and regressions: [FINAL_AUDIT_RESULTS](../docs/FINAL_AUDIT_RESULTS.md).

Implemented workbook/artifact pairing verification, exported exact estimator references, honest reset-view orientation, a legend matching the discrete probability colors, explicit single-model versus averaged-OOF wording, and pinned anatomy regeneration. The timed demo opening and English Devpost draft are prepared. **19** scientific/API checks, frozen metric/hash verification, an independent 160-trial audit, production build and two browser journeys pass. Report and captures are refreshed. Required final recording/upload and competition entry links are still outstanding. This update supersedes the earlier test counts below.

## 已完成

- 可操作的 Next.js + FastAPI 產品：55 個臨床輸入、JSON 匯入／匯出、四個真實預測、同步更新 3D 與解釋。
- CAD、LAD、LCX、RCA 四個模型；Logistic regression、Random forest、XGBoost 的巢狀比較；校準、OOF 結果、模型與 split artifacts 已保存。
- 5-fold × 2-repeat outer CV，3-fold inner tuning；前處理與校準限制在 training partitions；目標欄位 guard 實際存在且有測試。
- 真實 BodyParts3D 冠狀動脈 meshes：旋轉、縮放、平移、分別點選 LAD／LCX／RCA、X-ray、血管隔離、展開視圖；依血管預測上色。
- 校準機率的 local/global permutation SHAP、模型分歧、refitted-model range、OOD 提示。SHAP 加總重建的是畫面上的機率。
- Evidence Lab：完整 metrics、ROC／PR／calibration、confusion matrices、model comparisons、subgroups、ablations、失敗案例、來源與模型 hashes。
- README、六頁技術報告、五分鐘 demo script、資料／模型卡、來源授權、架構、先前獲獎專案研究、verification record。
- 本審查包另外提供 10 張實際產品截圖、完整數字 CSV／JSON、HTML 審查入口；沒有用 mock 圖替代產品。

## 結果與主要限制

Internal nested-CV ROC-AUC：CAD 0.925、LAD 0.839、LCX 0.728、RCA 0.732。

最後限縮優化：ExtraTrees／RBF SVM 各兩設定，expanded policy 未達預設改善門檻，原模型 hashes 保留。Training-only nested F1 cutoff 的 LCX recall／F1 為 .840／.641、RCA .868／.631；precision .518／.495。FP 30→93／34→101，accuracy .673→.630／.660→.617。AUC／calibrated probability 未變；原 0.50 baseline 和 workspace convention 保留。新結果並列於 Evidence Lab 與 RESEARCH_THRESHOLDS CSV／JSON，不冒充外部驗證。

另外完成 sklearn pre-unpickle version guard、demo 的 product-first 節奏、p2／p4 簡圖與文字精簡。四項結束後停止功能擴充。

最後審查微調：Evidence Lab 移除依 pooled outer-test retention gate 決定的高亮，固定 0.50 與 exploratory training-selected F1 operating point 平等呈現。Threshold 值仍由 training-only inner OOF 選出，但 retention 是看 outer 結果的 development audit，不能當作獨立確認。Demo 口白明說 reused nested-CV development evaluation 與 sensitivity／precision tradeoff；模型、報告及既有測試未改動。

主要結果評估的是 nested model-selection procedure；全資料選出的 deployed family 與個別 held-out demo 所使用的 fold model 必須分開理解。不要將這些數字描述成 final model 的獨立 external-test 成績。

最應接受審查的弱點：

1. LCX／RCA 在 0.50 threshold 的 recall 只有 0.420／0.395。這是實際性能弱點，沒有隱藏。
2. 僅 303 人、單中心 referral cohort；沒有外部臨床驗證。Bootstrap CI conditional on fitted folds，未包含重新訓練／選模變異。
3. 四個 target 是獨立 classifiers，可能互相矛盾；沒有強制修改結果來製造一致性。
4. 解釋為近似、非因果 SHAP；model range 與 OOD 為 descriptive heuristics，不是經臨床驗證的 confidence interval／detector。
5. 3D 是 generic adult male anatomy，不是病人的 scan，也不顯示捏造的 lesion 位置或 stenosis severity。
6. 軟體 WebGL 測試通過，但 FPS 依電腦而異；不可宣稱所有無獨顯裝置都固定達到某個 FPS。

## 怎麼 run

Python 3.13、Node.js 24 建議。專案根目錄執行：

```powershell
python scripts/start.py --setup
```

之後用 `python scripts/start.py`。網站：http://127.0.0.1:3000；API schema：http://127.0.0.1:8000/docs。

模型與 3D 資產已附，不需雲端帳號、API key 或重新訓練。啟動時以真實模型準備 opening case 的 SHAP，避免第一次操作承擔編譯延遲。

## 測試／build status

- 完整訓練成功；四 target 的 artifacts、OOF、split indices 與 hashes 已保存。
- `python -m ml.evaluate`：重新計算 frozen OOF metrics 並驗證 dataset／model hashes，通過。
- `python -m pytest`：18 個 checks 通過；新增 sklearn mismatch before unpickling、threshold training-only splits、research metrics reconstruction 三個必要檢查。
- `npm run typecheck`、`npm run lint`、production build 通過。
- 本輪表述微調後重新通過 typecheck／lint／production build；實際 production LCX／RCA 比較表無 retention 高亮、四列均保留，390px mobile 無頁面水平溢出，無 browser errors。只做針對性畫面驗證，沒有新增測試或重跑模型。
- 兩個真實 Playwright journeys 通過（15.2 秒）：desktop end-to-end 與 mobile，包含新增的 research threshold rows 與 mobile overflow。
- fresh `.venv` 安裝、`pip check`、`python scripts/start.py --setup` production startup 已驗證。
- 10 張新增審查截圖另由實際 production app 擷取；完整記錄見 `screenshots/index.json`。
- 有 upstream test-client AnyIO deprecation warning，沒有 failing checks。

## 未完成／未驗證

- 尚未錄製及上傳最終 3–10 分鐘 YouTube demo，尚未以提交者帳號送件。
- 尚未公開部署 frontend + Python model service。Native local production 完整可用。
- Dockerfile／Compose 已提供，但此主機沒有 Docker，容器執行未驗證。
- 沒有新增外部 clinical validation；不宣稱可用於診斷、治療或族群篩檢。
- Team／author 資訊、最終文案、公開 repository／demo links 需提交者 review。

## 官方評分項目對照

| 權重 | 建議實際檢查 | Evidence |
|---|---|---|
| Prediction 30% | 四 target 數字、低 recall、校準、fold validity | `MODEL_RESULTS.md`／CSV／JSON、`../ml/artifacts/evidence.json` |
| 3D 25% | 真實獨立 mesh、互動與上色、一般裝置體驗 | 截圖 01–05、`../web/public/anatomy/manifest.json`、`../web/components/HeartViewer.tsx` |
| Interpretability 20% | 顯示的機率是否被解釋、限制是否清楚 | 截圖 02／08、`../ml/modeling.py`、`../api/service.py` |
| Integration 15% | 輸入 → API → 四模型 → 3D／解釋、改值與失敗狀態 | `../web/e2e/demo.spec.ts`、實際 run |
| Technical 10% | 可重現、guard、模型版本、授權、build | `../tests/test_validity.py`、`../docs/VERIFICATION.md`、`../ATTRIBUTIONS.md` |

上述是審查入口，不是自評分數。是否「離第一名還差多少」，仍需審查者實際使用產品並比較同場作品。

AI disclosure：OpenAI Codex 協助研究、實作、debug、驗證、UI 與報告草稿。沒有 generative model 用於疾病預測或醫療建議。
