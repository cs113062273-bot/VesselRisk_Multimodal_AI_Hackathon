import { ArrowRight, Database, GitBranch, ShieldCheck, BarChart3 } from 'lucide-react';
import { Evidence, NAMES, pct, Registry, score, Target, TARGETS } from '@/lib/types';
import { TargetOverview } from './EvidenceCharts';
import styles from './ModelEvidence.module.css';
import { targetColorStyle } from '@/lib/target-colors';

export default function ModelEvidenceOverview({evidence,registry,target,onValidation}:{
  evidence:Evidence;registry:Registry;target:Target;onValidation:(target:Target)=>void;
}) {
  const steps = [
    {icon:Database,title:'Clinical data',text:'303 patients · 55 eligible inputs',detail:'Demographics, examination, ECG, labs & echo'},
    {icon:ShieldCheck,title:'Protect each split',text:'Four outcome columns excluded',detail:'Preprocessing and calibration inside training folds'},
    {icon:GitBranch,title:'Select & calibrate',text:'Three candidate model families',detail:'3-fold inner selection · sigmoid calibration'},
    {icon:BarChart3,title:'Evaluate held-out patients',text:'5 folds × 2 repeats',detail:'Two held-out predictions averaged per patient'},
  ];
  return <>
    <section className={styles.workflow} aria-label="Training and evaluation workflow"><div className={styles.sectionHeading}><h2>From data to evaluated predictions</h2><span>Training & validation pipeline</span></div>
      <div className={styles.steps}>{steps.map(({icon:Icon,title,text,detail},i)=><div key={title}><Icon size={20}/><h3>{title}</h3><strong>{text}</strong><p>{detail}</p>{i<steps.length-1&&<ArrowRight className={styles.stepArrow} size={16}/>}</div>)}</div>
    </section>
    <section className={styles.results} aria-label="All target validation results"><div className={styles.sectionHeading}><div><h2>Four targets. One evaluation protocol.</h2><p>Classification at a 50% research cutoff. Select a target to inspect its evidence.</p></div><span>303 patients · internal validation</span></div>
      <table><thead><tr><th>Prediction target</th><th>Accuracy</th><th>Recall</th><th>F1</th><th>ROC-AUC ↑</th><th>Brier ↓</th><th>Missed positives</th><th/></tr></thead><tbody>{TARGETS.map(t=>{const ev=evidence.targets[t];return <tr key={t} data-evidence-target={t} style={targetColorStyle(t)}><td><b>{t}</b><span>{NAMES[t]}</span></td><td>{pct(ev.metrics.accuracy)}</td><td>{pct(ev.metrics.recall)}</td><td>{score(ev.metrics.f1)}</td><td><strong>{score(ev.metrics.roc_auc)}</strong></td><td>{score(ev.metrics.brier)}</td><td>{ev.metrics.confusion_matrix[1][0]} / {ev.positive}</td><td><button aria-label={`View ${t} performance`} onClick={()=>onValidation(t)}><ArrowRight size={17}/></button></td></tr>})}</tbody></table>
      <p className={styles.caveat}>LCX and RCA detect fewer than half of recorded positives at this cutoff. Internal validation does not establish clinical performance on a new population.</p>
    </section>
    <div className={styles.overviewGraph}><TargetOverview evidence={evidence} target={target} onTarget={onValidation}/></div>
    <section className={styles.foundation}><div><h3>What is being measured?</h3><p>Existing CAD and vessel-level stenosis labels. These are not future event risks, blockage severity, or lesion coordinates.</p></div><div><h3>What is reproducible?</h3><p>Fixed seed {registry.seed}, recorded data and model hashes, fold assignments, fitted artifacts and the explanation protocol.</p></div><div><h3>What remains unverified?</h3><p>External clinical performance. Refitted model ranges and model disagreement are descriptive, not clinical confidence intervals.</p></div></section>
  </>;
}
