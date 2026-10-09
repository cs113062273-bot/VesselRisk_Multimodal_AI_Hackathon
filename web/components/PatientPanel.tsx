'use client';
import { useRef, useState } from 'react';
import { ArrowRight, ChevronDown, ClipboardList, RotateCcw, Search, Upload } from 'lucide-react';
import { DemoCase, Feature, Features } from '@/lib/types';
import { calculateBmi } from '@/lib/patient-profile';

const GROUPS=['Demographics & history','Symptoms & examination','ECG','Laboratory & echo'];
const BODY_FIELDS=['Age','Sex','Length','Weight','BMI'];
const IMPORTANT=[...BODY_FIELDS,'BP','PR','Typical Chest Pain','DM','HTN','LDL','HDL','FBS','EF-TTE','Region RWMA'];
const INPUT_VIEWS=['Key inputs',...GROUPS];
function groupLabel(group:string){return group==='Demographics & history'?'History':group==='Symptoms & examination'?'Symptoms':group==='Laboratory & echo'?'Labs & echo':group;}
function display(v:number|string,name:string){return v==='Fmale'?'Female':v==='Y'?'Yes':v==='N'?'No':typeof v==='number'&&['DM','HTN','Typical Chest Pain','Q Wave','St Elevation','St Depression','Tinversion','Current Smoker','EX-Smoker','FH','Edema'].includes(name)?v===1?'Yes':'No':String(v);}

