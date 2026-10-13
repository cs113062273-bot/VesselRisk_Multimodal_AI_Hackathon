"""Build the six-page Track A report from the shipped evaluation evidence."""
import hashlib
import json
import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT = ROOT / 'report/VesselRisk-Track-A.pdf'
W, H = 595.28, 841.89
M = 43
WIDTH = W - 2 * M
INK = HexColor('#17384b')
TEAL = HexColor('#168e8b')
MUTED = HexColor('#536d7b')
LINE = HexColor('#dce7ec')
ICE = HexColor('#f3f8fa')
COLORS = [TEAL, HexColor('#4f8bba'), HexColor('#ae7b16'), HexColor('#cf7874')]


class Report:
    def __init__(self):
        OUT.parent.mkdir(exist_ok=True)
        self.c = canvas.Canvas(str(OUT), pagesize=(W, H))
        self.c.setTitle('VesselRisk - Track A technical report')
        self.c.setAuthor('VesselRisk')
        self.page = 0
        self.y = 0

    def begin(self, title, subtitle):
        self.page += 1
        c = self.c
        c.setFillColor(INK)
        c.rect(0, H - 9, W, 9, fill=1, stroke=0)
        c.setFont('Helvetica-Bold', 11)
        c.drawString(M, H - 37, 'VesselRisk')
        c.setFillColor(MUTED)
        c.setFont('Helvetica', 9)
        c.drawRightString(W - M, H - 37, 'MULTIMODAL AI HACKATHON 2026 / TRACK A')
        c.setFillColor(INK)
        c.setFont('Helvetica-Bold', 23)
        c.drawString(M, H - 91, title)
        self.y = H - 109
        self.par(subtitle, size=10, color=MUTED, space=18)

    def par(self, text, size=10.5, color=INK, space=10, width=None, x=M):
        style = ParagraphStyle('body', fontName='Helvetica', fontSize=size,
                               leading=size * 1.36, textColor=color)
        p = Paragraph(text, style)
        _, height = p.wrap(width or WIDTH, 1000)
        if self.y - height < 67:
            raise RuntimeError(f'Page {self.page} overflow: {text[:80]}')
        p.drawOn(self.c, x, self.y - height)
        self.y -= height + space

    def heading(self, text):
        self.c.setFillColor(INK)
        self.c.setFont('Helvetica-Bold', 12)
        self.c.drawString(M, self.y - 12, text)
        self.y -= 26

    def table(self, rows, widths, size=9.5, padding=5):
        assert abs(sum(widths) - WIDTH) < .02
        style = ParagraphStyle('table', fontName='Helvetica', fontSize=size,
                               leading=size * 1.28, textColor=INK)
        data = [[Paragraph(str(cell), style) for cell in row] for row in rows]
        table = Table(data, colWidths=widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ICE),
            ('LINEBELOW', (0, 0), (-1, -1), .45, LINE),
            ('TOPPADDING', (0, 0), (-1, -1), padding),
            ('BOTTOMPADDING', (0, 0), (-1, -1), padding),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        _, height = table.wrap(WIDTH, 1000)
        if self.y - height < 67:
            raise RuntimeError(f'Page {self.page} table overflow')
        table.drawOn(self.c, M, self.y - height)
        self.y -= height + 14

    def image(self, path, width=WIDTH):
        image = ImageReader(str(path))
        iw, ih = image.getSize()
        height = width * ih / iw
        self.c.drawImage(image, M, self.y - height, width, height, mask='auto')
        self.y -= height + 12

    def flow(self, labels):
        gap = 10
        width = (WIDTH - gap * (len(labels) - 1)) / len(labels)
        bottom = self.y - 48
        for i, lines in enumerate(labels):
            x = M + i * (width + gap)
            self.c.setFillColor(ICE)
            self.c.setStrokeColor(LINE)
            self.c.roundRect(x, bottom, width, 44, 4, fill=1, stroke=1)
            self.c.setFillColor(INK)
            for j, line in enumerate(lines):
                self.c.setFont('Helvetica-Bold' if j == 0 else 'Helvetica', 9)
                self.c.drawCentredString(x + width / 2, bottom + 28 - j * 13, line)
            if i < len(labels) - 1:
                self.c.setStrokeColor(MUTED)
                self.c.line(x + width + 2, bottom + 22, x + width + gap - 2, bottom + 22)
                self.c.line(x + width + gap - 5, bottom + 24, x + width + gap - 2, bottom + 22)
                self.c.line(x + width + gap - 5, bottom + 20, x + width + gap - 2, bottom + 22)
        self.y = bottom - 14

    def code(self, lines):
        height = len(lines) * 16 + 16
        self.c.setFillColor(ICE)
        self.c.roundRect(M, self.y - height, WIDTH, height, 4, fill=1, stroke=0)
        self.c.setFillColor(INK)
        self.c.setFont('Courier', 10)
        for i, line in enumerate(lines):
            self.c.drawString(M + 10, self.y - 18 - i * 16, line)
        self.y -= height + 13

    def end(self):
        self.c.setStrokeColor(LINE)
        self.c.line(M, 53, W - M, 53)
        self.c.setFillColor(MUTED)
        self.c.setFont('Helvetica', 8)
        self.c.drawString(M, 38, 'Research and education only - not a substitute for diagnostic imaging.')
        self.c.drawRightString(W - M, 38, f'{self.page} / 6')
        print(f'Page {self.page}: content ends at {self.y:.1f} pt')
        self.c.showPage()


