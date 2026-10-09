"""Generate the official max-six-page report from measured evidence and screenshots."""
import json
import hashlib
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'report/VesselRisk-Track-A.pdf'
W,H=595.28,841.89
M=43
INK=HexColor('#17384b'); TEAL=HexColor('#168e8b'); MUTED=HexColor('#6a8392'); LINE=HexColor('#dce7ec'); ICE=HexColor('#f3f8fa')
COLORS=[TEAL,HexColor('#4f8bba'),HexColor('#c59841'),HexColor('#cf7874')]


class Report:
    def __init__(self):
        OUT.parent.mkdir(parents=True,exist_ok=True)
        self.c=canvas.Canvas(str(OUT),pagesize=(W,H))
        self.c.setTitle('VesselRisk | Track A technical report')
        self.c.setAuthor('VesselRisk contributors; AI-assisted with OpenAI Codex')
        self.page=0;self.y=0

    def begin(self,kicker,title,subtitle):
        self.page+=1;c=self.c
        c.setFillColor(INK);c.rect(0,H-9,W,9,fill=1,stroke=0)
        c.setFont('Helvetica-Bold',11);c.drawString(M,H-37,'VesselRisk')
        c.setFont('Helvetica',8);c.setFillColor(MUTED);c.drawRightString(W-M,H-37,'MULTIMODAL AI HACKATHON 2026 / TRACK A')
        c.setFillColor(TEAL);c.setFont('Helvetica-Bold',8);c.drawString(M,H-79,kicker.upper())
        c.setFillColor(INK);c.setFont('Helvetica-Bold',24);c.drawString(M,H-111,title)
        self.y=H-130
        self.par(subtitle,size=9,color=MUTED,space=23)

    def par(self,text,size=9,color=INK,space=12,width=None,x=M):
        style=ParagraphStyle('body',fontName='Helvetica',fontSize=size,leading=size*1.5,textColor=color)
        p=Paragraph(text,style);w,h=p.wrap(width or W-2*M,1000)
        if self.y-h<65:raise RuntimeError(f'Page {self.page} overflow: {text[:70]}')
        p.drawOn(self.c,x,self.y-h);self.y-=h+space

    def heading(self,text):
        self.c.setFillColor(INK);self.c.setFont('Helvetica-Bold',12);self.c.drawString(M,self.y-12,text);self.y-=27

    def table(self,rows,widths=None,size=8,padding=6):
        style=ParagraphStyle('table',fontName='Helvetica',fontSize=size,leading=size*1.35,textColor=INK)
        data=[[Paragraph(str(cell),style) for cell in row] for row in rows]
        t=Table(data,colWidths=widths or [((W-2*M)/len(rows[0]))]*len(rows[0]))
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),ICE),('TEXTCOLOR',(0,0),(-1,0),MUTED),('LINEBELOW',(0,0),(-1,0),.6,LINE),('LINEBELOW',(0,1),(-1,-1),.4,LINE),('TOPPADDING',(0,0),(-1,-1),padding),('BOTTOMPADDING',(0,0),(-1,-1),padding),('LEFTPADDING',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'TOP')]))
        tw,th=t.wrap(W-2*M,1000)
        if self.y-th<65:raise RuntimeError(f'Table overflow on page {self.page}')
        t.drawOn(self.c,M,self.y-th);self.y-=th+18

    def image(self,path,width=None,height=None):
        image=ImageReader(str(path));iw,ih=image.getSize()
        width=width or W-2*M
        height=height or width*ih/iw
        self.c.drawImage(image,M,self.y-height,width=width,height=height,mask='auto',preserveAspectRatio=True,anchor='c')
        self.y-=height+13

    def flow(self,labels,caption=None):
        """Compact vector diagram; every label remains searchable PDF text."""
        gap=10; width=(W-2*M-gap*(len(labels)-1))/len(labels); bottom=self.y-49
        c=self.c
        for i,lines in enumerate(labels):
            x=M+i*(width+gap); final=i==len(labels)-1
            c.setFillColor(TEAL if final else ICE);c.setStrokeColor(LINE)
            c.roundRect(x,bottom,width,45,4,fill=1,stroke=1)
            c.setFillColor(HexColor('#ffffff') if final else INK)
            for j,line in enumerate(lines):
                c.setFont('Helvetica-Bold' if j==0 else 'Helvetica',8)
                c.drawCentredString(x+width/2,bottom+28-j*12,line)
            if not final:
                c.setStrokeColor(MUTED);c.line(x+width+2,bottom+23,x+width+gap-3,bottom+23)
                c.line(x+width+gap-5,bottom+25,x+width+gap-3,bottom+23)
                c.line(x+width+gap-5,bottom+21,x+width+gap-3,bottom+23)
        self.y=bottom-12
        if caption:self.par(caption,size=7.5,color=MUTED,space=17)

    def end(self):
        c=self.c;c.setStrokeColor(LINE);c.line(M,53,W-M,53)
        c.setFillColor(MUTED);c.setFont('Helvetica',7)
        c.drawString(M,39,'Research / education only. No clinical diagnosis, treatment advice or lesion localization.')
        c.drawRightString(W-M,39,f'{self.page} / 6')
        c.showPage()


