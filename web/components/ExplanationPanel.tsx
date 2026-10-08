'use client';
import { useState } from 'react';
import { ArrowDownRight, ArrowUpRight, ChevronRight, Info, ShieldCheck } from 'lucide-react';
import { Evidence, NAMES, pct, Prediction, Risk, score, Target, TARGETS } from '@/lib/types';

function Contributors({risk}:{risk:Risk}){
  const [all,setAll]=useState(false);
  const items=risk.explanation.contributions.slice(0,all?55:7);
  const max=Math.max(...items.map(f=>Math.abs(f.value)),.01);
  return <><div className="contribution-heading"><span>MEASUREMENT</span><span>PROBABILITY IMPACT</span></div><div className="contributions">{items.map(f=><div className="contribution-row" key={f.feature}><div><strong>{f.label}</strong><span>{f.input==='Fmale'?'Female':String(f.input)} {f.unit}</span></div><div className="diverging-bar"><span className={f.value>=0?'positive-bar':'negative-bar'} style={{width:`${Math.abs(f.value)/max*48}%`}}/></div><b className={f.value>=0?'increase':'decrease'}>{f.value>=0?'+':''}{(f.value*100).toFixed(1)}<small>pp</small></b></div>)}</div><button className="text-button" onClick={()=>setAll(!all)}>{all?'Show strongest contributions':'View all 55 contributions'}<ChevronRight size={13}/></button><div className="shap-total"><span>Background <b>{pct(risk.explanation.base_probability)}</b></span><span>+ contributions</span><span><b>{pct(risk.explanation.reconstructed_probability)}</b></span></div><p className="fine-print">Permutation SHAP explains the exact calibrated probability. “pp” = percentage points. Associations, not causes or treatment effects.</p></>;
}

export default function ExplanationPanel({prediction,target,onTarget,evidence,onEvidence}:{prediction:Prediction|null;target:Target;onTarget:(t:Target)=>void;evidence:Evidence|null;onEvidence:()=>void}){
  const risk=prediction?.targets[target];
  const ev=evidence?.targets[target];
  return <aside className="explanation-panel"><div className="panel-title"><ShieldCheck size={18}/><h2>Behind the estimate</h2></div><div className="target-tabs" role="tablist" aria-label="Explanation target">{TARGETS.map(t=><button role="tab" aria-selected={target===t} key={t} onClick={()=>onTarget(t)}>{t}</button>)}</div>
    {!risk?<div className="explanation-empty"><span className="eyebrow">START HERE</span><h3>From patient to explanation.</h3><ol className="first-look-steps"><li><span>01</span><div><strong>Predict this profile</strong><p>Use “Predict coronary risk” in the patient panel to estimate all four targets.</p></div></li><li><span>02</span><div><strong>Select an artery</strong><p>Choose LAD, LCX or RCA on the heart. Its estimate and contributing measurements appear here.</p></div></li><li><span>03</span><div><strong>Inspect the evidence</strong><p>Open Evidence Lab for held-out results, calibration and failure cases.</p></div></li></ol><p className="first-look-scope">Reference anatomy shows vessel-level probability, not the location of a lesion.</p></div>:<div className="explanation-content" key={`${target}-${prediction?.case_id}-${risk.probability}`}>
      <span className="eyebrow">{target==='CAD'?'OVERALL CAD':`${target} STENOSIS ESTIMATE`}</span><h3 className="target-name">{NAMES[target]}</h3><div className="detail-probability"><strong>{(risk.probability*100).toFixed(1)}<small>%</small></strong><span>Sigmoid calibrated<br/><b>{risk.family}</b></span></div>
      <p className="fine-print">{prediction?.case_id?'One held-out fold model.':'One full-cohort fitted model.'} Validation below averages two held-out predictions per patient.</p>
      <div className="range-display"><div><span>Refitted model range</span><b>{pct(risk.resampling_range[0])} – {pct(risk.resampling_range[1])}</b></div><div className="range-track"><i style={{left:`${risk.resampling_range[0]*100}%`,width:`${(risk.resampling_range[1]-risk.resampling_range[0])*100}%`}}/><b style={{left:`${risk.probability*100}%`}}/></div><p>{risk.range_models} {prediction?.case_id?'held-out':'outer-fold'} models · descriptive range, not a clinical confidence interval.</p></div>
      <div className="explain-section-title"><h3>What moved this estimate?</h3><div className="direction-key"><span><ArrowUpRight size={12}/>Raises</span><span><ArrowDownRight size={12}/>Lowers</span></div></div><Contributors risk={risk}/>
      <div className="explain-section-title"><h3>Do the models agree?</h3><span className={risk.agreement_spread>.25?'amber-text':'muted'}>{Math.round(risk.agreement_spread*100)} pp spread</span></div><div className="agreement-list">{risk.agreement.map(m=><div key={m.family}><span>{m.family}</span><div><i style={{width:`${m.probability*100}%`}}/></div><b>{pct(m.probability)}</b></div>)}</div>
      <div className={`representation ${prediction?.ood.flag?'flagged':''}`}><Info size={16}/><div><strong>{prediction?.ood.flag?'Limited profile representation':'Internal cohort evidence only'}</strong><p>{prediction?.ood.flag?'Measurements differ from the reference cohort. Treat estimates with extra caution.':'303 patients. No external clinical validation.'}</p></div></div>
      {ev&&<button className="evidence-link" onClick={onEvidence}><span>Inspect {target} validation<span>AUC {score(ev.metrics.roc_auc)} · Brier {score(ev.metrics.brier)}</span></span><ChevronRight size={17}/></button>}
    </div>}
  </aside>;
}
