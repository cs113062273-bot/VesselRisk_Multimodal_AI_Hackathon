# VesselRisk：7 分鐘錄影腳本

**總長 07:00（420 秒）。** 中文照做；英文是之後的配音／字幕，你錄影時不用講話。

錄影前：依賴與 build 已完成；Chrome 已開 `localhost:3000`；檔案選擇器可找到 `demo/CUSTOM_PROFILE_START.json`。固定桌面視窗與縮放比例。

啟動或推論等太久時，最後剪掉超出的等待，接回以下時間。配音使用 `edge-tts` 的 **en-US-AriaNeural**，各段獨立配音、補靜音；字幕依同一份 [時間軸](DEMO_TIMELINE.json) 製作。

## 先認清畫面位置（不用錄進影片）

| 腳本提到的位置 | 實際在哪裡 |
|---|---|
| 頂部導覽列 | 最上方白色橫列：左側 VesselRisk；中央 Patient workspace／Model evidence；右側 Export case 或 Export evidence，最右端是圓圈 i。 |
| Patient profile 表單 | 導覽列下方的大白色區塊；標題列有 Example(Optional)、Reset inputs、Import JSON；最右端 Expand／Collapse 控制展開。 |
| 表單分組列 | Patient profile 標題下一排：Key inputs／History／Symptoms／ECG／Labs & echo；右側搜尋框寫 Find a measurement…。 |
| 心臟畫布 | 表單下方左邊的深藍色區塊；頂部是血管下拉、書本、擴大圖示；底部是 Orbit／Pause、X-ray、Vessels only、Reset。 |
| 右側說明面板 | 心臟右邊，標題 Coronary Risk Prediction；四機率頁籤在上面，SHAP、模型比較與計算明細在下面。 |
| Model evidence 左側選單 | 切到 Model evidence 後，左邊直式列出 Overview／Validation／Interpretability／Robustness／Data & provenance；詳細內容在右邊。 |

**捲動與輸入約定：**

- 「回頁首／回頂」：先點頁面外側灰白色空白處，再按 Ctrl+Home；不要在數字框內按。
- 「整頁往下」：游標放外側空白處或使用瀏覽器最右邊的捲軸，捲到指定英文標題出現，不用數滾輪格數。
- 「右側面板內捲」：游標放在 Coronary Risk Prediction 白色內容內，使用面板自己的捲軸；尤其是展開 55 項貢獻後。
- 數字修改：點欄位 → Ctrl+A → 輸入指定值；不用按 Enter。下拉修改：點欄位右端箭頭 → 選指定選項。
- 「指」代表移動游標讓觀眾看，不點擊；「展開／收合」是點那行帶小三角形的英文文字。

以下中文是詳細操作指引，不是要唸出的內容；旁白與原本 7 分鐘時間完全相同。

## 逐段操作與旁白

### 00:00–00:15 · S01 · 啟動 → 已開好的 localhost → 刷新

**操作：**

- 00:00 開始錄影。在 VS Code 下方的「終端機」，工作目錄為專案根目錄；輸入 `python scripts/start.py`，按 Enter。
- 00:03 切到 Chrome 已開好的 `localhost:3000` 分頁。留在這個分頁等待，每隔約 3 秒按 F5；看到 VesselRisk 標誌和 Patient profile 表單後，就停止刷新。

**旁白：** This is VesselRisk: coronary risk prediction, interactive anatomy, and model evidence.

### 00:15–00:25 · S02 · 第一輪：Example(Optional)

**操作：**

- 00:15 在網頁上方的白色 **Patient profile** 區塊，找到標題右邊的 **Example(Optional)** 下拉選單，點右端的向下箭頭。
- 00:17 在展開的選單中，點第四個病人 **59-year-old man · diabetes, high blood pressure**。
- 00:20 在下方 **Key inputs** 欄位區，將游標依序移到 **Age 59**、**Diabetes Yes**、**Hypertension Yes**；只指出數值，不修改。

**旁白：** First, I choose the fifty-nine-year-old example with diabetes and hypertension. It fills all fifty-five inputs.

### 00:25–00:35 · S03 · 看全部輸入分組

**操作：**

- 00:25 在 Patient profile 標題下方的橫排分組按鈕中，點 **History**。
- 00:27 同一排點 **Symptoms**，讓下方欄位切換。
- 00:29 同一排點 **ECG**。
- 00:31 同一排點 **Labs & echo**。
- 00:33 點這排最左邊的 **Key inputs**，回到常用欄位。每次切換只展示，不改值。

**旁白：** History, symptoms, ECG, labs, and echo cover all inputs. Key inputs collects the main measurements.

### 00:35–00:47 · S04 · 搜尋、修改、Reset inputs

**操作：**