def plot(r, x, bottom, width, height, key, targets, title, xlabel, ylabel):
    c = r.c
    left, y0 = x + 30, bottom + 32
    cw, ch = width - 43, height - 43
    c.setFillColor(INK)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(x, bottom + height + 12, title)
    c.setFont('Helvetica', 8.5)
    for t in [0, .5, 1]:
        c.setStrokeColor(LINE)
        c.setLineWidth(.45)
        c.line(left, y0 + t * ch, left + cw, y0 + t * ch)
        c.line(left + t * cw, y0, left + t * cw, y0 + ch)
        c.setFillColor(MUTED)
        c.drawRightString(left - 5, y0 + t * ch - 3, f'{t:g}')
        c.drawCentredString(left + t * cw, y0 - 13, f'{t:g}')
    c.setDash(3, 3)
    c.setStrokeColor(HexColor('#b9cad3'))
    c.line(left, y0, left + cw, y0 + ch)
    c.setDash()
    for (_, evidence), color in zip(targets.items(), COLORS):
        c.setStrokeColor(color)
        c.setLineWidth(1.5)
        p = c.beginPath()
        for i, point in enumerate(evidence['curves'][key]):
            px, py = left + point['x'] * cw, y0 + point['y'] * ch
            p.moveTo(px, py) if i == 0 else p.lineTo(px, py)
        c.drawPath(p)
    c.setFillColor(MUTED)
    c.setFont('Helvetica', 8.5)
    c.drawCentredString(left + cw / 2, y0 - 27, xlabel)
    c.drawString(left, y0 + ch + 4, ylabel)


