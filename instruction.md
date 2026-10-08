可以。先把目標定義得很清楚：不是「做完 Track A」，而是做一個讓評審很難把你歸類成普通 Codex/vibe-coded 專案的 Track A submission。 第一名沒有人能保證，但照今年官方評分表、去年公開得獎作品的完成度，我會把下面這套當成「衝 Track A 第一」的初始規格，而不是 MVP。
1. 你現在應該知道的比賽事實
今年是 15 天開發期：9/30–10/14 EOD，10/15–20 評審，10/21 Final Showcase / winner announcement；允許 solo 到 4 人，一個人只能加入一個 submitting team，而且一隊只能投一個 Track。AI coding assistants 沒有使用限制，官方甚至明列 Cursor、Claude Code、Copilot、ChatGPT、v0，但必須在 Built With / README 揭露 AI 協助部分，而且被問到時你必須能解釋程式。
Devpost 目前顯示 1,147 participants，但這只是註冊人數，不代表 1,147 組會提交，更不代表都選 A。活動仍標示 Fully online，而且目前 judges 還是「To be announced」。
有一個官方資訊衝突你要知道：你下載的 Prize Pool PDF 寫的是每 Track 第一 ₹15,000、第二 ₹10,000，四軌共 ₹100,000。 但 Devpost 現在則寫 one winner per track / 4 winners total，Overview 顯示每個 Track winner ₹25,000。 這顯然需要主辦方在 Discord 澄清；反正你的目標是第一，暫時不影響開發策略。
2. Track A 本質到底是什麼
不是 CT、MRI、angiography image segmentation，也不是自己做醫療影像模型。
官方要你從 病人的結構化臨床資料預測：
Overall CAD + LAD stenosis + LCX stenosis + RCA stenosis
接著把 LAD / LCX / RCA 的 predicted probability 映射到互動式 3D heart / torso，並用 SHAP/LIME 等方式說明模型為什麼作出這個判斷。 
資料是 demographic、clinical examination、ECG 的已整理特徵、laboratory、echocardiographic features；不是 raw ECG waveform，也沒有 3D lesion coordinate。官方甚至特別警告 RWMA 只是一個 clinical feature，不能假裝它代表 3D 病灶位置。
所以正確概念是：
Patient clinical features
          │
          ▼
     ML predictors
 ┌────┬────┬────┬────┐
 CAD  LAD  LCX  RCA
 └────┴────┴────┴────┘
          │
   calibrated probability
          │
      ┌───┴────┐
      ▼        ▼
    SHAP     3D heart
 explain     vessel mapping
      └───┬────┘
          ▼
 Clinical decision-support UI
3. 你的主要資料完全公開，大家基本拿到一樣的起跑線
官方推薦的是 UCI Extension of Z-Alizadeh Sani Dataset：303 patients、59 features，並包含 overall CAD 以及 LAD、LCX、RCA vessel labels。
UCI 官方確認它是 tabular classification dataset、303 records、無 missing values，資料分成 demographic、symptom/examination、ECG、laboratory/echo 四類，授權 CC BY 4.0，可以直接下載 XLSX。
公開研究使用這個資料系列時報告約 216 CAD / 87 Normal，所以至少 overall CAD 有明顯 class imbalance；不能只看 accuracy。
最重要的紅線：leakage
今年官方比原 UCI 說明更嚴格：
預測 CAD 或任何 vessel stenosis 時，LAD、LCX、RCA、Cath 全部不得作為 input features。

也就是 Codex 一開始就要有一個硬性的 LeakageGuard。不允許任何 preprocessing / feature-selection / training pipeline 把這四欄偷偷帶進 X。
我甚至會刻意做一個 leakage demo：
INVALID pipeline
includes Cath/LAD/LCX/RCA
AUC → 異常漂亮

VALID pipeline
removes all forbidden variables
AUC → 真實結果
這不是搞笑功能。它會直接讓評審看到你知道什麼叫可信的 medical ML。
4. 額外資料要不要找？
完成題目不需要。
而且一開始不要為了「資料越多越厲害」亂 merge Cleveland / Statlog 等 heart-disease datasets。那些資料欄位不一致，而且大部分根本沒有 LAD / LCX / RCA vessel-level ground truth。
高規格版本可以後期做一個 external robustness experiment：取另一公開 CAD dataset 與本資料共同存在的 feature subset，另外訓練一個 reduced-feature overall-CAD model，看看 generalization。但它應該是 bonus，不是主模型。
不要把不相容 datasets 混在一起假裝 N 變大。
5. 去年冠軍告訴我們的真正門檻
2025 是全場總排行，不是今年這種 A/B/C/D 各 Track。官方公布 250+ participants，第一名 Team Ult4 — Smart Scribe，後面是 From Bavaria、SafeCity、ControlScape、YogMaya。
第一名 Smart Scribes 公開 repo 不是只有一張投影片。他們公開了 Demo video、Presentation、Documentation Hub、Installation Guide、原始碼；repo 內有 Python multimodal pipeline、audio/frame/PDF processing、embeddings、Next.js frontend、API routes、Supabase 等。
第五名 YogMaya 的公開 repo 甚至把 30 FPS、<200 ms feedback、87% average pose accuracy 這種 benchmark 數字直接展示出來，還有 real-time pose detection、multimodal interaction、RAG memory。
這裡我會保守一點：公開 repo 可能在賽後有更新，所以不能說今天看到的每一行 code 都是當時 submission snapshot。但它足以告訴我們一件事：
去年會進前段的作品，不是「功能清單很多」，而是看起來像真的完整產品，而且能拿出技術 pipeline、實際 demo、量化結果與文件。