- 00:35 在表單分組列點 **ECG**。
- 00:36 點分組列右邊、有放大鏡的 **Find a measurement…** 搜尋框，輸入 `cholesterol`。
- 00:39 看搜尋框下方出現的 **LDL cholesterol** 和 **HDL cholesterol** 兩個欄位；即使剛才選 ECG，仍能搜到其他組的欄位。
- 00:40 點搜尋結果上方、**results · all input groups** 那一行右端的 **Clear search**。
- 00:42 點分組列最左邊 **Key inputs**；點下方 **Age** 的數字框，Ctrl+A 後輸入 `60`。
- 00:45 點 Patient profile 標題那一行右側的 **Reset inputs**（迴轉箭頭）。確認 Age 回到 `59`。

**旁白：** Search works across groups. I change age, then reset the example to its original values.

### 00:47–00:59 · S05 · Example 預測

**操作：**

- 00:47 在 Patient profile 欄位區的右下方，點深藍色大按鈕 **Predict coronary risk →**。若按鈕在視窗下方，先在表單外的頁面空白處往下捲到它。
- 等按鈕結束 Predicting…、表單收合後，在頁面空白處往下捲，直到左邊的心臟和右邊 **Coronary Risk Prediction** 都看得見。
- 00:53 將游標移過右側標題下方那排四個機率：**CAD 98.2%／LAD 51.5%／LCX 49.3%／RCA 49.3%**。這四個也是可點選的頁籤。

**旁白：** The example returns four probabilities. The anatomy updates its colors, and the heart begins orbiting.

### 00:59–01:07 · S06 · CAD 與分類提示

**操作：**

- 00:59 在心臟右側 **Coronary Risk Prediction** 下方的四機率列，點最左邊 **CAD**。
- 01:01 在機率列下方找到 **Overall coronary artery disease**；點它右邊 **Positive** 旁的圓圈 **i**，看到分類說明小窗。
- 01:04 按 Escape 關閉小窗。
- 01:05 回到同一排四機率，點第二個 **LAD**。

**旁白：** Positive uses a fifty-percent research cutoff. The displayed probability is not blockage severity.

### 01:07–01:15 · S07 · 三種選取方式

**操作：**

- 01:07 在左側深藍色心臟畫布上，點浮在血管旁、有 **LAD 51.5%** 的小標籤。標籤會隨角度移動，不是畫布底部按鈕。
- 01:09 點心臟畫布頂部的長形下拉選單（目前顯示 LAD · Left anterior descending），選 **LCX · Left circumflex**。
- 01:12 點心臟右側四機率列的 **RCA**。確認左側下拉選單也變 RCA，心臟角度和右側解釋一起切換。

**旁白：** Labels, the selector, and explanation tabs stay synchronized for each artery.

### 01:15–01:25 · S08 · 旋轉、縮放、平移

**操作：**

- 01:15 把游標放在左側心臟畫布中央，避開浮動標籤；按住左鍵向右拖約 120px，再放開，展示旋轉。
- 01:18 游標留在心臟畫布內，滾輪向上 2 格放大，再向下 2 格縮回。不要在頁面白色區域滾動。
- 01:22 在畫布中央按住右鍵，拖約 30px 再放開，展示平移；不是點瀏覽器右鍵選單。

**旁白：** I rotate, zoom, and pan. The labels remain attached to the anatomical surface.

### 01:25–01:35 · S09 · Orbit、Pause、X-ray、Vessels only

**操作：**

- 01:25 在心臟畫布底部、色帶上方的按鈕列，點最左邊 **Orbit**（播放三角形），讓心臟自動轉動。
- 01:28 點同一位置已變成的 **Pause**（暫停符號），停止轉動。
- 01:29 點旁邊第二個 **X-ray**（疊層圖示），心臟外層變透明。
- 01:31 點第三個 **Vessels only**，外層隱藏，只留下血管。
- 01:33 在畫布上點浮動的 **RCA** 標籤，選取右冠狀動脈。

**旁白：** Orbit and pause control motion. X-ray and vessel isolation reveal the coronary branches.

### 01:35–01:50 · S10 · 擴大、三條血管說明、Reset

**操作：**

- 01:35 在心臟底部按鈕列，再點一次 **Vessels only**、再點一次 **X-ray**，關掉這兩個效果。
- 01:36 在心臟頂部下拉選單的右邊，點最右端「兩個向外箭頭」的 **擴大圖示**，進入放大的心臟視圖。
- 01:37 點擴大圖示左邊的 **書本圖示**，開啟目前 RCA 的解剖說明。
- 01:39 按 Escape，只關閉解剖說明，保留擴大視圖。
- 01:40 用擴大視圖頂部的血管下拉選單選 **LAD**，再點書本圖示，展示 LAD 說明。
- 01:42 Escape 關閉說明。
- 01:43 同一個下拉選單選 **LCX**，再點書本圖示，展示 LCX 說明。
- 01:45 Escape 關閉說明。
- 01:46 再按一次 Escape，退出擴大視圖。
- 01:47 點心臟底部按鈕列最右端 **Reset**，還原鏡頭位置。
- 01:48 指按鈕列下方的三色 **Probability** 色帶；再點心臟右側四機率列的 **LAD**，準備看解釋。

**旁白：** The expanded view includes an anatomy guide for each artery. Reset restores the camera. Colors represent probability on reference anatomy.

