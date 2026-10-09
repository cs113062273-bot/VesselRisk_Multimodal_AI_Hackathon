'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { Activity, ArrowRight, BookOpen, Download, FlaskConical, Info, LayoutDashboard, RefreshCw, ShieldCheck, X } from 'lucide-react';
import PatientPanel from '@/components/PatientPanel';
import ExplanationPanel from '@/components/ExplanationPanel';
import EvidenceLab from '@/components/EvidenceLab';
import { calculateBmi, withCalculatedBmi } from '@/lib/patient-profile';
import { api, DemoCase, downloadJSON, Evidence, Feature, Features, Prediction, Registry, Target, TARGETS } from '@/lib/types';

const HeartViewer=dynamic(()=>import('@/components/HeartViewer'),{ssr:false,loading:()=> <div className="heart-loading"><span className="loader"/>Preparing 3D viewer…</div>});

export default function Home(){
  const [view,setView]=useState<'workspace'|'evidence'>('workspace');
  const [schema,setSchema]=useState<Feature[]>([]);
  const [cases,setCases]=useState<DemoCase[]>([]);
  const [features,setFeatures]=useState<Features>({});
  const [caseId,setCaseId]=useState<string|null>(null);
  const [prediction,setPrediction]=useState<Prediction|null>(null);
  const [focusVersion,setFocusVersion]=useState(0);
  const [viewerOpened,setViewerOpened]=useState(false);
  const markViewerOpened=useCallback(()=>setViewerOpened(true),[]);
  const [evidence,setEvidence]=useState<Evidence|null>(null);
  const [registry,setRegistry]=useState<Registry|null>(null);
  const [target,setTarget]=useState<Target>('LAD');
  const [busy,setBusy]=useState(false);
  const [profileCollapsed,setProfileCollapsed]=useState(false);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState('');
  const [dirty,setDirty]=useState(false);
  const [showSafety,setShowSafety]=useState(false);
  const [reveal,setReveal]=useState(false);
  const [latency,setLatency]=useState<number|null>(null);
  const [predictedFeatures,setPredictedFeatures]=useState<Features>({});
  const serial=useRef(0);
  useEffect(()=>{
    let live=true;
    Promise.all([api<{features:Feature[]}>('/schema'),api<{cases:DemoCase[]}>('/cases'),api<Evidence>('/evidence'),api<Registry>('/model-info')]).then(([s,c,e,r])=>{
      if(!live)return;setSchema(s.features);setCases(c.cases);setEvidence(e);setRegistry(r);
      const initial=c.cases[0];
      setFeatures(initial.features);setCaseId(initial.id);setLoading(false);
    }).catch(e=>{if(live){setError(e.message);setLoading(false);}});
    return ()=>{live=false;};
  },[]);
  function changeCase(id:string){
    const c=cases.find(x=>x.id===id);
    setCaseId(c?.id??null);setFeatures(c?{...c.features}:withCalculatedBmi(Object.fromEntries(schema.map(f=>[f.name,f.default]))));
    setDirty(true);setReveal(false);setError('');
  }
  function changeFeature(name:string,value:string|number){
    if(name==='BMI')return;
    setFeatures(prev=>{
      const next={...prev,[name]:value};
      return name==='Length'||name==='Weight'?withCalculatedBmi(next):next;
    });
    setDirty(true);setError('');
  }
  async function predict(){
    if(calculateBmi(features)===''){setError('Enter a positive height and weight to calculate BMI before predicting.');return;}
    const request=++serial.current;setBusy(true);setError('');const start=performance.now();
    try{
      const p=await api<Prediction>('/predict',{method:'POST',body:JSON.stringify({features,case_id:caseId})});
      const elapsed=Math.round(performance.now()-start);
      // Keep fast responses visible long enough to acknowledge the action.
      await new Promise<void>(resolve=>setTimeout(resolve,Math.max(0,600-elapsed)));
      if(request!==serial.current)return;
      setPrediction(p);setPredictedFeatures({...features});setLatency(elapsed);setDirty(false);setReveal(false);
      setProfileCollapsed(true);
    }catch(e){setError(e instanceof Error?e.message:'Prediction failed. Check the model service and try again.');}
    finally{if(request===serial.current)setBusy(false);}
  }
  function selectTarget(t:Target){setTarget(t);setFocusVersion(n=>n+1);}
  function inspectEvidence(){setView('evidence');window.scrollTo({top:0,behavior:'smooth'});}
  return <div className="app-shell">
    <header className={`app-header ${view==='workspace'&&!loading&&schema.length?'workspace-header':''}`}>
      <button className="brand" aria-label="VesselRisk home" onClick={()=>setView('workspace')}><span className="brand-icon"><Activity size={24}/></span><span>Vessel<span className="brand-light">Risk</span><small>EXPLAINABLE CORONARY RISK</small></span></button>
      {view==='workspace'&&!loading&&schema.length>0&&<div className="header-workspace-title"><h1 id="workspace-title">Explore coronary risk.</h1><p>Predict a patient profile. Select an artery. See what shaped its estimate.</p></div>}
      <nav aria-label="Primary navigation"><button className={view==='workspace'?'active':''} onClick={()=>setView('workspace')}><LayoutDashboard size={16}/>Patient workspace</button><button className={view==='evidence'?'active':''} onClick={inspectEvidence}><FlaskConical size={16}/>Evidence Lab</button></nav>
      <div className="header-meta">
        {view==='workspace'&&!loading&&schema.length>0&&<button className="secondary-button header-export" aria-label="Export case" title="Export case" disabled={!prediction||dirty||busy} onClick={()=>downloadJSON('vesselrisk-patient-evidence.json',{features:predictedFeatures,...prediction})}><Download size={15}/><span>Export case</span></button>}
        <button className="icon-button" onClick={()=>setShowSafety(true)} aria-label="About this research system"><Info size={18}/></button>
      </div>
    </header>
    {loading?<main className="loading-screen"><span className="loader"/><h1>Loading model evidence</h1><p>Connecting to the local clinical model service.</p></main>:schema.length===0?<main className="loading-screen"><Info size={28}/><h1>The model service is unavailable</h1><p>{error}</p><button className="primary-button" onClick={()=>window.location.reload()}><RefreshCw size={16}/>Reconnect</button><p>Start the project with <code>python scripts/start.py</code>.</p></main>:view==='evidence'&&evidence&&registry?<EvidenceLab {...{evidence,registry,target}} onTarget={selectTarget}/>:<main className="workspace page-enter">
      {error&&<div className="error-banner" role="alert"><Info size={17}/><span>{error}</span><button onClick={()=>setError('')} aria-label="Dismiss error"><X size={16}/></button></div>}
      <PatientPanel {...{schema,cases,features,caseId,busy}} collapsed={profileCollapsed} onToggle={()=>setProfileCollapsed(value=>!value)} onCase={changeCase} onChange={changeFeature} onPredict={predict} onImport={f=>{setFeatures(withCalculatedBmi(f));setCaseId(null);setDirty(true);setError('');}}/>
      <div className="workspace-grid workspace-results">
        <div className={`anatomy-workspace ${dirty&&prediction?'results-stale':''}`} id="prediction-results" tabIndex={-1} aria-label="Prediction results">
          <HeartViewer {...{prediction,target,focusVersion,dirty}} initialOrbit={!viewerOpened} onOpened={markViewerOpened} onSelect={selectTarget}/>
        </div>
        <ExplanationPanel {...{prediction,target,evidence,latency,dirty,busy}} onTarget={selectTarget} onEvidence={inspectEvidence}/>
      </div>
      {prediction&&<div className="case-review"><div><ShieldCheck size={17}/><p>{prediction.observed?'Compare the prediction with the recorded angiographic result.':prediction.case_id?'Edited inputs show how the model responds.':'Prediction for the entered patient profile.'}</p></div>{prediction.observed&&<button className="text-button" onClick={()=>setReveal(!reveal)} disabled={dirty}>{reveal?'Hide recorded outcomes':'Reveal recorded outcomes'}<ArrowRight size={14}/></button>}{reveal&&!dirty&&prediction.observed&&<div className="recorded-outcomes">{TARGETS.map(t=><span key={t}><b>{t}</b>{prediction.observed![t]?'Recorded positive':'Recorded negative'}<small>Model {prediction.targets[t].positive?'positive':'negative'}{prediction.targets[t].positive===!!prediction.observed![t]?' · agrees':' · missed'}</small></span>)}</div>}</div>}
      {prediction&&prediction.warnings.length>1&&<div className="prediction-warnings">{prediction.warnings.slice(1).map(w=><p key={w}><Info size={14}/>{w}</p>)}</div>}
    </main>}
    <footer className="safety-footer"><ShieldCheck size={17}/><p><strong>Research & education only.</strong> Not a diagnosis, treatment advice, or a substitute for formal diagnostic imaging. Colors represent vessel-level probability, not lesion location.</p><button onClick={()=>setShowSafety(true)}>Scope & limitations <ArrowRight size={13}/></button></footer>
    {showSafety&&<div className="modal-backdrop" onClick={()=>setShowSafety(false)}><section className="safety-modal" role="dialog" aria-modal="true" aria-labelledby="safety-title" onClick={e=>e.stopPropagation()}><button className="modal-close icon-button" aria-label="Close scope and limitations" onClick={()=>setShowSafety(false)}><X size={19}/></button><span className="eyebrow">SCOPE & LIMITATIONS</span><h2 id="safety-title">Evidence before confidence.</h2><p>VesselRisk estimates overall CAD and vessel-level stenosis from structured clinical inputs. It combines demographic, examination, ECG, and laboratory/echo feature groups with a reference 3D coronary model.</p><ul>{evidence?.protocol.limitations.map(l=><li key={l}>{l}</li>)}</ul><p>The anatomy is generic BodyParts3D reference anatomy, not a patient scan. We never infer lesion coordinates from RWMA or deform a vessel to imply measured narrowing.</p><p>Research threshold 0.50 and visual color bands are display conventions. They are not validated clinical risk categories. Refitted model ranges are not confidence intervals.</p><div className="modal-actions"><button className="primary-button" onClick={()=>{setShowSafety(false);inspectEvidence();}}>Inspect validation<ArrowRight size={16}/></button><a className="secondary-button" href="/api/report" target="_blank"><BookOpen size={15}/>Technical report</a></div></section></div>}
  </div>;
}