今年所有人又都有 Claude/Codex，所以「React 很漂亮、API 有串起來」已經只能算基本分。
6. 今年 A 想衝第一，我會把內部標準拉到這裡
官方權重就是：Predictive Performance 30%、3D Visualization 25%、Clinical Interpretability 20%、System Integration 15%、Technical Implementation 10%。
官方項目	第一名規格，我會要求 Codex 做到
Predictive Performance 30%	4 targets 全做；nested/repeated stratified CV；baseline + model zoo；class imbalance 處理只發生在 training fold；hyperparameter tuning；calibration；ROC-AUC/F1/precision/recall/accuracy + PR-AUC/Brier；mean±SD/CI；confusion matrix；ablation；leakage audit
3D Visualization 25%	真正能分別控制 LAD/LCX/RCA 的 anatomical mesh；smooth rotate/zoom/select；風險動態著色；點 artery 展開 probability、uncertainty、explanation；正常瀏覽器 GPU-free 順跑
Interpretability 20%	Global SHAP + patient-level local SHAP；不同 target 各自 explanation；feature group；跨 fold SHAP stability；model agreement；plain-language clinical explanation；明確顯示 uncertainty，不把相關性包裝成因果
System Integration 15%	Patient input → API → 4 predictions → calibration → SHAP → 3D update 全部一次完成；不用手動跑 notebook；case switching 無 reload；model/version/provenance 全部可追
Technical 10%	一鍵啟動；Docker；typed API schema；tests；CI；固定 seed/environment；model registry/hash；data/model card；license attribution；完整 README；failure mode documentation


這才是我心中的「第一名候選」，不是單純 XGBoost + Three.js。
其中 Predictive Performance 的重點不是硬追一個神奇的 95% accuracy。303 人的小資料，一個誠實的 repeated/nested CV + confidence interval + calibration，會比一個可疑的 97% train/test split 更有說服力。
7. 我會把模型層做到多狠
不是只 train XGBoost。
Codex 建：
                  RAW UCI DATA
                       │
             Schema + Leakage Audit
                       │
          ┌────────────┴─────────────┐
          │ 4 independent targets   │
          │ CAD / LAD / LCX / RCA   │
          └────────────┬─────────────┘
                       │
          Repeated / Nested Stratified CV
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
 Logistic Reg.    Random Forest   XGBoost/LightGBM
        │              │              │
        └──────────────┼──────────────┘
                       ▼
             probability calibration
            Platt / isotonic comparison
                       │
                       ▼
             per-target best model
             or calibrated ensemble
                       │
        ┌──────────────┼───────────────┐
        ▼              ▼               ▼
     Metrics         SHAP        uncertainty/OOD
我還會要求：
baseline 一定存在。 Logistic Regression 就是 sanity baseline。
所有 preprocessing、feature selection、oversampling、tuning 都在 CV fold 裡。 絕對不能先對全資料做 feature selection 或 SMOTE 再 CV。
Probability 要 calibration。 題目寫的是 risk estimation quality，不只是「有病 / 沒病」。
Uncertainty 不要裝神。 可以做 model disagreement、cross-validation dispersion、簡單 OOD detector；如果病人的 feature profile 離 training population 太遠，就直接顯示：
Limited confidence — this profile is poorly represented in the training cohort.

這其實非常符合只有 303 人的小樣本現實。
8. 3D 不要只是「整顆心變紅」
這會是你的 Demo 記憶點。
你要先找 LAD、LCX、RCA 能獨立成 mesh/object 的模型。如果找到的模型只有一整顆 heart，寧願前兩天就進 Blender 拆好，不要到最後才發現 Three.js 根本沒辦法選 artery。
官方允許 BodyParts3D 或公開 .gltf/.glb/.obj，也明確允許 Three.js / WebGL / React Three Fiber / VTK.js。 
最高規格 UI，我會做：
LEFT                        CENTER                    RIGHT
Patient data          Interactive 3D Heart       Evidence Panel
────────────────      ────────────────────       ───────────────
Age                   CAD overall risk           LAD 82%
BP                    LAD highlighted            calibrated
Cholesterol           LCX                        confidence
ECG features          RCA                        model agreement
Echo features         rotate / zoom / click      SHAP contributors
                                                  model limitations