### 01:50–02:02 · S11 · SHAP 與 pp

**操作：**

- 01:50 看右側 **Left anterior descending** 標題下方的淺藍色橫帶；游標由左至右指 **Explanation background → Combined input contribution → This patient**。
- 01:54 在橫帶下方 **Top influences** 區，指 **Typical Chest Pain** 的紅色正值、**Ejection fraction** 的青綠色負值。
- 01:58 在 **Top influences** 標題右邊、**Raises／Lowers** 後面，點 **pp ⓘ**，開啟百分點說明。
- 02:00 Escape 關閉說明小窗。

**旁白：** SHAP connects the background probability to this result. Red raises it; teal lowers it. Contributions use percentage points.

### 02:02–02:12 · S12 · 模型比較與重訓範圍

**操作：**

- 02:02 在右側 Top influences 下方找到 **Do the models agree?**；指它下面 Logistic regression、Random forest、XGBoost 三條長條及模型名稱旁的勾號。若未露出，先在右側面板內往下捲到這個標題。
- 02:04 點 **Do the models agree?** 標題右端的圓圈 **i**。
- 02:06 Escape 關閉說明。
- 02:07 看長條圖右邊的 **Across fitted models** 區塊；指範圍數字，再點該標題右端的 **i**。
- 02:10 Escape 關閉說明，保持 LAD 選取。

**旁白：** Compare candidate models and the range across fitted models. This range is not a confidence interval.

### 02:12–02:22 · S13 · 全部 55 項貢獻與運算細節

**操作：**

- 02:12 在右側說明面板往下找到長條圖／範圍區下方的 **▸ All 55 inputs & calculation details**，點這行文字展開。
- 02:14 游標放在右側說明面板的白色內容內，滾輪往下，或拖這個面板右緣的內部捲軸到底；要捲的是 55 項貢獻清單。
- 02:17 在清單最下方指 **Model／Calibration／Research cutoff／Result source／Response**；Result source 應為 **held-out demonstration**。
- 02:20 在同一面板內往上捲回 **All 55 inputs & calculation details** 那行，再點一次收合；不要刷新頁面。

**旁白：** All fifty-five contributions are available, with model, calibration, response time, and the held-out result source.

### 02:22–02:35 · S14 · 匯出 Example，準備手動資料

**操作：**

- 02:22 在整頁頂部白色導覽列右側，點 **Export case**（下載箭頭）；瀏覽器會下載 `vesselrisk-patient-evidence.json`，不必開啟檔案。若頂部導覽列不在畫面內，先回頁首。
- 02:24 回頁首，在 **Patient profile** 標題列最右端點 **Expand**，重新展開表單。
- 02:27 在同一標題列右側點 **Import JSON**（上傳箭頭）。Windows 選檔視窗底部「檔案名稱」輸入 `C:\Users\chinh\Desktop\MultimodelAI\demo\CUSTOM_PROFILE_START.json`，點右下角「開啟」。
- 02:32 回到網頁後，點 **Import JSON** 左邊的 **Reset inputs**。確認 Example 下拉不再顯示選定病人，欄位區來源摘要出現 defaults；這次是自訂 profile。

**旁白：** I export the example, then import and reset a blank-identity profile. The second test uses manual inputs.

### 02:35–02:45 · S15 · 清空 Height、BMI 測試

**操作：**

- 02:35 確認表單分組列選 **Key inputs**。在基本資料欄位找到 **Height**，點數字框，Ctrl+A 後按 Backspace 清空。
- 02:37 看表單欄位區右下方：**Predict coronary risk** 變灰，旁邊出現 **Enter a positive height and weight.**。若看不到按鈕，只捲到表單底部，不切換分組。
- 02:39 回到 **Height** 的空框，輸入 `160`。
- 02:41 點它旁邊的 **Weight**，Ctrl+A 輸入 `60`。
- 02:43 指 **Weight** 旁邊的唯讀 **BMI** 框：自動顯示 `23.44`；Predict 恢復可點。

**旁白：** An empty height blocks prediction. Restoring height and weight automatically recalculates BMI.

### 02:45–02:55 · S16 · 錯誤資料與修正

**操作：**

- 02:45 在同一個 Key inputs 區的 **Age** 數字框，Ctrl+A 輸入 `999`。
- 02:47 點表單右下方 **Predict coronary risk**。
- 02:50 看 **Patient profile 上方、整頁導覽列下方** 出現的紅色錯誤橫條；把游標移到錯誤文字。若視窗在表單下半部，往上捲到紅條。
- 02:52 點紅色錯誤橫條最右端的 **×** 關閉錯誤。
- 02:53 回到 Key inputs 的 **Age** 框，Ctrl+A 輸入 `90`。

**旁白：** Age nine hundred ninety-nine is rejected by the API. I correct it to ninety.

### 02:55–03:15 · S17 · 手動資料：基本資料與生命徵象

**操作：**

