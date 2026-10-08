'use client';
import { useState } from 'react';
import { ArrowRight, ChevronDown, ClipboardList, RotateCcw, Search, Upload } from 'lucide-react';
import { DemoCase, Feature, Features } from '@/lib/types';
import { calculateBmi } from '@/lib/patient-profile';

const GROUPS=['Demographics & history','Symptoms & examination','ECG','Laboratory & echo'];
const BODY_FIELDS=['Age','Sex','Length','Weight','BMI'];
const IMPORTANT=[...BODY_FIELDS,'BP','PR','Typical Chest Pain','DM','HTN','LDL','HDL','FBS','EF-TTE','Region RWMA'];
function display(v:number|string,name:string){return v==='Fmale'?'Female':v==='Y'?'Yes':v==='N'?'No':typeof v==='number'&&['DM','HTN','Typical Chest Pain','Q Wave','St Elevation','St Depression','Tinversion','Current Smoker','EX-Smoker','FH','Edema'].includes(name)?v===1?'Yes':'No':String(v);}

export default function PatientPanel({schema,cases,features,caseId,onCase,onChange,onPredict,busy,dirty,onImport}:{schema:Feature[];cases:DemoCase[];features:Features;caseId:string|null;onCase:(id:string)=>void;onChange:(name:string,value:string|number)=>void;onPredict:()=>void;busy:boolean;dirty:boolean;onImport:(features:Features)=>void}){
  const [tab,setTab]=useState('Key inputs');
  const [search,setSearch]=useState('');
  const [importError,setImportError]=useState('');
  const visible=schema.filter(f=>tab==='Key inputs'?IMPORTANT.includes(f.name):f.group===tab)
    .sort((a,b)=>{
      const rank=(name:string)=>BODY_FIELDS.includes(name)?BODY_FIELDS.indexOf(name):BODY_FIELDS.length;
      return rank(a.name)-rank(b.name);
    }).filter(f=>`${f.name} ${f.label}`.toLowerCase().includes(search.toLowerCase()));
  const current=cases.find(c=>c.id===caseId);
  return <aside className="patient-panel">
    <div className="panel-title"><ClipboardList size={18}/><h2>Patient profile</h2><span className="quiet-tag">55 inputs</span></div>
    <div className="case-picker"><label htmlFor="demo-case">Explore a held-out case</label><div className="select-wrap"><select id="demo-case" value={caseId??'custom'} onChange={e=>onCase(e.target.value)} disabled={busy}>{cases.map(c=><option value={c.id} key={c.id}>{c.title}</option>)}<option value="custom">New profile · cohort defaults</option></select><ChevronDown size={15}/></div><p>{current?.description??'Defaults are cohort medians and modes. Review every group.'}</p></div>
    <div className="input-tabs" role="tablist" aria-label="Clinical input groups">{['Key inputs',...GROUPS].map(g=><button key={g} role="tab" aria-selected={tab===g} onClick={()=>setTab(g)}>{g==='Demographics & history'?'History':g==='Symptoms & examination'?'Symptoms':g==='Laboratory & echo'?'Labs & echo':g}</button>)}</div>
    <label className="search-input"><Search size={14}/><input aria-label="Search clinical inputs" placeholder="Find a measurement…" value={search} onChange={e=>setSearch(e.target.value)}/></label>
    <form onSubmit={e=>{e.preventDefault();onPredict();}} className="clinical-form">
      <div className="fields-scroll">{visible.map(f=>{
        const derived=f.name==='BMI';
        const value=features[f.name]??f.default;
        return <label key={f.name} className={`clinical-field ${f.kind==='category'?'category-field':''}`}>
          <span>{f.label}<small>{f.unit}</small></span>
          {f.kind==='category'?<select value={String(value)} onChange={e=>{const next=f.options!.find(v=>String(v)===e.target.value)!;onChange(f.name,next);}} disabled={busy||f.constant} aria-label={f.label}>{f.options?.map(v=><option key={String(v)} value={String(v)}>{display(v,f.name)}</option>)}</select>:
            <input type={derived?'text':'number'} readOnly={derived} required={!derived} step={f.integer?1:'any'} value={derived?(value===''?'':Number(value).toFixed(2)):value} onChange={derived?undefined:e=>onChange(f.name,e.target.value===''?'':Number(e.target.value))} disabled={busy} aria-label={f.label} aria-describedby={derived?'bmi-note':undefined}/>}
          <span className="observed-range" id={derived?'bmi-note':undefined}>{derived?'Auto-calculated from height & weight':f.constant?'Constant in cohort':f.kind==='number'?`Cohort: ${f.min?.toFixed(f.integer?0:1)}–${f.max?.toFixed(f.integer?0:1)}`:f.name==='Region RWMA'?'Source category code; no spatial coordinates':''}</span>
        </label>;
      })}{!visible.length&&<p className="muted">No matching inputs in this group.</p>}</div>
      <div className="input-footer"><p><i className={dirty?'dirty-dot':'ready-dot'}/>{calculateBmi(features)===''?'Enter a positive height and weight':dirty?'Inputs changed · run to update all targets':caseId?'Real cohort case · excluded from its models':'Review defaults before interpreting estimates'}</p><button className="primary-button" type="submit" disabled={busy||calculateBmi(features)===''}>{busy?<><span className="loader small"/>Estimating & explaining…</>:<>Predict coronary risk<ArrowRight size={17}/></>}</button><div className="input-actions"><button type="button" disabled={busy} onClick={()=>onCase(caseId??'custom')}><RotateCcw size={13}/>Reset inputs</button><label className="import-button"><Upload size={13}/>Import JSON<input type="file" accept=".json,application/json" disabled={busy} onChange={async e=>{try{const file=e.target.files?.[0];if(!file)return;const j=JSON.parse(await file.text());onImport(j.features??j);setImportError('');}catch{setImportError('Choose a JSON object with the 55 source feature names.');}e.target.value='';}}/></label></div>{importError&&<p role="alert" className="error-text">{importError}</p>}</div>
    </form>
    <div className="leakage-seal"><span>✓</span><div><strong>Leakage guard active</strong><p>LAD, LCX, RCA & Cath excluded from all inputs.</p></div></div>
  </aside>;
}