選 LAD，只有 LAD 被強調；右邊立刻切到 LAD predictor 的 evidence。
切 RCA，就切 RCA 的 SHAP、probability、confidence。
不要把 artery 上某個位置畫成「病灶點」，因為資料根本沒有 lesion coordinate。應該標成 vessel-level predicted stenosis risk。這個科學誠實度反而會加分。
9. 再多做一個普通參賽者很少做的頁面：Model Evidence Lab
這頁不面向一般病人，是直接面向評審。
評審點進去會看到：
DATA
303 patients
data provenance
class distribution
forbidden-feature audit

MODEL
CAD / LAD / LCX / RCA
model selected
hyperparameters
model hash

VALIDATION
Repeated CV
ROC / PR
confusion matrix
calibration curve
Brier score
95% interval

ROBUSTNESS
subgroup checks
model disagreement
OOD cases
failure cases

EXPLAINABILITY
global SHAP
local SHAP
SHAP stability
這頁就是你跟「Codex 幫我做一個醫療 dashboard」最大的差異。
10. Clinical Interpretability 也要往上拉一層
我不只做：
Age +0.16
Cholesterol +0.09

我要 UI 能回答：
「這個結果為什麼高？」
「哪個 target 的原因？」
「三個模型同不同意？」
「模型自己有多確定？」
「這個病人是不是 training data 幾乎沒看過的類型？」
但不要做「如果你把 cholesterol 降 30 就可以降低真實疾病 12%」這種假因果。最多叫 model sensitivity explorer，明確寫「model response, not clinical treatment effect」。
11. 高規格但我反而不想要的功能
LLM chatbot、voice assistant、登入系統、社群、hospital database、用 AI 自動寫診斷書、raw ECG waveform、CT segmentation……
只要官方沒給分，就不要因為「AI 看起來比較多」而犧牲 validation。
你的賣點應該是：
This is not another AI-generated medical dashboard. Every risk estimate is leakage-audited, calibrated, uncertainty-aware, anatomically mapped, and traceable to validation evidence.

這一句就已經比「我們用了 8 個 AI API」強很多。
12. 最終 Demo 應該給評審看到什麼
前三十秒，不講技術名詞。選一個 sample patient → Predict。
畫面出現：
Overall CAD       HIGH
LAD               84%
LCX               27%
RCA               61%
3D heart 同時更新。
點 LAD。
出現：
LAD stenosis estimate: 84%
Confidence: Moderate

Top contributing features
ST Elevation
RWMA
Age
T Inversion

Model agreement
Logistic    77%
RF          84%
XGBoost     89%

⚠ Decision-support only
接著 30 秒切 Model Evidence Lab：
「這不是單次 random split。這些結果來自 repeated/nested validation；所有 LAD/LCX/RCA/Cath 都在 preprocessing 前被 leakage guard 排除；以下是 calibration 與 confidence intervals。」

最後才講 architecture。
這會比從「我們使用 Next.js、FastAPI、XGBoost……」開始有殺傷力得多。
13. Codex 的最高規格初始架構
我會直接把 repo 定死成：
vesselrisk/
├── data/
│   ├── raw/
│   ├── processed/
│   └── data_dictionary/
├── ml/
│   ├── schema/
│   ├── leakage_guard/
│   ├── preprocessing/
│   ├── training/
│   ├── calibration/
│   ├── evaluation/
│   ├── explainability/
│   ├── uncertainty/
│   └── artifacts/
├── api/
│   ├── predict
│   ├── explain
│   ├── model-info
│   └── health
├── web/
│   ├── patient-input
│   ├── risk-dashboard
│   ├── 3d-heart
│   ├── evidence-lab
│   └── safety
├── assets/
│   └── anatomy/
├── experiments/
├── tests/
├── docs/
├── report/
└── demo/
前端我會選 Next.js + TypeScript + React Three Fiber；ML/API 用 Python + scikit-learn/XGBoost/LightGBM + SHAP + FastAPI。沒有任何理由把大型神經網路塞進來。
官方要求最終至少有 working web prototype、trained model pipeline/weights、clinical explanation dashboard、最多 6 頁 documentation、3–10 分鐘 YouTube demo。
另外，官方要求 3D 在現代瀏覽器保持 responsive，不能依賴 dedicated GPU。
我對「第一名完成度」的底線
到 submission 前，我希望不是「功能全部有」。
而是以下任何一項被評審點開，都沒有明顯洞：
模型可信、3D 有記憶點、解釋有深度、整合像產品、repo 能重現、限制敢講、Demo 完整。
去年第一名已經做到完整 pipeline + frontend + demo + slides + docs；今年又有超過千人註冊、人人能用 Claude/Codex。
所以我們的標準不能是「比去年第一名多一個 feature」，而應該是：
把今年 Track A 的每一個評分項目做到評審找不到明顯弱邊，而且核心可信度是純 vibe coder 最難偽造的東西。

下面我會把這套「最高規格 VesselRisk」架構直接畫成一張正式系統設計圖；圖是視覺摘要，實際開發規格以上面的文字為準。