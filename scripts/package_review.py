"""Create an evidence-first offline review entry and verified complete repo ZIP."""
import csv
import hashlib
import html
import json
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
REVIEW = ROOT / 'review'
OUTPUT = ROOT / 'submission'
from scripts.submission_files import collect_files, validate_required, EXCLUDED_DIRS, EXCLUDED_FILES
METRICS = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc', 'pr_auc', 'brier']
LABELS = ['Accuracy', 'Precision', 'Recall', 'F1', 'ROC-AUC', 'PR-AUC (AP)', 'Brier']


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')


def make_evidence():
    from ml.integrity import verify_manifest
    from ml.reliability import load_verified
    verify_manifest()
    reliability = load_verified()
    if reliability is None:
        raise RuntimeError('Missing or stale reliability evidence; run python -m ml.reliability')
    evidence = json.loads((ROOT / 'ml/artifacts/evidence.json').read_text(encoding='utf-8'))
    registry = json.loads((ROOT / 'ml/artifacts/registry.json').read_text(encoding='utf-8'))
    anatomy = json.loads((ROOT / 'web/public/anatomy/manifest.json').read_text(encoding='utf-8'))
    screenshots = json.loads((REVIEW / 'screenshots/index.json').read_text(encoding='utf-8'))
    assert len(screenshots['captures']) == 11 and not screenshots['browser_errors']
    results = {}
    csv_rows = []
    for target, e in evidence['targets'].items():
        deployed = registry['models'][target]
        results[target] = {key: e[key] for key in ['n', 'positive', 'negative', 'metrics', 'auc_ci', 'dispersion', 'selection_counts', 'calibration_comparison']}
        results[target]['deployed_model'] = deployed
        row = {'target': target, 'deployed_family': deployed['family'], 'deployed_params': json.dumps(deployed['params']),
               'positive_n': e['positive'], 'negative_n': e['negative'], 'auc_ci_low': e['auc_ci'][0], 'auc_ci_high': e['auc_ci'][1]}
        row.update({metric: e['metrics'][metric] for metric in METRICS})
        for metric in METRICS:
            row[f'{metric}_fold_mean'] = e['dispersion'][metric]['mean']
            row[f'{metric}_fold_sd'] = e['dispersion'][metric]['sd']
        tn, fp = e['metrics']['confusion_matrix'][0]
        fn, tp = e['metrics']['confusion_matrix'][1]
        row.update({'TN': tn, 'FP': fp, 'FN': fn, 'TP': tp})
        csv_rows.append(row)
    write_json(REVIEW / 'MODEL_RESULTS.json', {'source': 'Unmodified shipped evidence.json and registry.json', 'protocol': evidence['protocol'], 'targets': results, 'reliability': reliability})
    refinement=json.loads((ROOT/'experiments/vessel_refinement/results.json').read_text(encoding='utf-8'))
    assert refinement['baseline_evidence_sha256']==hashlib.sha256((ROOT/'ml/artifacts/evidence.json').read_bytes()).hexdigest()
    assert refinement['baseline_registry_sha256']==hashlib.sha256((ROOT/'ml/artifacts/registry.json').read_bytes()).hexdigest()
    research_rows=[]
    for t,e in refinement['targets'].items():
        for v in e['variants']:
            m=v['metrics'];matrix=m['confusion_matrix']
            research_rows.append({'target':t,'policy':v['policy'],'point':v['operating_point'],**{k:m[k] for k in METRICS},'TN':matrix[0][0],'FP':matrix[0][1],'FN':matrix[1][0],'TP':matrix[1][1]})
    with (REVIEW/'RESEARCH_THRESHOLDS.csv').open('w',newline='',encoding='utf-8-sig') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(research_rows[0]));writer.writeheader();writer.writerows(research_rows)
    with (REVIEW / 'MODEL_RESULTS.csv').open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0]))
        writer.writeheader(); writer.writerows(csv_rows)

    tables = []
    sections = []

    def table(title, headers, rows):
        tables.extend([f'## {title}', '', '| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|'])
        tables.extend('| ' + ' | '.join(map(str, row)) + ' |' for row in rows)
        tables.append('')
        body = ''.join('<tr>' + ''.join(f'<td>{html.escape(str(cell))}</td>' for cell in row) + '</tr>' for row in rows)
        sections.append(f'<section><h2>{html.escape(title)}</h2><div class="table-wrap"><table><thead><tr>' + ''.join(f'<th>{html.escape(h)}</th>' for h in headers) + f'</tr></thead><tbody>{body}</tbody></table></div></section>')

    table('Deployed models（全 cohort inner selection 後重訓）', ['Target', 'Family', 'Tuned parameters', 'Calibration'],
          [[t, registry['models'][t]['family'], json.dumps(registry['models'][t]['params']), 'Sigmoid / 3-fold'] for t in results])
    table('Primary results（每人兩次 held-out prediction 平均後計算）', ['Target', *LABELS, 'AUC 95% conditional CI'],
          [[t, *[f'{e["metrics"][m]:.6f}' for m in METRICS], f'[{e["auc_ci"][0]:.6f}, {e["auc_ci"][1]:.6f}]'] for t, e in results.items()])
    table('Outer-fold mean ± SD（10 folds；非獨立樣本）', ['Target', *LABELS],
          [[t, *[f'{e["dispersion"][m]["mean"]:.6f} ± {e["dispersion"][m]["sd"]:.6f}' for m in METRICS]] for t, e in results.items()])
    table('Class distribution / confusion matrix（threshold 0.50）', ['Target', 'Positive', 'Negative', 'TN', 'FP', 'FN', 'TP'],
          [[row[k] for k in ['target', 'positive_n', 'negative_n', 'TN', 'FP', 'FN', 'TP']] for row in csv_rows])
    table('Calibration sensitivity / Brier', ['Method', *results.keys()],
          [[method, *[f'{next(v for v in e["calibration_comparison"] if v["method"] == method)["metrics"]["brier"]:.6f}' for e in results.values()]] for method in ['Raw', 'Sigmoid', 'Isotonic']])
    table('Frozen probability-quality diagnostics', ['Target', 'Brier conditional 95% interval', 'Training-prevalence baseline', 'Relative Brier reduction'],
          [[t, ' / '.join(f'{v:.4f}' for v in e['probability']['brier_ci']), f'{e["probability"]["training_prevalence_brier"]:.4f}', f'{e["probability"]["brier_skill"]*100:.1f}%'] for t,e in reliability['targets'].items()])
    table('Local SHAP sensitivity: four predefined held-out profiles', ['Target', 'Changed seed: mean top-5 overlap', 'Changed background: mean top-5 overlap', 'Largest background change'],
          [[t, f'{e["local_shap"]["summary"][0]["mean_top5_overlap"]*100:.0f}%', f'{e["local_shap"]["summary"][2]["mean_top5_overlap"]*100:.0f}%', f'{e["local_shap"]["summary"][2]["max_change_pp"]:.1f} pp'] for t,e in reliability['targets'].items()])
    table('Exploratory operating-point comparison（training-only F1；原模型保留）',['Target','Policy','Point','Accuracy','Precision','Recall','F1','AUC','FP / FN'],
          [[r['target'],r['policy'],'Exploratory training-selected F1 operating point' if r['point']=='Nested F1' else 'Fixed 0.50',*[f'{r[k]:.6f}' for k in ['accuracy','precision','recall','f1','roc_auc']],f'{r["FP"]} / {r["FN"]}'] for r in research_rows])
    methods = [
        '最後一輪限縮實驗：LCX/RCA 加入 ExtraTrees 與 RBF SVM，各兩組參數；expanded nested policy 未通過預先設定的 AUC/Brier 改善門檻，四個 deployed model hashes 全部保留。',
        'Research threshold：只用 outer train 的 calibrated 3-fold inner OOF，在固定 .15:.01:.75 grid 最大化 F1；每人平均兩次 probability-minus-cutoff。LCX recall/F1 .840/.641、RCA .868/.631，precision .518/.495；FP 30→93 / 34→101、accuracy 降低。AUC/Brier 不变，workspace 保持 0.50。重用 outer splits 的 development evidence 不是獨立確認。',
        'Threshold 值與 retention decision 分開：前者 training-only，後者使用 pooled outer-test labels，只是 development audit。Model evidence 平等展示 Fixed 0.50 與 Exploratory training-selected F1 operating point，不依 retention 結果高亮 winner；不宣稱最佳 threshold 或獨立確認的改善。',
        '資料：原始 XLSX 的 303 人、59 欄；55 個輸入，無 missing／duplicate rows。一筆 Cath Normal／LAD Stenotic 原始矛盾標籤保留，不自行改成 vessel union。',
        '切分：seed 2026；5-fold × 2-repeat stratified outer CV；每個 outer train 內 3-fold inner CV 比較六個候選設定。沒有另宣稱一份未參與開發的 external test。',
        '選模：inner ROC-AUC − 0.25 × Brier；先選每個 family 的參數，再選 family。Headline 評估 nested selection policy；不是 final full-cohort model 的外部成績。',
        'Preprocessing：numeric median imputation + scaling；categorical mode imputation + one-hot。全部在 pipeline 與 training fold 內 fit；無 global feature selection／SMOTE。',
        'Imbalance：Logistic regression 使用 balanced；Random forest 使用 balanced_subsample；XGBoost 使用 regularization。Class weights 只由各 training estimator 計算。',
        'Calibration：predeclared sigmoid，outer train 內 3-fold OOF calibration，ensemble=False；Raw／Isotonic 僅 sensitivity comparison，未用 outer test 選校準方法。',
        'CI：1,000 次 patient-stratified bootstrap，針對 repeat-averaged OOF；conditional on fitted folds，不含重新訓練／選模變異。Fold SD 是 descriptive，因 folds 重疊。',
        'Uncertainty：三 family disagreement + refitted-model min/max。Demo 只取排除此病人的兩個 outer models；新輸入取十個 outer models；不是 clinical confidence interval。',
        'OOD：standardized mixed-feature nearest-neighbor distance，以 cohort leave-one-out distance 的 95th percentile 為界，加上 observed single-feature range。未經外部驗證的 heuristic。',
        'Leakage guard：ml/schema.py 的 LeakageGuard／guard_columns，會拒絕 Cath／LAD／LCX／RCA（含大小寫／常見字元變體），接在 fit／transform 與 API validation；tests/test_validity.py 有真實 guard／fold／prediction checks。',
        'SHAP：對相同 calibrated probability 做 permutation SHAP；background 只來自 training partition；55 個原始 feature coalitions，兩個 local cycles；base + contributions 重建機率至 1e-6。近似且非因果。',
        'Demo honesty：目前八個案例依病人特徵選取，不是 evaluation sample；模型與 SHAP background 排除此病例。改值後仍用排除該 row 的模型；新 profile 使用全 cohort fitted model。',
        'Reliability：四個預先固定案例、四個 target 的 local SHAP seed／computation／training-background sensitivity，量化重疊與幅度，不能概括所有病人。校準六分箱加入人數、descriptive Wilson intervals；Brier bootstrap conditional on fitted predictions。完整 protocol／vectors／fingerprints：experiments/reliability/results.json。',
        'Integrity：checkpoint 比對 data／code／schema／seed／repeats／Python／libraries；API 載入前驗證八個 inference files，含 OOD。輸入來源逐欄追蹤並隨病例匯出；桌面 Chromium integration tests 已接入 CI。',
    ]
    counts = {t: sum(p['target'] == t for p in anatomy['parts']) for t in results if t != 'CAD'}
    anatomy_text = f'BodyParts3D 4.0 / DBCLS，CC BY 4.0；human-atlas derivative commit {anatomy["revision"]}。共 {len(anatomy["parts"])} 個真實 mesh、{anatomy["triangles"]:,} triangles、{anatomy["bytes"]:,} bytes。LAD {counts["LAD"]}、LCX {counts["LCX"]}、RCA {counts["RCA"]} 個 source mesh 各自分組，可獨立選取／上色；不是手畫線或 overlay。DOM 文字標籤只是投影到 mesh centroid。Source names／IDs、license、修改與 hash 位於 manifest 與 ATTRIBUTIONS。'
    risk_text = '風險映射：每組真實 coronary mesh 的 Three.js material 依該 target calibrated probability 由 teal → amber → coral 上色；等待預測時無虛構機率。可 rotate／zoom／pan／select／X-ray／isolate／expand。沒有 patient-specific scan、lesion coordinates 或 RWMA-to-lesion mapping。'
    intro = '# 真實模型結果與最後方法\n\n所有數字直接從 shipped evidence.json／registry.json 讀取，未手填或重跑改分數。CSV／JSON 提供 full precision。\n\n'
    (REVIEW / 'MODEL_RESULTS.md').write_text(intro + '\n'.join(tables) + '\n## ML methodology\n\n' + '\n'.join(f'- {s}' for s in methods) + '\n\n## 3D implementation\n\n' + anatomy_text + '\n\n' + risk_text + '\n', encoding='utf-8')
    photos = ''.join(f'<figure><a href="screenshots/{c["file"]}"><img loading="lazy" src="screenshots/{c["file"]}" alt="{html.escape(c["description"])}"></a><figcaption><strong>{html.escape(c["file"])}</strong><br>{html.escape(c["description"])}</figcaption></figure>' for c in screenshots['captures'][1:])
    page = '''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VesselRisk | Track A review package</title><style>
    *{box-sizing:border-box}body{margin:0;background:#f3f7f9;color:#19384b;font:15px/1.75 system-ui,"Microsoft JhengHei",sans-serif}header{background:#143345;color:#fff;padding:48px max(24px,calc((100vw - 1200px)/2))}header h1{font-size:38px;margin:8px 0}header p{color:#b5cfd9;max-width:920px}.weights{font:13px ui-monospace,monospace;color:#7ed2c4}main{max-width:1250px;margin:auto;padding:32px 24px 80px}h2{font-size:23px;margin:28px 0 12px}h3{font-size:18px}.note{border-left:4px solid #16998e;padding:16px 20px;background:#e6f3f0}.warning{border-color:#ce8b54;background:#fff3e7}a{color:#117f83}img{width:100%;display:block;border-radius:6px}figure{margin:0}figcaption{padding:12px 0;font-size:13px;color:#5d7786}section{margin:30px 0}.table-wrap{overflow-x:auto;background:white;border:1px solid #d9e5eb}table{border-collapse:collapse;width:100%;font:13px/1.5 ui-monospace,monospace}th,td{padding:12px;text-align:left;border-bottom:1px solid #e0e9ee;white-space:nowrap}th{font-family:system-ui,sans-serif;background:#edf4f6}.gallery{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;align-items:start}.links{display:flex;flex-wrap:wrap;gap:12px 24px;margin:20px 0}li{margin:9px 0}.small{font-size:13px;color:#6b8390}@media(max-width:800px){.gallery{grid-template-columns:1fr 1fr}header h1{font-size:29px}}@media(max-width:520px){.gallery{grid-template-columns:1fr}}
    </style><header><div class="weights">PREDICTION 30% / 3D 25% / INTERPRETABILITY 20% / INTEGRATION 15% / TECHNICAL 10%</div><h1>VesselRisk：Track A 審查入口</h1><p>先看實際產品，再看完整數字與方法。此頁可離線開啟；它不是自評獎項或宣稱第一名。</p></header><main>
    <div class="links"><a href="../README.md">完整 README / run</a><a href="COMPLETION_SUMMARY.md">Completion summary</a><a href="../docs/FINAL_AUDIT_RESULTS.md">Final audit / model investigation</a><a href="../docs/DEVPOST_COPY.md">Devpost draft</a><a href="MODEL_RESULTS.csv">完整數字 CSV</a><a href="MODEL_RESULTS.json">完整數字 JSON</a><a href="../report/VesselRisk-Track-A.pdf">六頁 report</a><a href="../demo/DEMO_NARRATION_EN.md">English demo narration</a></div>
    <p class="note">四模型 + 55 輸入 + 真實 3D + SHAP + Model evidence 已同步可靠性實驗、輸入來源與完整性驗證。測試、解壓驗證與版本範圍見 BUILD_VALIDATION.json。ZIP 包含可建置原始碼、models、assets、lockfiles 與 build/run 設定；執行 --setup 安裝依賴並在本機建置前端。</p>
    <h2>01 / 先看主畫面</h2><a href="screenshots/01-dashboard.png"><img src="screenshots/01-dashboard.png" alt="Actual VesselRisk dashboard"></a>
    <p class="small">實際 held-out mixed-vessel case：CAD 94.9%、LAD 90.4%、LCX 17.7%、RCA 18.6%。這是示範病例，不是平均驗證表現。點圖片看原尺寸。</p>
    <h2>02 / 產品各狀態</h2><div class="gallery">''' + photos + '''</div>
    <p class="note warning">0.50 基準的 LCX／RCA recall 是 0.420／0.395；training-only F1 research cutoffs 提高至 0.840／0.868，代價是更多 false positives、較低 precision／accuracy。兩種 operating point 均完整列出。303 人單中心 cohort，沒有外部 clinical validation；CI 不含重訓／選模 uncertainty。3D 是 generic anatomy，不是病人 scan 或 lesion localization。</p>
    <h2>03 / 真實數字</h2><p>下列 headline scores 評估 repeated nested selection policy；deployed family 在全 cohort 另做 inner selection。不可將表中的 AUC 當作 final model 的 external-test 成績。PR-AUC 使用 average precision。</p>''' + ''.join(sections) + '''
    <h2>04 / 最後的 ML methodology</h2><ol>''' + ''.join(f'<li>{html.escape(m)}</li>' for m in methods) + '</ol><h2>05 / 3D 的實際做法</h2><p>' + html.escape(anatomy_text) + '</p><p>' + html.escape(risk_text) + '''</p>
    <h2>06 / 完成狀態與尚未驗證</h2><p>核心本機產品、訓練／evaluation artifacts、解釋、3D、Model evidence、report／demo script 與驗證已完成。<strong>Docker 執行未驗證</strong>（主機無 Docker）；尚未 remote deployment、final demo recording／YouTube upload、competition submission。Author／team／public links 與最後說法需提交者 review。</p>
    <p>Run：專案根目錄 <code>python scripts/start.py --setup</code>；之後 <code>python scripts/start.py</code>。開 <a href="http://127.0.0.1:3000">http://127.0.0.1:3000</a>。Python 3.13 + Node.js 24 建議；不需 API key 或重訓。</p><p class="small">研究／教育用途，不是 diagnosis、treatment advice 或外部驗證 clinical screening。OpenAI Codex 協助研究、實作、驗證與文案；模型結果從 supplied workbook 實際計算。</p></main></html>'''
    (REVIEW / 'index.html').write_text(page, encoding='utf-8')