- 02:55 留在 **Patient profile → Key inputs**；確認基本資料的 **Age** 是 `90`。
- 02:57 點 **Age** 旁邊的 **Sex** 下拉，選 **Female**。
- 03:00 查看基本資料的 **Height 160／Weight 60／BMI 23.44**，不需重新輸入。
- 03:03 找到 **Diabetes** 下拉，選 **No**。
- 03:06 找到 **Hypertension** 下拉，選 **Yes**。
- 03:09 找到 **Systolic blood pressure**（單位 mmHg），點數字框，Ctrl+A 輸入 `145`。
- 03:12 找到 **Pulse rate**（單位 bpm），Ctrl+A 輸入 `76`。這些欄位都在 Key inputs，不用到 History 或 Symptoms。

**旁白：** This synthetic profile is a ninety-year-old woman, one hundred sixty centimeters, sixty kilograms, with hypertension and no diabetes. Blood pressure is one hundred forty-five; pulse, seventy-six.

### 03:15–03:35 · S18 · 手動資料：主要檢查

**操作：**

- 03:15 仍在 **Key inputs**，找到 **Typical Chest Pain** 下拉，選 **No**；必要時在表單欄位區往下捲一點。
- 03:18 在 **Fasting blood sugar**（FBS，mg/dL）數字框，Ctrl+A 輸入 `100`。
- 03:21 在 **LDL cholesterol** 數字框，Ctrl+A 輸入 `110`。
- 03:24 在 **HDL cholesterol** 數字框，Ctrl+A 輸入 `50`。
- 03:27 在 **Ejection fraction**（%）數字框，Ctrl+A 輸入 `55`。
- 03:31 在 **RWMA region code** 下拉，選 **0**。此時不要點 Predict。

**旁白：** I enter no typical chest pain, fasting glucose one hundred, LDL one hundred ten, HDL fifty, ejection fraction fifty-five, and RWMA category zero.

### 03:35–03:44 · S19 · History 與欄位來源

**操作：**

- 03:35 在 Patient profile 上方的分組列，點 **History**。
- 03:36 在 History 欄位找到 **Current Smoker** 下拉，選 **No**。
- 03:38 找到 **EX-Smoker** 下拉，選 **No**。
- 03:40 找到 **Obesity** 下拉，選 **No**；不是改 BMI。
- 03:42 游標停在 **Family history** 的欄位標題上，稍等顯示來源提示；不修改這個欄位。

**旁白：** I check smoking and obesity, and inspect the source of the remaining default values.

### 03:44–03:54 · S20 · Symptoms、ECG、Labs 與未套用提示

**操作：**

- 03:44 點表單分組列的 **Symptoms**，用游標掃過下方欄位，保留目前值。
- 03:46 同一排點 **ECG**，展示 Q Wave、ST、T-wave 等欄位，不改值。
- 03:48 同一排點 **Labs & echo**。
- 03:49 在這一組找到 **Valvular heart disease**（VHD）下拉，選 **No**；如在欄位下方，捲表單欄位區找到它。
- 03:51 在表單外往下捲到心臟右側結果面板的上緣，看黃色 **Previous explanation** 提示；再指頁首 **Export case** 的停用狀態。這表示新輸入還沒套用。

**旁白：** I review the remaining groups. Edited inputs mark the previous explanation as stale and block export until prediction.

### 03:54–04:07 · S21 · 第二輪有效預測

**操作：**

- 03:54 回到 **Patient profile 表單底部** 的深藍色 **Predict coronary risk** 按鈕並點擊；不是按右側的機率頁籤。
- 結果完成、表單收合後，立即在整頁空白處往下捲到心臟；先看血管浮動標籤上短暫出現的 **vs last** 差值，不要等它消失才找。
- 04:01 點右側 **Coronary Risk Prediction** 下的 **CAD** 機率頁籤。確認四值為 **87.1／30.4／37.9／47.5%**。
- 04:03 在右側 **Top influences** 下方找黃色 **Unusual patient profile** 警示，指文字；必要時在右側說明面板內往下捲。年齡 `90` 是你剛輸入的值，這個警示本身不會列出 Age 數字。

**旁白：** The new profile returns fresh probabilities. Age ninety triggers a warning because it exceeds the observed cohort age range.

### 04:07–04:18 · S22 · 新 profile 的模型、下載

**操作：**

- 04:07 在右側說明面板 **Across fitted models** 標題下方，指 **10 fitted models**；這次不是 Example 的 2 fitted models。
- 04:09 在同一面板下方點 **All 55 inputs & calculation details** 展開；游標留在面板內，往下捲過 55 項貢獻到最底部。
- 04:12 指最底部 **Result source: new profile**，以及下一段 **This profile uses a model fitted on the full cohort.**。
- 04:14 點整頁頂部導覽列右側 **Export case**，下載第二輪 JSON；若導覽列不在畫面內，先回頁首。
- 04:16 回頁首，讓頂部 **Patient workspace／Model evidence** 導覽按鈕可見。

**旁白：** This profile uses the full-cohort model. Ten fitted models show variation, and I export the complete case.

### 04:18–04:31 · S23 · Model evidence：Overview

**操作：**

