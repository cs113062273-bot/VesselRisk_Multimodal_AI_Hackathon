'use client';
import { useState } from 'react';
import { ArrowDownRight, ArrowUpRight, ChevronRight, Info, ShieldCheck } from 'lucide-react';
import { Evidence, NAMES, pct, Prediction, Risk, Target, TARGETS } from '@/lib/types';
import { measurementText } from '@/lib/clinical-display';
import InfoPopover from './InfoPopover';

function Contributors({risk}:{risk:Risk}) {
  const [all,setAll]=useState(false);
  const items=risk.explanation.contributions.slice(0,all?55:5);
  const max=Math.max(...items.map(f=>Math.abs(f.value)),.01);
  return <>
    <div className="contribution-heading"><span>PATIENT MEASUREMENT</span><span>CHANGE IN ESTIMATE</span></div>
    <div className="contributions">{items.map(f=><div className="contribution-row" key={f.feature}>
      <div><strong>{f.label}</strong><span>{measurementText(f.feature,f.input,f.unit)}</span></div>
      <div className="diverging-bar" aria-hidden="true"><span className={f.value>=0?'positive-bar':'negative-bar'} style={{width:`${Math.abs(f.value)/max*48}%`}}/></div>
      <b className={f.value>=0?'increase':'decrease'} aria-label={`${f.value>=0?'Raises':'Lowers'} the estimate by ${Math.abs(f.value*100).toFixed(1)} percentage points`}>{f.value>=0?'+':'−'}{Math.abs(f.value*100).toFixed(1)}<small>pp</small></b>
    </div>)}</div>
    <p className="impact-caption">“pp” means percentage points. These explain the model, not the effect of treatment.</p>
    <button className="text-button" onClick={()=>setAll(!all)}>{all?'Show top 5 factors':'View all 55 contributions'}<ChevronRight size={13}/></button>
  </>;
}

export default function ExplanationPanel({prediction,target,onTarget,evidence,onEvidence,latency,dirty,busy}:{prediction:Prediction|null;target:Target;onTarget:(t:Target)=>void;evidence:Evidence|null;onEvidence:()=>void;latency:number|null;dirty:boolean;busy:boolean}) {
  const risk=prediction?.targets[target];
  const ev=evidence?.targets[target];
  return <aside className={`explanation-panel ${dirty&&prediction?'explanation-stale':''}`} id="prediction-explanation" tabIndex={-1} aria-label="Prediction explanation">
    <div className="panel-title"><ShieldCheck size={18}/><h2>Why this estimate?</h2></div>
    {prediction&&dirty&&<div className="stale-explanation" role="status"><Info size={16}/><span><strong>{busy?'Updating explanation…':'Previous explanation'}</strong>Based on the last prediction. Edited inputs have not been applied.</span></div>}
    <div className="target-tabs" role="tablist" aria-label="Explanation target">{TARGETS.map(t=><button role="tab" aria-label={t} aria-selected={target===t} key={t} onClick={()=>onTarget(t)}><span>{t}</span><strong className={`target-probability ${prediction?(prediction.targets[t].probability<.3?'decrease':prediction.targets[t].probability<.6?'mid-probability':'increase'):''}`}>{prediction?(prediction.targets[t].probability*100).toFixed(1):'—'}{prediction&&<small>%</small>}</strong></button>)}</div>
    {!risk?<div className="explanation-empty"><h3>Start with a patient.</h3><ol className="first-look-steps">
      <li><span>01</span><div><strong>Predict</strong><p>Use the loaded case or enter your measurements.</p></div></li>
      <li><span>02</span><div><strong>Explore the heart</strong><p>Select an artery to bring it into view.</p></div></li>
      <li><span>03</span><div><strong>Understand the result</strong><p>See which measurements raised or lowered its estimate.</p></div></li>
    </ol></div>:<div className="explanation-content" key={`${target}-${prediction?.case_id}-${risk.probability}`}>
      <span className="eyebrow">{target==='CAD'?'OVERALL CAD':`${target} · SELECTED ARTERY`}</span>
      <div className="estimate-heading"><h3 className="target-name">{NAMES[target]}</h3>{target==='CAD'&&<InfoPopover label="CAD classification information" title="Overall CAD classification" buttonClassName="cad-classification" trigger={<><b className="cad-status">{risk.positive?'Positive':'Negative'}</b><Info size={14}/></>}>
        <p>The percentage is the model&apos;s estimated probability of CAD. Positive / negative uses a research cutoff of {(risk.threshold*100).toFixed(0)}%.</p>
        <p>This cutoff is a model decision rule, not a measure of narrowing or a clinical diagnosis.</p>
      </InfoPopover>}</div>
      <div className="explain-section-title"><h3>Top influences</h3><div className="direction-key"><span><ArrowUpRight size={12}/>Raises</span><span><ArrowDownRight size={12}/>Lowers</span></div></div>
      <Contributors risk={risk}/>
      {prediction?.ood.flag&&<div className="representation flagged"><Info size={16}/><div><strong>Unusual patient profile</strong><p>These measurements differ from the training cohort. Estimates may be less reliable.</p></div></div>}
      {ev&&<button className="evidence-link" onClick={onEvidence}><span>{target} model validation<span>{ev.n} patients · internal validation<br/>No external clinical validation</span></span><ChevronRight size={17}/></button>}
      <details className="model-details"><summary>Model & calculation details</summary>
        <dl className="model-facts"><dt>Model</dt><dd>{risk.family}</dd><dt>Calibration</dt><dd>Sigmoid</dd><dt>Classification</dt><dd>{risk.positive?'Positive':'Negative'} at {(risk.threshold*100).toFixed(0)}% research cutoff</dd><dt>Validation</dt><dd>303 patients · internal validation only</dd><dt>Result source</dt><dd>{prediction?.mode}</dd><dt>Response</dt><dd>{latency??'—'} ms · {prediction?.version}</dd></dl>
        <p>{prediction?.case_id?'This dataset patient was excluded from this model’s training.':'This profile uses a model fitted on the full cohort.'} Reported validation averages two held-out predictions per patient.</p>
        <h4>Variation across fitted models</h4>
        <div className="range-display"><div><span>{risk.range_models} models</span><b>{pct(risk.resampling_range[0])} – {pct(risk.resampling_range[1])}</b></div><div className="range-track"><i style={{left:`${risk.resampling_range[0]*100}%`,width:`${(risk.resampling_range[1]-risk.resampling_range[0])*100}%`}}/><b style={{left:`${risk.probability*100}%`}}/></div><p>Observed prediction range, not a clinical confidence interval.</p></div>
        <h4>Do different models agree?</h4><div className="agreement-list">{risk.agreement.map(m=><div key={m.family}><span>{m.family}</span><div><i style={{width:`${m.probability*100}%`}}/></div><b>{pct(m.probability)}</b></div>)}</div>
        <h4>How the contributions add up</h4><div className="shap-total"><span>Reference <b>{pct(risk.explanation.base_probability)}</b></span><span>+ all factors</span><span><b>{pct(risk.explanation.reconstructed_probability)}</b></span></div>
        <p>Permutation SHAP attributes the displayed calibrated probability to the inputs. The reference is the model’s average output on its explanation background, not population prevalence. Correlated measurements can share attribution.</p>
      </details>
    </div>}
  </aside>;
}