def build():
    from ml.reliability import load_verified
    reliability = load_verified()
    if reliability is None:
        raise RuntimeError('Run python -m ml.reliability before building the report')
    evidence = json.loads((ROOT / 'ml/artifacts/evidence.json').read_text(encoding='utf-8'))
    registry = json.loads((ROOT / 'ml/artifacts/registry.json').read_text(encoding='utf-8'))
    refinement = json.loads((ROOT / 'experiments/vessel_refinement/results.json').read_text(encoding='utf-8'))
    assert refinement['baseline_evidence_sha256'] == hashlib.sha256((ROOT / 'ml/artifacts/evidence.json').read_bytes()).hexdigest()
    assert refinement['baseline_registry_sha256'] == hashlib.sha256((ROOT / 'ml/artifacts/registry.json').read_bytes()).hexdigest()
    targets = evidence['targets']
    r = Report()

    r.begin('VesselRisk', 'Clinical inputs, coronary probabilities, and interactive 3D anatomy.')
    r.par('VesselRisk predicts <b>overall coronary artery disease (CAD)</b> and stenosis in the <b>LAD, LCX, and RCA</b> from 55 clinical inputs. The workspace connects each probability to its artery and the measurements that contributed to it. A separate Model evidence view shows training, validation, calibration, and failures.')
    r.image(ROOT / 'demo/screenshots/patient-workspace.png', width=WIDTH)
    r.par('Running application, using the 54-year-old example: <b>CAD 94.9%, LAD 90.4%, LCX 17.7%, RCA 18.6%</b>. Each displayed model was trained without this patient. An example prediction is not an average evaluation result.', size=9.5, space=13)
    r.heading('What the prototype includes')
    r.table([
        ['Part', 'Implementation'],
        ['Prediction', 'Four trained classifiers, calibrated probabilities, and held-out evaluation.'],
        ['3D and explanations', 'Separate artery selection and coloring, measured inputs, and signed SHAP contributions.'],
        ['Integration', 'Validated FastAPI requests, synchronized results, input checks, and JSON exports.'],
    ], [120, WIDTH - 120])
    r.end()

    r.begin('Data and model training', 'The original labels are retained; none of the four outcomes is used as an input.')
    r.par('The supplied UCI workbook has <b>303 patients and 59 columns</b>: 55 inputs and four outcomes. Inputs cover demographics/history, examination, ECG, blood tests, and echocardiography. The empty worksheet is ignored. There are no missing or duplicate rows; constant Exertional CP is retained.')
    r.table([['Target', 'Positive', 'Negative']] + [[t, e['positive'], e['negative']] for t, e in targets.items()], [WIDTH - 220, 110, 110])
    r.par('A guard rejects <b>Cath, LAD, LCX, and RCA</b> during training and inference. Source row 94 has Cath Normal and LAD Stenotic; this discrepancy is recorded without changing either label.', size=10, space=12)
    r.heading('Training and evaluation procedure')
    r.flow([['Outer folds', '5 x 2 repeats'], ['Inner selection', '3 folds'], ['Calibration', 'Training only'], ['Outer test', 'Held-out results']])
    r.par('Stratified outer cross-validation uses five folds, repeated twice, with seed 2026. Each outer training partition compares six fixed configurations using <b>inner ROC-AUC - 0.25 x Brier</b>. Numeric imputation/scaling and categorical imputation/one-hot encoding are fitted inside the training partitions.', size=10)
    r.table([
        ['Family', 'Compared settings'],
        ['Logistic regression', 'C = 0.1 or 1; balanced class weights.'],
        ['Random forest', '120 trees; minimum leaf size 3 or 8; balanced subsample weights.'],
        ['XGBoost', '110 trees; depth 2 or 3; learning rate 0.04; regularization.'],
    ], [135, WIDTH - 135])
    r.par('Sigmoid calibration uses three folds inside outer training data. Raw and isotonic results are comparisons, not methods selected using test results. Each patient has two held-out probabilities, averaged for the main metrics. Deployment repeats inner selection on all 303 patients; this single fitted model is distinct from the evaluated procedure.', size=10, space=4)
    deployed = '; '.join(f'{t}: {m["family"]} ({", ".join(f"{k}={v}" for k, v in m["params"].items())})' for t, m in registry['models'].items())
    r.par('<b>Selected models for new profiles:</b> ' + deployed + '.', size=9.5, space=4)
    r.end()

    r.begin('Evaluation results', 'Internal held-out results at a 0.50 classification cutoff; no external clinical validation.')
    rows = [['Target', 'Accuracy', 'Precision', 'Recall', 'F1', 'ROC-AUC', 'AP', 'Brier']]
    for t, e in targets.items():
        rows.append([t] + [f'{e["metrics"][k]:.3f}' for k in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc', 'pr_auc', 'brier']])
    r.table(rows, [48, 70, 70, 63, 56, 75, 65, WIDTH - 447])
    intervals = '; '.join(f'{t} [{e["auc_ci"][0]:.3f}, {e["auc_ci"][1]:.3f}]' for t, e in targets.items())
    r.par('<b>ROC-AUC 95% intervals:</b> ' + intervals + '. Bootstrap: 1,000 patient-stratified resamples of the fixed predictions; retraining/selection uncertainty is excluded.', size=9.5, space=18)
    plot(r, M, r.y - 158, 244, 140, 'roc', targets, 'ROC curves', 'False positive rate', 'True positive rate')
    plot(r, M + 265, r.y - 158, 244, 140, 'calibration', targets, 'Calibration curves', 'Predicted probability', 'Observed positive rate')
    r.y -= 176
    for i, (target, color) in enumerate(zip(targets, COLORS)):
        r.c.setFillColor(color)
        r.c.circle(M + 5 + i * 112, r.y, 3, fill=1, stroke=0)
        r.c.setFont('Helvetica', 9.5)
        r.c.drawString(M + 14 + i * 112, r.y - 3, target)
    r.y -= 19
    r.par('AP is average precision. Brier measures probability error; lower is better. The app also shows precision-recall curves, calibration-bin counts, intervals, and separate-repeat results.', size=9.5, space=13)
    r.heading('Threshold tradeoffs for the vessel models')
    rows = [['Target', 'Missed cases<br/>0.50 / F1', 'False positives<br/>0.50 / F1', 'Recall<br/>0.50 / F1']]
    for t in ['LCX', 'RCA']:
        variants = refinement['targets'][t]['variants']
        a, b = [next(v['metrics'] for v in variants if v['policy'] == 'Frozen baseline' and v['operating_point'] == k) for k in ['0.50', 'Nested F1']]
        rows.append([t, f'{a["confusion_matrix"][1][0]} / {b["confusion_matrix"][1][0]}', f'{a["confusion_matrix"][0][1]} / {b["confusion_matrix"][0][1]}', f'{a["recall"]:.3f} / {b["recall"]:.3f}'])
    r.table(rows, [55, 151, 156, WIDTH - 362])
    r.par('F1 cutoffs are selected from inner training predictions. Higher recall comes with more false positives and lower accuracy. Models and probabilities are unchanged; the workspace keeps 0.50. These reused-split comparisons do not establish clinical cutoffs.', size=9.5, space=4)
    r.end()

    r.begin('Explanations and model checks', 'The explanation uses the same calibrated classifier as the displayed prediction.')
    r.flow([['Background', 'Starting probability'], ['Input contributions', '55 signed effects'], ['Patient estimate', 'Base + contributions']])
    r.par('Permutation SHAP assigns contributions to the original input variables. Background patients come from the model\'s training partition. Starting probability plus all contributions reconstructs the displayed probability within 1e-6. Red increases it; teal decreases it. Values use percentage points, not causal treatment effects.')
    r.par('Local explanations use two permutation cycles and 16 or 20 background patients. Additivity checks the sum; it does not prove that individual contributions are precise. Correlated measurements can share attribution.', size=10, space=12)
    r.heading('Sensitivity on four held-out profiles')
    rows = [['Target', 'Changed seed:<br/>top-five overlap', 'Changed background:<br/>top-five overlap', 'Largest background<br/>change (pp)']]
    for t in targets:
        s = reliability['targets'][t]['local_shap']['summary']
        rows.append([t, f'{s[0]["mean_top5_overlap"] * 100:.0f}%', f'{s[2]["mean_top5_overlap"] * 100:.0f}%', f'{s[2]["max_change_pp"]:.1f}'])
    r.table(rows, [47, 143, 174, WIDTH - 364])
    r.par('The audit also changes the computation budget. Global SHAP uses 60 held-out explanations across ten folds, with 16 background patients per fold. Rank correlations range from 0.730 to 0.775. These are descriptive checks, not population-wide reliability claims.', size=9.5, space=12)
    r.heading('How to read the other checks')
    r.table([
        ['Display', 'Meaning'],
        ['Model disagreement', 'Three model families give different estimates for the same inputs.'],
        ['Fitted-model range', 'New profiles use ten outer models; examples use the two that excluded the patient. This is not a confidence interval.'],
        ['Unusual profile', 'Observed-range and mixed-feature distance checks flag unfamiliar inputs. The warning is a heuristic, not a validated clinical test.'],
    ], [125, WIDTH - 125])
    r.par('Model evidence includes age/sex groups, ECG and laboratory/echo ablations, and actual false positives and missed cases. Small subgroups and approximate explanations limit the conclusions.', size=10, space=4)
    r.end()

    r.begin('3D mapping and integration', 'Each artery keeps the same identity in the model output, mesh, label, and explanation.')
    top = r.y
    r.image(ROOT / 'demo/screenshots/coronary-anatomy.png', width=215)
    bottom = r.y
    r.y = top
    right_x = M + 236
    right_width = WIDTH - 236
    r.par('<b>BodyParts3D reference anatomy</b><br/>63 meshes, 37,444 triangles, and about 1 MB of geometry. The heart and coronary arteries are loaded locally.', width=right_width, x=right_x)
    r.par('LAD, LCX, and RCA meshes receive the corresponding probability color. Labels remain anchored to vessel surfaces as the view rotates.', width=right_width, x=right_x)
    r.par('Controls include rotation, zoom, pan, orbit/pause, X-ray, vessel isolation, reset, expansion, and artery guides. Orbit starts on first opening and after a successful prediction.', width=right_width, x=right_x, size=10)
    r.y = min(r.y, bottom) - 2
    r.table([
        ['Artery', 'Source structures'],
        ['LAD', 'Anterior interventricular artery and branches; trunk FJ2631.'],
        ['LCX', 'Left circumflex branches; FJ2649-FJ2654.'],
        ['RCA', 'Right coronary artery and branches; trunk FJ2723.'],
    ], [60, WIDTH - 60])
    r.par('The pinned human-atlas derivative preserves source mesh names and IDs. Geometry is recentered and uniformly scaled. It is generic adult male anatomy: colors show probability, not patient-specific lesions, stenosis severity, or RWMA coordinates.', size=10, space=12)
    r.heading('From inputs to the screen')
    r.flow([['Next.js form', '55 clinical inputs'], ['FastAPI', 'Models + SHAP'], ['UI update', 'Risk + 3D + explanation']])
    r.par('Invalid inputs are rejected. Edits mark old explanations and disable export until prediction succeeds. Input sources and exact values are included in JSON exports. Schema, model code, API, and mesh mapping are separate modules, so features and models can be extended without replacing the whole application.', size=10, space=4)
    r.end()

    r.begin('Usage and limitations', 'Included models and local anatomy require no cloud credentials or retraining.')
    r.heading('Local startup')
    r.par('Use Python 3.13 and Node.js 24. Open a terminal in the extracted repository folder. The first command installs dependencies, builds the frontend, and starts both services.', size=10)
    r.code(['python scripts/start.py --setup', '# Later launches', 'python scripts/start.py'])
    r.par('Wait for startup, then open <b>http://localhost:3000</b>. Select an example, predict, inspect arteries and explanations, then open Model evidence. Ctrl+C stops both services.', size=10, space=12)
    r.par('Run the commands below with the Python environment created by setup: .venv/Scripts/python on Windows, or .venv/bin/python on macOS/Linux, in place of python.', size=9.5, space=8)
    r.table([
        ['Task', 'Command or location'],
        ['Verify frozen results', 'python -m ml.evaluate'],
        ['Scientific/API tests', 'python -m pytest'],
        ['Train models', 'python -m ml.train (optional; use the pinned environment)'],
        ['Models and evidence', 'ml/artifacts/; full usage and browser checks in README.md'],
    ], [142, WIDTH - 142])
    r.heading('Limits')
    r.par('The data is a single 303-patient referral cohort, with no external validation or future-event outcomes. LCX/RCA recall is limited at 0.50. Independent target models can disagree. Approximate SHAP, fitted-model ranges, and unfamiliar-input warnings do not establish clinical reliability. The UI states that this is research/education software, not diagnosis, treatment advice, or a substitute for diagnostic imaging.', size=10, space=12)
    r.heading('Sources and AI assistance')
    r.par('<b>Data:</b> UCI Extension of Z-Alizadeh Sani, DOI <link href="https://doi.org/10.24432/C5461K" color="#168e8b">10.24432/C5461K</link>, CC BY 4.0.<br/><b>Anatomy:</b> BodyParts3D / DBCLS, CC BY 4.0; DOI <link href="https://doi.org/10.1093/nar/gkn613" color="#168e8b">10.1093/nar/gkn613</link>. The exact derivative revision and mesh IDs are in the anatomy manifest.<br/><b>Methods:</b> scikit-learn nested validation/calibration and SHAP permutation explanations. Links are in docs/RESEARCH.md; licenses and modifications are in ATTRIBUTIONS.md.', size=9.5)
    r.par('OpenAI Codex assisted research, implementation, debugging, tests, UI, and report drafting. Microsoft Edge TTS generated the demo narration. Statistical models produce the predictions; generative AI does not predict disease or give medical advice.', size=9.5, space=4)
    r.end()
    assert r.page == 6
    r.c.save()
    print(f'Created {OUT} (6 pages)')


if __name__ == '__main__':
    build()