def chart(c,x,y,w,h,series,title,xlabel,ylabel,diagonal=True):
    c.setFillColor(INK);c.setFont('Helvetica-Bold',10);c.drawString(x,y+h+21,title)
    left,bottom=x+25,y+23;cw,ch=w-35,h-28
    c.setStrokeColor(LINE);c.setLineWidth(.45)
    for t in [0,.25,.5,.75,1]:
        c.line(left,bottom+t*ch,left+cw,bottom+t*ch)
        c.line(left+t*cw,bottom,left+t*cw,bottom+ch)
        c.setFont('Helvetica',6);c.setFillColor(MUTED)
        c.drawRightString(left-4,bottom+t*ch-2,f'{t:g}')
        c.drawCentredString(left+t*cw,bottom-10,f'{t:g}')
    if diagonal:
        c.setDash(3,3);c.setStrokeColor(HexColor('#b9cad3'));c.line(left,bottom,left+cw,bottom+ch);c.setDash()
    for name,points,color in series:
        c.setStrokeColor(color);c.setLineWidth(1.4);p=c.beginPath()
        for i,v in enumerate(points):
            px,py=left+v['x']*cw,bottom+v['y']*ch
            if i==0:p.moveTo(px,py)
            else:p.lineTo(px,py)
        c.drawPath(p)
    c.setFont('Helvetica',7);c.setFillColor(MUTED);c.drawCentredString(left+cw/2,bottom-22,xlabel)
    c.drawString(left,bottom+ch+5,ylabel)


