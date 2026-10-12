'use client';
import type { ReactNode } from 'react';
import { ArrowDownRight, ArrowUpRight, Info } from 'lucide-react';
import { NAMES, pct, Prediction, Risk, Target, TARGETS } from '@/lib/types';
import { measurementText } from '@/lib/clinical-display';
import InfoPopover from './InfoPopover';
import { TARGET_COLORS } from '@/lib/target-colors';

export function Contributors({risk,all=false}:{risk:Risk;all?:boolean}) {
  const items=risk.explanation.contributions.slice(0,all?55:5);
  const max=Math.max(...items.map(f=>Math.abs(f.value)),.01);
  return <>
    <div className="explain-section-title"><h3>{all?'All input contributions':'Top influences'}</h3><div className="direction-key"><span><ArrowUpRight size={12}/>Raises</span><span><ArrowDownRight size={12}/>Lowers</span><InfoPopover label="About percentage points" title="Reading feature contributions" buttonClassName="contribution-unit" trigger={<>pp <Info size={12}/></>}><p>pp = percentage points. +7.4 pp moves a probability from 60% to 67.4%.</p><p>Contributions explain the model, not the effect of treatment. Changing a measurement does not imply the same change in disease probability.</p></InfoPopover></div></div>
    <div className="contributions">{items.map(f=><div className="contribution-row" key={f.feature}>
      <div><strong>{f.label}</strong><span>{measurementText(f.feature,f.input,f.unit)}</span></div>
      <div className="diverging-bar" aria-hidden="true"><span className={f.value>=0?'positive-bar':'negative-bar'} style={{width:`${Math.abs(f.value)/max*48}%`}}/></div>
      <b className={f.value>=0?'increase':'decrease'} aria-label={`${f.value>=0?'Raises':'Lowers'} the estimate by ${Math.abs(f.value*100).toFixed(1)} percentage points`}>{f.value>=0?'+':'−'}{Math.abs(f.value*100).toFixed(1)}<small>pp</small></b>
    </div>)}</div>
  </>;
}

export default function ExplanationPanel({prediction,target,onTarget,latency,dirty,busy,children}:{prediction:Prediction|null;target:Target;onTarget:(t:Target)=>void;latency:number|null;dirty:boolean;busy:boolean;children?:ReactNode}) {
  const risk=prediction?.targets[target];
  return <aside className={`explanation-panel ${!prediction?'explanation-unpredicted':''} ${dirty&&prediction?'explanation-stale':''}`} id="prediction-explanation" tabIndex={-1} aria-label="Prediction explanation">
    <div className="panel-title"><h2>Coronary Risk Prediction</h2></div>
    {prediction&&dirty&&<div className="stale-explanation" role="status"><Info size={16}/><span><strong>{busy?'Updating explanation…':'Previous explanation'}</strong>Based on the last prediction. Edited inputs have not been applied.</span></div>}
    <div className="target-tabs" role="tablist" aria-label="Explanation target">{TARGETS.map(t=><button role="tab" aria-label={t} aria-selected={target===t} key={t} onClick={()=>onTarget(t)}><span style={{color:TARGET_COLORS[t].ink}}>{t}</span><strong className={`target-probability ${prediction?(prediction.targets[t].probability<.3?'decrease':prediction.targets[t].probability<.6?'mid-probability':'increase'):''}`}>{prediction?(prediction.targets[t].probability*100).toFixed(1):'—'}{prediction&&<small>%</small>}</strong></button>)}</div>
    {!risk?<div className="explanation-empty"><h3>Start with a patient.</h3><ol className="first-look-steps">
      <li><span>01</span><div><strong>Predict</strong><p>Use the loaded case or enter your measurements.</p></div></li>
      <li><span>02</span><div><strong>Explore the heart</strong><p>Select an artery to bring it into view.</p></div></li>
      <li><span>03</span><div><strong>Understand the result</strong><p>See which measurements raised or lowered its estimate.</p></div></li>
    </ol>{children}</div>:<div className="explanation-content" key={`${target}-${prediction?.case_id}-${risk.probability}`}>
      <div className="estimate-summary">
      <div className="estimate-heading"><h3 className="target-name">{NAMES[target]}</h3>{target==='CAD'&&<InfoPopover label="CAD classification information" title="Overall CAD classification" buttonClassName="cad-classification" trigger={<><b className="cad-status">{risk.positive?'Positive':'Negative'}</b><Info size={14}/></>}>
        <p>The percentage is the model&apos;s estimated probability of CAD. Positive / negative uses a research cutoff of {(risk.threshold*100).toFixed(0)}%.</p>
        <p>This cutoff is a model decision rule, not a measure of narrowing or a clinical diagnosis.</p>
      </InfoPopover>}</div></div>
      <section className="patient-reason" aria-label="How the contributions add up">
        <div><span title="Average model output on the SHAP background, not population prevalence">Explanation background</span><b>{pct(risk.explanation.base_probability)}</b></div>
        <div className={risk.explanation.reconstructed_probability>=risk.explanation.base_probability?'increase':'decrease'}><span>Combined input contribution</span><b>{risk.explanation.reconstructed_probability>=risk.explanation.base_probability?'+':'−'}{Math.abs((risk.explanation.reconstructed_probability-risk.explanation.base_probability)*100).toFixed(1)}<small> pp</small></b></div>
        <div><span>This patient</span><b>{pct(risk.explanation.reconstructed_probability)}</b></div>
      </section>
      <Contributors risk={risk}/>
      {prediction?.ood.flag&&<div className="representation flagged"><Info size={16}/><div><strong>Unusual patient profile</strong><p>These measurements differ from the training cohort. Estimates may be less reliable.</p></div></div>}
      {children}
      <details className="model-details"><summary onClick={event=>{
        if(event.currentTarget.parentElement?.hasAttribute('open'))return;
        const panel=event.currentTarget.closest<HTMLElement>('.explanation-panel');
        if(panel)panel.style.setProperty('--expanded-panel-height',`${panel.getBoundingClientRect().height}px`);
      }}>All 55 inputs & calculation details</summary>
        <Contributors risk={risk} all/>
        <dl className="model-facts"><dt>Model</dt><dd>{risk.family}</dd><dt>Calibration</dt><dd>Sigmoid</dd><dt>Research cutoff</dt><dd>{(risk.threshold*100).toFixed(0)}%</dd><dt>Result source</dt><dd>{prediction?.mode}</dd><dt>Response</dt><dd>{latency??'—'} ms · {prediction?.version}</dd></dl>
        <p>{prediction?.case_id?'This dataset patient was excluded from this model’s training.':'This profile uses a model fitted on the full cohort.'}</p>
        <p>Permutation SHAP attributes the displayed calibrated probability to the inputs. The reference is the model’s average output on its explanation background, not population prevalence. Correlated measurements can share attribution.</p>
      </details>
    </div>}
  </aside>;
}