- 04:18 點整頁頂部白色導覽列中央的 **Model evidence**（燒瓶圖示），不是心臟旁的資訊按鈕。進入後左邊會有五項直式選單，預設選 **Overview**。
- 04:20 在右邊 Overview 內容的最上方，找到 **From data to evaluated predictions**；游標由左至右掃過四個流程區塊。
- 04:23 在整頁往下捲一點，到 **Four targets. One evaluation protocol.** 表格；從左邊 CAD／LAD／LCX／RCA 四列，向右指 ROC-AUC、Recall、Brier、Missed positives 欄。此時只看，不點右端箭頭。

**旁白：** Model evidence makes the evaluation inspectable: the workflow, four targets, discrimination, calibration, and missed positives.

### 04:31–04:40 · S24 · Overview 切換、進 Validation

**操作：**

- 04:31 在 Overview 整頁繼續往下捲，到 **Four targets, one view.** 的四列圖表。
- 04:33 在這個圖表標題的右邊，點 **Recall at 0.50**。
- 04:35 點旁邊 **ROC-AUC**，切回 AUC 圖。
- 04:37 點下方圖表第一列 **CAD**（整條都可點），進入 **Validation**；不是回 Patient workspace 點 CAD。

**旁白：** The overview switches between recall and AUC. Selecting a target opens its validation evidence.

### 04:40–04:50 · S25 · 四目標 Validation

**操作：**

- 04:40 在 Model evidence 的 **Validation** 內容回頂，找到右側內容頂部的 **CAD／LAD／LCX／RCA** 四按鈕列；目前應是 CAD。先看標題下方 Held-out ROC-AUC 和指標。
- 04:42 在這列點 **LAD**。
- 04:44 同一列點 **LCX**。
- 04:46 同一列點 **RCA**。
- 04:48 同一列回 **CAD**；這是 Evidence target，沒有病人機率數字。

**旁白：** Each target has separate metrics, fold variation, and uncertainty estimates from nested validation.

### 04:50–05:00 · S26 · ROC、PR、Calibration

**操作：**

- 04:50 在 Validation 整頁往下捲，越過 ROC-AUC／指標摘要與說明，到同一排的三個圖表。
- 04:52 游標移到左圖 **ROC curve** 的實線附近，停一下看數值提示，不要點。
- 04:54 游標移到中圖 **Precision–recall** 曲線，展示提示。
- 04:56 游標移到右圖 **Calibration curve** 的圓點上，展示提示。
- 04:58 游標移到三圖外的空白處，讓提示消失。

**旁白：** Interactive ROC, precision-recall, and calibration plots expose the underlying evaluation points.

### 05:00–05:12 · S27 · 校準明細與基準

**操作：**

- 05:00 在三圖正下方，點帶小三角形的 **Calibration evidence · patient counts, intervals & baseline** 文字列展開。
- 05:02 在展開表格中，指 **Positive / patients** 與最右欄 **Descriptive 95% interval**。
- 05:05 在整頁往下捲一點，到表格下面的 **Brier** 和 **Training-prevalence baseline** 那段。
- 05:08 再稍微往下，到 **Each repeat before averaging**，指 Repeat 1、Repeat 2 表格。
- 05:10 往上捲回這個展開區的標題，點同一行 **Calibration evidence…** 收合。

**旁白：** Calibration details include patient counts, intervals, a training baseline, and results before averaging the repeated validation runs.

### 05:12–05:22 · S28 · LCX 候選模型與混淆矩陣

**操作：**

- 05:12 回 Validation 內容頂部，在 **Evidence target** 四按鈕列選 **LCX**。
- 05:14 整頁往下捲過三圖和已收合的 Calibration evidence，到左右並排的 **Model comparison／Confusion matrix**。
- 05:16 指左邊 Model comparison 表格的模型列，以及最下面 **Nested selection policy**。
- 05:18 指右邊 Confusion matrix 四格：左上 **154 True negatives**、右上 **30 False positives**、左下 **69 False negatives**、右下 **50 True positives**。

**旁白：** Candidate comparison and the confusion matrix show exactly where the LCX classifier succeeds and makes errors.

### 05:22–05:31 · S29 · 校準敏感度與驗證方法

**操作：**

- 05:22 在剛才混淆矩陣下方，繼續往下捲到下一組左右並排的 **Calibration sensitivity／Validation protocol**。
- 05:24 指左邊表格 **Raw／Sigmoid · deployed／Isotonic** 三列。
- 05:27 指右邊 **Outer evaluation／Inner selection／Selection score／Calibration／Seed / threshold**。這些是文字與數字，不需要點按鈕。

**旁白：** Raw and calibrated results are compared alongside the nested selection protocol and reproducible seed.

### 05:31–05:41 · S30 · LCX 門檻測試

**操作：**

- 05:31 在 Validation protocol 下方，往下捲到 **Research operating thresholds**，保持 LCX 選取。
- 05:33 看這區的 **Missed positives** 圖，指 **Fixed 0.50** 與 **Training-selected F1** 比較的 `69 → 19`。
- 05:36 看旁邊 **False positives** 圖，指 `30 → 93`。
- 05:38 指各 operating point 的 Recall 數值約 `42% → 84%`。這一區是比較圖，沒有要你拖動的門檻滑桿。