def threshold_chart(r, refinement):
    """Paired error counts from the same frozen models, on identical zero-based axes."""
    rows=[]
    for target in ['LCX','RCA']:
        variants=refinement['targets'][target]['variants']
        for operating,label,color in [('0.50','0.50',HexColor('#627d90')),('Nested F1','F1',HexColor('#6d60a2'))]:
            metrics=next(v['metrics'] for v in variants if v['policy']=='Frozen baseline' and v['operating_point']==operating)
            cm=metrics['confusion_matrix']
            rows.append((f'{target} / {label}',cm[1][0],cm[0][1],color))
    scale=max(20,((max(max(row[1:3]) for row in rows)+19)//20)*20)
    height=114
    if r.y-height<65:raise RuntimeError('Threshold chart overflow')
    c=r.c
    for panel,title in enumerate(['Missed positives (patients)','False positives (patients)']):
        x=M+panel*267; left=x+66; width=149
        c.setFillColor(INK);c.setFont('Helvetica-Bold',9);c.drawString(x,r.y-9,title)
        for i,(label,fn,fp,color) in enumerate(rows):
            y=r.y-29-i*18; count=fn if panel==0 else fp
            c.setFillColor(INK);c.setFont('Helvetica',7);c.drawString(x,y,label)
            c.setFillColor(ICE);c.rect(left,y-1,width,8,fill=1,stroke=0)
            c.setFillColor(color);c.rect(left,y-1,width*count/scale,8,fill=1,stroke=0)
            c.setFillColor(INK);c.drawRightString(x+241,y,str(count))
        c.setFillColor(MUTED);c.setFont('Helvetica',6.5)
        for tick in [0,scale/2,scale]:c.drawCentredString(left+width*tick/scale,r.y-101,f'{tick:g}')
    r.y-=height


def build():
    evidence=json.loads((ROOT/'ml/artifacts/evidence.json').read_text(encoding='utf-8'))
    registry=json.loads((ROOT/'ml/artifacts/registry.json').read_text(encoding='utf-8'))
    targets=evidence['targets'];r=Report()
    r.begin('01 / Product & objective','Coronary risk, made visible.','Four calibrated clinical predictions, independently mapped to real coronary anatomy and explained by patient-level evidence.')
    r.par('VesselRisk connects <b>structured patient inputs → four trained classifiers → calibrated probabilities → interpretable 3D coronary anatomy</b>. The first screen pairs the patient profile, heart and target-specific explanation. A separate Evidence Lab exposes validation, calibration, failures, provenance and model hashes.',space=15)
    screenshot=ROOT/'demo/screenshots/patient-workspace.png'
    if not screenshot.exists():raise RuntimeError('Run the browser demo checks to generate final screenshots first')
    r.image(screenshot,height=270)
    r.par('Actual application screenshot: a held-out cohort case, not a mockup. Outputs are CAD 94.9%, LAD 90.4%, LCX 17.7% and RCA 18.6%. Selected demonstration cases are illustrative, not the evaluation sample.',size=7.5,color=MUTED,space=17)
    r.heading('Track A fit')
    r.table([['Official criterion','Delivered evidence'],['Prediction · 30%','Four targets; nested repeated CV; model/calibration comparisons; honest per-target metrics'],['3D · 25%','63 licensed meshes; separate coronary territories; rotate, zoom, select, X-ray and vessel isolation'],['Interpretability · 20%','Exact-probability SHAP reconstruction, measured inputs, global ranks, model disagreement'],['Integration · 15% / technical · 10%','Validated API; synchronized outputs; local assets; pinned artifacts, hashes, tests and startup']],widths=[140,W-2*M-140],size=7.5)
    r.end()

    r.begin('02 / Data & scientific protocol','Validation without shortcuts.','Target columns are rejected during fitting, preprocessing and inference.')
    r.flow([['303 patients','55 inputs'],['LeakageGuard','No target inputs'],['Nested CV','5 folds x 2'],['Inner selection','3-fold search'],['Calibration','Training only'],['Held-out OOF','Two per patient']],
           'Selection, preprocessing and calibration use outer training data only; test labels stay isolated.')
    r.table([['Source workbook','Actual inspection'],['Populated worksheet','303 patients x 59 columns; 55 inputs. Empty Sheet1 excluded.'],['Quality audit','0 missing / duplicate rows; constant Exertional CP retained.'],['Positive / negative','CAD 216 / 87; LAD 177 / 126; LCX 119 / 184; RCA 114 / 189'],['Label discrepancy','Patient row 94: Cath Normal, LAD Stenotic. Source labels preserved.']],widths=[137,W-2*M-137])
    r.heading('Repeated nested stratified cross-validation')
    r.par('<b>Outer:</b> stratified 5-fold x 2 repeats, seed 2026; average two held-out probabilities per patient. <b>Inner:</b> three folds, six fixed candidates; maximize ROC-AUC - 0.25 x Brier. Select parameters, then family.')
    r.table([['Family','Search / fixed configuration'],['Logistic regression','C = 0.1 or 1; balanced class weights; max_iter 2500'],['Random forest','min_samples_leaf = 3 or 8; 120 trees; max_features .7; balanced_subsample'],['XGBoost','max_depth = 2 or 3; 110 trees; rate .04; lambda 5; min_child_weight 4']],widths=[135,W-2*M-135],size=7.5)
    r.par('<b>Fold-local pipeline:</b> numeric median imputation/scaling; categorical mode imputation/one-hot. No global selection, SMOTE or merging. Class weights are training-only; XGBoost uses regularization.')
    r.par('<b>Calibration:</b> predeclared sigmoid; three-fold OOF within outer train, then base-estimator refit (<font name="Courier">ensemble=False</font>). Raw/isotonic: sensitivity only. Full-cohort artifacts use inner selection and refit.')
    r.par('<b>Scope:</b> headline metrics average two held-out models per patient; the workspace explains one fitted model. No external validation. Operating points appear separately (page 3).',color=MUTED)
    r.end()

    r.begin('03 / Measured predictive performance','Strong CAD; harder vessel tasks.','Primary metrics use one repeat-averaged held-out probability per patient. Scores below are from shipped artifacts.')
    rows=[['Target','AUC [95% CI]','Acc','Prec','Recall','F1','AP','Brier ↓']]
    for t,e in targets.items():
        m=e['metrics'];rows.append([t,f'{m["roc_auc"]:.3f}<br/>[{e["auc_ci"][0]:.3f}, {e["auc_ci"][1]:.3f}]',*[f'{m[k]:.3f}' for k in ['accuracy','precision','recall','f1','pr_auc','brier']]])
    r.table(rows,widths=[36,112,57,57,57,57,57,76],size=7,padding=4)
    r.par('Intervals: 1,000 patient-stratified bootstrap resamples conditional on fitted folds. They omit retraining/selection uncertainty and are not external-validation intervals. Fold SD is descriptive because folds overlap. AP is average precision.',size=7.5,color=MUTED,space=12)
    series=[(t,e['curves']['roc'],color) for (t,e),color in zip(targets.items(),COLORS)]
    chart(r.c,M,r.y-174,243,152,series,'ROC / all four targets','False positive rate','True positive rate')
    cal=[(t,e['curves']['calibration'],color) for (t,e),color in zip(targets.items(),COLORS)]
    chart(r.c,M+267,r.y-174,243,152,cal,'Calibration / six quantile bins','Estimated probability','Observed positive rate')
    r.y-=192
    for i,(t,color) in enumerate(zip(targets,COLORS)):
        r.c.setFillColor(color);r.c.circle(M+4+i*110,r.y,3,fill=1,stroke=0);r.c.setFont('Helvetica',8);r.c.drawString(M+13+i*110,r.y-3,t)
    r.y-=19
    refinement=json.loads((ROOT/'experiments/vessel_refinement/results.json').read_text(encoding='utf-8'))
    if (refinement['baseline_evidence_sha256']!=hashlib.sha256((ROOT/'ml/artifacts/evidence.json').read_bytes()).hexdigest()
            or refinement['baseline_registry_sha256']!=hashlib.sha256((ROOT/'ml/artifacts/registry.json').read_bytes()).hexdigest()):
        raise RuntimeError('Stale research evidence: run python -m ml.refine_vessels before building the report')
    r.heading('Training-selected research operating points')
    threshold_chart(r,refinement)
    r.par('Gray: fixed 0.50; purple: training-selected F1. Same models/probabilities. LCX recall .420 to .840 (119 positives); RCA .395 to .868 (114 positives). Negative counts: 184 / 189. F1 cutoffs use inner OOF from outer train only; pool mean probability-minus-cutoff per patient. AUC/Brier stay unchanged. Accuracy falls .673 to .630 / .660 to .617. Research tradeoffs, not clinical cutoffs.',size=7.5,color=MUTED,space=9)
    r.par('Neither the earlier ExtraTrees/SVM expansion nor the final elastic-net/HistGradientBoosting/CatBoost search showed a material policy gain. Final LCX/RCA AUC: .731/.733 versus .728/.732; paired delta intervals include zero. Original models retained. Reused splits are development evidence, not independent confirmation; full trial logs: experiments/final_audit.',size=7.5,color=MUTED,space=9)
    r.end()

    r.begin('04 / Interpretability & uncertainty','Explain the actual probability.','A contribution must explain the value the user sees, not an unrelated raw model margin.')
    r.flow([['Training background','Base probability'],['55 signed effects','Feature contributions'],['Displayed estimate','Reconstructed to 1e-6']],
           'Base + all signed contributions reconstruct the displayed calibrated probability.')
    r.par('<b>Local SHAP:</b> permutation explanations use the selected calibrated classifier and training-only background. Original categorical variables remain indivisible coalitions. Two cycles, 16/20 background patients, all 55 contributions. Reconstruction to 1e-6 checks additivity, not attribution precision.')
    r.heading('Held-out global explanation evidence')
    r.table([['Target','Leading absolute probability contributors','Rank stability'],*[ [t,', '.join(f['label'] for f in e['global_shap'][:4]),f'{e["shap_stability"]["mean_spearman"]:.3f}'] for t,e in targets.items()]],widths=[45,390,74],size=7.5)
    r.par('Global importance: mean absolute probability SHAP, six held-out patients x ten folds; background n=16, one cycle. Stability: mean pairwise Spearman correlation of fold rankings. Approximate, descriptive and noncausal; correlated features can share credit.',size=8,color=MUTED)
    r.heading('Three complementary limits on confidence')
    r.table([['Signal','Meaning and limitation'],['Candidate disagreement','Probability spread across three families exposes sensitivity to model choice. Not a confidence interval.'],['Refitted model range','Min/max of ten outer models; demo uses two excluding that patient. Descriptive; may omit the full-cohort estimate.'],['Profile representation','Standardized mixed-feature nearest-neighbor distance, cohort leave-one-out 95th percentile + single-feature range checks. Unvalidated heuristic.']],widths=[130,379],size=8)
    r.heading('Inspect failures, not only successes')
    r.par('Evidence Lab exposes sex/age subgroups, eight largest held-out errors per target and fixed-logistic 5-fold ECG/laboratory-echo ablations. Small samples support descriptive checks, not fairness certification. The demo includes a confident CAD miss; the source discrepancy remains visible.')
    r.par('<b>Boundary:</b> editing inputs explores model response, not treatment effect. Independent CAD/vessel classifiers may disagree; the UI exposes this. Attribution does not establish causality or clinical validity.',size=8.5,color=MUTED)
    r.end()

    r.begin('05 / 3D & end-to-end integration','Real anatomy, honest mapping.','A memorable interaction with traceable structure identity, not invented lesion localization.')
    r.image(ROOT/'demo/screenshots/coronary-anatomy.png',width=305,height=220)
    r.par('Actual interactive viewer. Heart-wall meshes, great vessels and independently selectable coronary branches are loaded locally; no asset network dependency during the demo.',size=7.5,color=MUTED)
    r.table([['Vessel mapping','Source geometry / identity'],['LAD','Anterior interventricular / anterior descending branches; trunk FJ2631'],['LCX','Circumflex branches of left coronary artery; FJ2649-FJ2654'],['RCA','Right coronary artery trunk and branches; trunk FJ2723']],widths=[110,399],size=8)
    r.par('<b>Asset:</b> BodyParts3D 4.0, DBCLS, CC BY 4.0; pinned human-atlas derivative. 63 meshes, 37,444 triangles, 1,071,048 bytes. Selected, recentered and uniformly scaled; source names/IDs retained. Generic adult male anatomy, not a patient image. No RWMA-to-lesion mapping or geometry deformation.')
    r.par('<b>Interaction:</b> rotate, zoom, pan, select vessel, orbit, X-ray, vessel isolation, reset and expanded view. Artery colors use model probabilities; projected labels connect to artery surface vertices. The artery guide explains typical course and supply, not patient injury. The renderer limits pixel ratio to 1.5. Software WebGL browser tests exercise the interface without a dedicated GPU; universal FPS is not claimed.')
    r.par('<b>System path:</b> Next.js clinical form → validated FastAPI request → calibrated CAD/LAD/LCX/RCA models → SHAP/uncertainty/OOD → probability, anatomy and explanation updates. Edited inputs mark previous results and explanations stale and block stale exports. API failures preserve the previous result and explain how to retry. Height and weight remain editable; BMI is derived. Cohort defaults are explicitly marked.')
    r.end()

    r.begin('06 / Reproducibility, usage & limits','Ready to run and review.','The software, model weights and evidence run locally without cloud credentials or inference APIs.')
    r.heading('Run the complete system')
    r.par('Python 3.13 and Node 24 recommended. First run: <font name="Courier">python scripts/start.py --setup</font>. Subsequent launches: <font name="Courier">python scripts/start.py</font>. Open <b>http://127.0.0.1:3000</b>. Select a held-out case → Predict → select vessels → inspect explanations → Evidence Lab. Optional Docker Compose packaging is supplied; Docker execution was not verified on this host.',size=9)
    r.table([['Reproduce / inspect','Command or artifact'],['Train and pair vessel audit','python -m ml.train (seed 2026; 5 x 2 outer folds)<br/>python -m ml.refine_vessels'],['Verify frozen OOF results','python -m ml.evaluate → experiments/metrics.csv'],['Critical validity checks','python -m pytest'],['Frontend checks','cd web; npm run typecheck; npm run lint; npm run build'],['Browser demo reliability','cd web; npx playwright install chromium; npx playwright test'],['Scientific artifacts','ml/artifacts/{CAD,LAD,LCX,RCA}.joblib; evidence.json; registry.json'],['Submission materials','README; data/model card; licenses; screenshots; five-minute demo script']],widths=[145,364],size=7.5)
    r.heading('Scope and limitations')
    r.par('Small single-center referral cohort with high CAD prevalence; no external clinical validation or longitudinal outcome prediction. Independent classifiers do not produce a validated joint probability. Vessel estimates are weaker, with low recall at the default threshold. Mixed-feature OOD and refit ranges are descriptive heuristics. No diagnosis, treatment advice, stenosis severity or lesion coordinates. Human review is required before submission; the final YouTube recording/upload uses the submitter’s account.',size=8.5)
    r.heading('Sources, licenses and AI disclosure')
    r.par('Official task: supplied <b>Track A.pdf</b>. Clinical data: Alizadehsani, Roshanzamir &amp; Sani, UCI Extension of Z-Alizadeh Sani, <b>DOI 10.24432/C5461K</b>, CC BY 4.0. Anatomy: <b>BodyParts3D / DBCLS</b>, CC BY 4.0; Mitsuhashi et al., DOI 10.1093/nar/gkn613; derivative pinned to human-atlas commit 1c38bf35c254a891200d3cedecfd57abebe83d8d. Original application code MIT; Manrope and IBM Plex Mono fonts OFL. Detailed attribution and dependency terms: ATTRIBUTIONS.md.',size=8)
    r.par('Method references: scikit-learn nested CV and probability calibration documentation; SHAP permutation explanations. Exact URLs and prior-winner research are in docs/RESEARCH.md. The six-page limit applies to this report; full audit tables remain in the software and artifacts.',size=8,color=MUTED)
    r.par('<b>AI assistance:</b> OpenAI Codex assisted research, coding, debugging, verification and drafting. The deployed product uses no generative model to predict, diagnose or advise. All reported model measurements are computed from the supplied cohort, not generated or copied.',size=8)
    r.end();r.c.save()
    print(f'Created {OUT} (6 pages)')


if __name__=='__main__':build()