export default function PatientPanel({schema,cases,features,caseId,onCase,onChange,onPredict,busy,onImport,collapsed,onToggle}:{schema:Feature[];cases:DemoCase[];features:Features;caseId:string|null;onCase:(id:string)=>void;onChange:(name:string,value:string|number)=>void;onPredict:()=>void;busy:boolean;onImport:(features:Features)=>void;collapsed:boolean;onToggle:()=>void}){
  const [tab,setTab]=useState('Key inputs');
  const [search,setSearch]=useState('');
  const [importError,setImportError]=useState('');
  const tabButtons=useRef<(HTMLButtonElement|null)[]>([]);
  const query=search.trim().toLowerCase();
  const visible=schema.filter(f=>query?`${f.name} ${f.label}`.toLowerCase().includes(query):tab==='Key inputs'?IMPORTANT.includes(f.name):f.group===tab)
    .sort((a,b)=>{
      const rank=(name:string)=>BODY_FIELDS.includes(name)?BODY_FIELDS.indexOf(name):BODY_FIELDS.length;
      return rank(a.name)-rank(b.name);
    });
  const current=cases.find(c=>c.id===caseId);
  return <section className={`patient-panel patient-profile-horizontal${collapsed?' is-collapsed':''}`} id="patient-inputs" tabIndex={-1} aria-label="Patient inputs">
    <div className="patient-profile-header">
    <div className="panel-title"><ClipboardList size={18}/><h2>Patient profile</h2></div>
    <div className="profile-edit-actions" hidden={collapsed}>
    <div className="case-picker"><label htmlFor="demo-case">Example(Optional)</label><div className="select-wrap"><select id="demo-case" value={caseId??''} onChange={e=>onCase(e.target.value)} disabled={busy}><option value="" disabled>Choose an example…</option>{cases.map(c=><option value={c.id} key={c.id} title={c.description}>{c.title}</option>)}</select><ChevronDown size={15}/></div></div>
    <div className="input-actions"><button type="button" disabled={busy} onClick={()=>onCase(caseId??'custom')}><RotateCcw size={13}/>Reset inputs</button><label className="import-button"><Upload size={13}/>Import JSON<input type="file" accept=".json,application/json" disabled={busy} onChange={async e=>{try{const file=e.target.files?.[0];if(!file)return;const j=JSON.parse(await file.text());onImport(j.features??j);setImportError('');}catch{setImportError('Choose a JSON object with the 55 source feature names.');}e.target.value='';}}/></label></div>
    </div>
    {collapsed&&<p className="profile-summary"><strong>{current?.title??'Custom profile'}</strong><span>{features.Age} years · {display(features.Sex,'Sex')}</span></p>}
    <button className="profile-toggle" type="button" aria-label={`${collapsed?'Expand':'Collapse'} patient profile`} aria-expanded={!collapsed} aria-controls="patient-profile-body" onClick={onToggle}>{collapsed?'Expand':'Collapse'}<ChevronDown size={16}/></button>
    </div>
    <div id="patient-profile-body" className="profile-body" inert={collapsed} aria-hidden={collapsed}>
    <div className="profile-body-content">
    <div className="patient-input-toolbar">
    <div className="input-tabs" role="tablist" aria-label="Clinical input groups">{INPUT_VIEWS.map((g,index)=><button key={g} ref={element=>{tabButtons.current[index]=element;}} id={`input-group-${index}`} type="button" role="tab" aria-label={groupLabel(g)} aria-controls="clinical-input-fields" aria-selected={!query&&tab===g} tabIndex={tab===g?0:-1} className={index===0?'input-shortcut':undefined} title={index===0?'Frequently used fields across all categories':g} onClick={()=>{setTab(g);setSearch('');}} onKeyDown={event=>{
      const next=event.key==='ArrowRight'?(index+1)%INPUT_VIEWS.length:event.key==='ArrowLeft'?(index+INPUT_VIEWS.length-1)%INPUT_VIEWS.length:event.key==='Home'?0:event.key==='End'?INPUT_VIEWS.length-1:null;
      if(next===null)return;event.preventDefault();setTab(INPUT_VIEWS[next]);setSearch('');tabButtons.current[next]?.focus();
    }}><span>{groupLabel(g)}</span><small aria-hidden="true">{schema.filter(f=>index===0?IMPORTANT.includes(f.name):f.group===g).length}</small></button>)}</div>
    <label className="search-input"><Search size={14}/><input aria-label="Search clinical inputs" placeholder="Find a measurement…" value={search} onChange={e=>setSearch(e.target.value)}/></label>
    </div>
    <p className="patient-input-scope">{tab==='Key inputs'&&!query?'Key inputs is a shortcut across all categories. ':''}All {schema.length} inputs are used in every prediction.</p>
    {importError&&<p role="alert" className="patient-import-error error-text">{importError}</p>}
    {query&&<div className="search-summary" role="status"><span>{visible.length} results · all input groups</span><button onClick={()=>setSearch('')}>Clear search</button></div>}
    <form onSubmit={e=>{e.preventDefault();onPredict();}} className="clinical-form">
      <div className="fields-scroll" id="clinical-input-fields" role={query?'region':'tabpanel'} aria-label={query?'Search results across all input groups':undefined} aria-labelledby={query?undefined:`input-group-${INPUT_VIEWS.indexOf(tab)}`}>{visible.map(f=>{
        const derived=f.name==='BMI';
        const value=features[f.name]??f.default;
        const unitId=f.unit?`input-unit-${f.name.replace(/\W/g,'-')}`:undefined;
        const description=[unitId,derived?'bmi-note':undefined].filter(Boolean).join(' ')||undefined;
        const note=derived?'Auto-calculated from height & weight':f.constant?'Constant in cohort':f.kind==='number'?`Cohort: ${f.min?.toFixed(f.integer?0:1)}–${f.max?.toFixed(f.integer?0:1)}`:f.name==='Region RWMA'?'Source category code; no spatial coordinates':'';
        return <label key={f.name} className={`clinical-field ${f.kind==='category'?'category-field':''}`}>
          <span>{f.label}</span>
          {query&&<span className="field-group">{f.group}</span>}
          <span className="clinical-control">
            {f.kind==='category'?<select value={String(value)} onChange={e=>{const next=f.options!.find(v=>String(v)===e.target.value)!;onChange(f.name,next);}} disabled={busy||f.constant} aria-label={f.label} aria-describedby={description}>{f.options?.map(v=><option key={String(v)} value={String(v)}>{display(v,f.name)}</option>)}</select>:
              <input type={derived?'text':'number'} readOnly={derived} required={!derived} step={f.integer?1:'any'} value={derived?(value===''?'':Number(value).toFixed(2)):value} onChange={derived?undefined:e=>onChange(f.name,e.target.value===''?'':Number(e.target.value))} disabled={busy} aria-label={f.label} aria-describedby={description}/>}
            {f.unit&&<span className="input-unit" id={unitId}>{f.unit}</span>}
          </span>
          {note&&<span className="observed-range" id={derived?'bmi-note':undefined}>{note}</span>}
        </label>;
      })}{!visible.length&&<p className="muted">No matching clinical inputs.</p>}
        <div className="input-footer"><button className="primary-button" type="submit" aria-busy={busy} disabled={busy||calculateBmi(features)===''}>{busy?<><span className="loader small" aria-hidden="true"/>Predicting…</>:<>Predict coronary risk<ArrowRight size={17}/></>}</button>{calculateBmi(features)===''&&<p className="input-validation" role="status">Enter a positive height and weight.</p>}</div>
      </div>
    </form>
    </div>
    </div>
  </section>;
}