**旁白：** For LCX, an alternative research threshold reduces misses from sixty-nine to nineteen, while increasing false positives.

### 05:41–05:51 · S31 · RCA 門檻與精確表

**操作：**

- 05:41 回 Validation 內容頂部，在 Evidence target 四按鈕列選 **RCA**。
- 05:43 整頁往下捲回 **Research operating thresholds**；標題上方仍是模型比較、校準敏感度等內容。
- 05:45 指 RCA 圖裡的 missed positives `69 → 15`、false positives `34 → 101`。
- 05:47 在比較圖下面點 **▸ All operating points & exact metrics** 展開。
- 05:49 指展開表格的四列，以及最右邊 **FP / FN** 欄；不用更改數字。

**旁白：** RCA shows the same tradeoff. The exact table preserves each operating point; workspace classification remains at fifty percent.

### 05:51–05:59 · S32 · ExtraTrees／SVM 與十折明細

**操作：**

- 05:51 點同一行 **All operating points & exact metrics** 收合。
- 05:52 在它下方找到 **▸ Bounded ExtraTrees / SVM experiment and threshold method**，點開，指 Policy / family、AUC、Brier 表格。
- 05:54 點同一行收合。
- 05:55 再往下到 **▸ Inspect all 10 outer folds and selected model families**，點開。
- 05:57 指表格的 **Train / test**、**Selected model** 欄，展示不同 fold 的資料數和模型。

**旁白：** Additional model experiments and all ten outer folds are available for inspection.

### 05:59–06:13 · S33 · Interpretability：全局與穩定性

**操作：**

- 05:59 在 Model evidence **左側直式選單** 點 **Interpretability**，再回內容頂部。頂部 Evidence target 保持 **RCA**；若不是 RCA，點 RCA。
- 06:01 在右邊內容左半部 **Global feature contributions**，指前 15 項水平長條。
- 06:03 指內容右半部 **Explanation consistency** 的 `0.730`，再指下面 **Held-out explanations 60**、**Background 16 patients**。
- 06:05 在這組左右內容下方，點 **▸ Local explanation stability · 4 held-out profiles** 展開。
- 06:07 指展開表格第一欄中 seed、computation、background 三種比較。
- 06:10 指同一表格最右欄 **Largest contribution change** 的 `8.4 pp`。

**旁白：** Global SHAP ranks influential inputs. Stability tests compare changed seeds, computation budgets, and backgrounds, including the largest observed change.

### 06:13–06:26 · S34 · Robustness：分組、消融、失敗案例

**操作：**

- 06:13 在 **左側直式選單** 點 **Robustness**，回內容頂部；在右上 Evidence target 四按鈕列點 **LAD**。
- 06:15 指左半部 **Subgroup checks** 表格中的 Sex、Age 分組列。
- 06:17 指右半部 **Feature-group ablation** 表格的 **ECG／Laboratory & echo** 列。
- 06:19 整頁往下到 **Where the model failed** 表格；指前兩列的 **Observed／Estimated probability**：Negative／92.1%，Positive／8.2%。
- 06:23 再往下到 **Limits that matter**，讓限制清單進入畫面。

**旁白：** Robustness includes subgroup checks, feature ablations, and actual false positives and false negatives. The page also states the study limitations.

### 06:26–06:42 · S35 · Data & provenance、Registry、素材、下載

**操作：**

- 06:26 在 **左側直式選單** 點 **Data & provenance**，回內容頂部。
- 06:28 指左半部 **Dataset provenance** 的 **Records / source columns 303 / 59**、**Eligible clinical inputs 55**、**Missing / duplicate records 0 / 0**。
- 06:30 指左下 **Positive label distribution**；再指右半部 **Leakage audit** 的四個排除標籤，以及下面 **Invalid identity predictor／1.000 AUC／BLOCKED**。
- 06:33 整頁往下到 **Reproducible model registry**；指表格的 Deployed family、Parameters、Artifact SHA-256，再指表格下方的軟體版本小標籤。
- 06:36 再往下到 **Real reference anatomy, honest mapping**，點下面的 **Inspect exact source revision & mesh mapping ↗**；Chrome 新分頁顯示 JSON。
- 06:38 Ctrl+W 關閉這個新分頁，回 Model evidence。
- 06:39 回頁首，在整頁頂部導覽列右側點 **Export evidence**，下載 `vesselrisk-evidence.json`。

**旁白：** Provenance covers the dataset, leakage checks, model parameters, hashes, software versions, and anatomy sources. The evidence can be downloaded.

### 06:42–06:52 · S36 · Scope 與六頁報告

**操作：**