def package():
    OUTPUT.mkdir(exist_ok=True)
    files = collect_files(ROOT)
    validate_required(p.relative_to(ROOT).as_posix() for p in files)
    manifest = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    write_json(REVIEW / 'FILE_MANIFEST.json', {'root': 'VesselRisk', 'files': manifest, 'note': 'Portable source package. Run python scripts/start.py --setup to install dependencies and build locally. Every packaged file except this self-referential manifest is hashed.', 'excluded': sorted(EXCLUDED_DIRS | EXCLUDED_FILES) + ['local references', 'historical UI snapshots', 'test screenshots', 'env files', 'logs', 'bytecode', 'training checkpoints']})
    files.append(REVIEW / 'FILE_MANIFEST.json')
    archive = OUTPUT / 'VesselRisk-Track-A-review.zip'
    with ZipFile(archive, 'w', compression=ZIP_DEFLATED, compresslevel=6) as zipped:
        for path in files:
            zipped.write(path, 'VesselRisk/' + path.relative_to(ROOT).as_posix())
    with ZipFile(archive) as zipped:
        assert zipped.testzip() is None
        names = set(zipped.namelist())
        validate_required(n.removeprefix('VesselRisk/') for n in names)
        reliability_required = ['ml/artifacts/integrity.json', 'ml/integrity.py', 'ml/reliability.py', 'ml/reproducibility.py', 'experiments/reliability/results.json', 'docs/RELIABILITY_AUDIT.md', 'tests/test_reliability.py', 'web/components/ReliabilityDetails.tsx', 'web/lib/input-provenance.ts', 'web/e2e/reliability.spec.ts', 'review/BUILD_VALIDATION.json']
        assert all('VesselRisk/' + p in names for p in reliability_required), 'Missing reliability deliverable'
        assert sum(n.startswith('VesselRisk/review/screenshots/') and n.endswith('.png') for n in names) == 11
        ui_required = ['web/components/HeartViewer.module.css', 'web/components/ModelEvidenceOverview.tsx', 'web/components/ModelEvidence.module.css', 'web/components/WorkspaceAnalytics.tsx', 'web/lib/target-colors.ts', 'review/screenshots/11-model-evidence-overview.png']
        assert all('VesselRisk/' + p in names for p in ui_required), 'Missing current UI deliverable'
        for item in manifest:
            data = zipped.read('VesselRisk/' + item['path'])
            assert hashlib.sha256(data).hexdigest() == item['sha256']
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (OUTPUT / (archive.name + '.sha256')).write_text(f'{digest}  {archive.name}\n', encoding='ascii')
    print(f'Created {archive.name}: {archive.stat().st_size / 1024**2:.2f} MiB, {len(files)} files; CRC, SHA-256 manifest and core deliverables verified.')


if __name__ == '__main__':
    make_evidence()
    package()