- 06:42 在整頁頂部導覽列最右邊、**Export evidence** 右側，點單獨的圓圈 **i**，開啟 Scope & limitations 對話框。
- 06:44 看中央彈窗 **Evidence before confidence.** 下的研究用途與限制說明。
- 06:46 在彈窗底部點 **Technical report**（書本圖示）；不是左邊的 Inspect validation。Chrome 會另開 PDF 分頁。
- 06:48 在 PDF 檢視器上方工具列，指目前頁數／總頁數中的 **6**，讓報告首頁維持可見。

**旁白：** The scope panel links the six-page technical report, including methods, results, and limitations.

### 06:52–07:00 · S37 · 回到第二輪結果，結束

**操作：**

- 06:52 Ctrl+W 關閉 PDF 分頁，回到仍開著 Scope 彈窗的 VesselRisk 分頁。
- 06:53 點中央 Scope 彈窗**右上角 ×**，關閉彈窗。
- 06:54 點整頁頂部導覽列中央的 **Patient workspace**，回第二輪病人結果。
- 06:56 若右側 **All 55 inputs & calculation details** 還展開，先在面板內捲回那行並點它收合；再在整頁空白處捲到左邊心臟、右邊四機率同時可見。
- 07:00 停止錄影。

**旁白：** The case remains available. VesselRisk combines prediction, anatomy, explanations, and reproducible evidence for research.

<details>
<summary>第二輪完整 55 欄（錄影前對照）</summary>


## 第二輪完整55欄資料

這是假設的功能／表示範圍測試，不具有臨床ground truth。年齡90合法（API允許18–110），但超出訓練資料最高86，刻意用來展示OOD提示。不能據此宣稱預測正確。第一輪是59歲男性example（id115），第二輪必須case_id=null。

值為「保留預設」的欄位在影片中逐組查看，不做虛構量測。BMI必須由160cm與60kg算得23.4375，畫面顯示23.44。不要把報告或patient結果中的50% cutoff當成血管狹窄程度。

| 分組 | UI欄名（原始key） | 最終值 | 操作／來源 |
|---|---|---|---|
| Demographics & history | Age (`Age`) | 90 | 本輪指定／確認；未改值可保留預設 |
| Demographics & history | Weight (`Weight`) | 60 | 本輪指定／確認；未改值可保留預設 |
| Demographics & history | Height (`Length`) | 160 | 本輪指定／確認；未改值可保留預設 |
| Demographics & history | Sex (`Sex`) | Female | 本輪指定／確認；未改值可保留預設 |
| Demographics & history | BMI (`BMI`) | 23.44（內部23.4375） | 自動計算／唯讀 |
| Demographics & history | Diabetes (`DM`) | No | 本輪指定／確認；未改值可保留預設 |
| Demographics & history | Hypertension (`HTN`) | Yes | 本輪指定／確認；未改值可保留預設 |
| Demographics & history | Current Smoker (`Current Smoker`) | No | 本輪指定／確認；未改值可保留預設 |
| Demographics & history | EX-Smoker (`EX-Smoker`) | No | 本輪指定／確認；未改值可保留預設 |
| Demographics & history | Family history (`FH`) | No | 保留預設／逐組檢查 |
| Demographics & history | Obesity (`Obesity`) | No | 本輪指定／確認；未改值可保留預設 |
| Demographics & history | Chronic renal failure (`CRF`) | No | 保留預設／逐組檢查 |
| Demographics & history | Cerebrovascular history (`CVA`) | No | 保留預設／逐組檢查 |
| Demographics & history | Airway disease (`Airway disease`) | No | 保留預設／逐組檢查 |
| Demographics & history | Thyroid Disease (`Thyroid Disease`) | No | 保留預設／逐組檢查 |
| Demographics & history | Heart failure history (`CHF`) | No | 保留預設／逐組檢查 |
| Demographics & history | Dyslipidemia (`DLP`) | No | 保留預設／逐組檢查 |
| Symptoms & examination | Systolic blood pressure (`BP`) | 145 | 本輪指定／確認；未改值可保留預設 |
| Symptoms & examination | Pulse rate (`PR`) | 76 | 本輪指定／確認；未改值可保留預設 |
| Symptoms & examination | Edema (`Edema`) | No | 保留預設／逐組檢查 |
| Symptoms & examination | Weak Peripheral Pulse (`Weak Peripheral Pulse`) | No | 保留預設／逐組檢查 |
| Symptoms & examination | Lung rales (`Lung rales`) | No | 保留預設／逐組檢查 |
| Symptoms & examination | Systolic Murmur (`Systolic Murmur`) | No | 保留預設／逐組檢查 |
| Symptoms & examination | Diastolic Murmur (`Diastolic Murmur`) | No | 保留預設／逐組檢查 |
| Symptoms & examination | Typical Chest Pain (`Typical Chest Pain`) | No | 本輪指定／確認；未改值可保留預設 |
| Symptoms & examination | Dyspnea (`Dyspnea`) | No | 保留預設／逐組檢查 |
| Symptoms & examination | Function Class (`Function Class`) | 0 | 保留預設／逐組檢查 |
| Symptoms & examination | Atypical (`Atypical`) | No | 保留預設／逐組檢查 |
| Symptoms & examination | Nonanginal (`Nonanginal`) | No | 保留預設／逐組檢查 |
| Symptoms & examination | Exertional CP (`Exertional CP`) | No | 保留預設／逐組檢查 |
| Symptoms & examination | LowTH Ang (`LowTH Ang`) | No | 保留預設／逐組檢查 |
| ECG | Q Wave (`Q Wave`) | No | 保留預設／逐組檢查 |
| ECG | ST elevation (`St Elevation`) | No | 保留預設／逐組檢查 |
| ECG | ST depression (`St Depression`) | No | 保留預設／逐組檢查 |
| ECG | T-wave inversion (`Tinversion`) | No | 保留預設／逐組檢查 |
| ECG | Left ventricular hypertrophy (`LVH`) | No | 保留預設／逐組檢查 |
| ECG | Poor R Progression (`Poor R Progression`) | No | 保留預設／逐組檢查 |
| ECG | Bundle branch block (`BBB`) | No | 保留預設／逐組檢查 |
| Laboratory & echo | Fasting blood sugar (`FBS`) | 100 | 本輪指定／確認；未改值可保留預設 |
| Laboratory & echo | Creatinine (`CR`) | 1 | 保留預設／逐組檢查 |
| Laboratory & echo | Triglycerides (`TG`) | 122 | 保留預設／逐組檢查 |
| Laboratory & echo | LDL cholesterol (`LDL`) | 110 | 本輪指定／確認；未改值可保留預設 |
| Laboratory & echo | HDL cholesterol (`HDL`) | 50 | 本輪指定／確認；未改值可保留預設 |
| Laboratory & echo | Blood urea nitrogen (`BUN`) | 16 | 保留預設／逐組檢查 |
| Laboratory & echo | ESR (`ESR`) | 15 | 保留預設／逐組檢查 |
| Laboratory & echo | Hemoglobin (`HB`) | 13.2 | 保留預設／逐組檢查 |
| Laboratory & echo | Potassium (`K`) | 4.2 | 保留預設／逐組檢查 |
| Laboratory & echo | Sodium (`Na`) | 141 | 保留預設／逐組檢查 |
| Laboratory & echo | White blood cells (`WBC`) | 7100 | 保留預設／逐組檢查 |
| Laboratory & echo | Lymphocytes (`Lymph`) | 32 | 保留預設／逐組檢查 |
| Laboratory & echo | Neutrophils (`Neut`) | 60 | 保留預設／逐組檢查 |
| Laboratory & echo | Platelets (`PLT`) | 210 | 保留預設／逐組檢查 |
| Laboratory & echo | Ejection fraction (`EF-TTE`) | 55 | 本輪指定／確認；未改值可保留預設 |
| Laboratory & echo | RWMA region code (`Region RWMA`) | 0 | 本輪指定／確認；未改值可保留預設 |
| Laboratory & echo | Valvular heart disease (`VHD`) | No | 本輪指定／確認；未改值可保留預設 |


</details>

<details>
<summary>功能與參考圖對照</summary>


| 功能 | 時間 |
|---|---|
| 啟動、Example、全部輸入、搜尋、重設 | 00:00–00:47 |
| 四機率、CAD 提示、三種目標選取、所有 3D 控制與解剖說明 | 00:47–01:50 |
| SHAP、pp、候選模型、重訓範圍、55 項貢獻 | 01:50–02:22 |
| JSON 匯出／匯入、BMI、前後端驗證、手動資料、stale、OOD、新 profile | 02:22–04:18 |
| Overview、四目標、ROC／PR／Calibration、校準明細 | 04:18–05:12 |
| 候選模型、混淆矩陣、校準敏感度、thresholds、ExtraTrees／SVM、十折 | 05:12–05:59 |
| 全局解釋、穩定性、subgroup、ablation、失敗案例與限制 | 05:59–06:26 |
| 資料、leakage、registry、素材來源、下載、scope、報告、返回 workspace | 06:26–07:00 |



| 參考圖 | 段落 |
|---|---|
| image.png | S23 |
| image copy.png / image copy 2.png | S24 |
| image copy 3.png / image copy 4.png | S25–S26 |
| image copy 5.png | S28–S29 |
| image copy 6.png | S30 |
| image copy 7.png | S31–S32 |
| image copy 8.png | S32 |
| image copy 9.png / image copy 10.png | S33 |
| image copy 11.png / image copy 12.png | S34 |
| image copy 13.png / image copy 14.png / image copy 15.png | S35 |
| image copy 16.png | S14、S22 |


</details>

官方要求：影片 3–10 分鐘、英文語音或字幕、公開 GitHub、報告最多六頁。[競賽規則](https://multimodal-ai-hackathon-2026-7.devpost.com/rules) · [提交指南](https://drive.google.com/file/d/1HEy6MBO_BN_aID2Nik2woYLWfuawzwHN/view)。

兩份測試資料與 15 組真實 API 桌面彩排結果保留在 [DEMO_REHEARSAL.json](DEMO_REHEARSAL.json)。這次只改錄影編排；7 分鐘的真人操作與配音尚未彩排。
