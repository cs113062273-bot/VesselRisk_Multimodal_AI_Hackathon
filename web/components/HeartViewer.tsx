'use client';
import { Suspense, useEffect, useMemo, useRef, useState, Component, type ReactNode } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { BufferAttribute, BufferGeometry, Color, DoubleSide, MeshBasicMaterial, MeshStandardMaterial, Vector3 } from 'three';
import { RotateCcw, Play, Pause, Layers, Focus, Maximize2, Minimize2, BookOpen, ChevronDown } from 'lucide-react';
import { NAMES, pct, Prediction, riskColor, Target, TARGETS, VESSELS, Vessel } from '@/lib/types';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import { ARTERY_GUIDE } from '@/lib/coronary-anatomy';
import InfoPopover from './InfoPopover';
import styles from './HeartViewer.module.css';

interface Part { id:string;name:string;target:Vessel|null;surface:string;positions:number;normals:number;indices:number;vertexCount:number;indexCount:number; }
interface Anatomy { parts:Part[];bytes:number;triangles:number;revision:string; }
interface Loaded { part:Part; geometry:BufferGeometry;center:[number,number,number]; }

class CanvasBoundary extends Component<{ children:ReactNode },{failed:boolean}> {
  state={failed:false};
  static getDerivedStateFromError(){return {failed:true};}
  render(){return this.state.failed?<div className="canvas-message">3D rendering is unavailable in this browser.<br/>Enable WebGL or use a modern browser. Vessel controls and evidence remain available.</div>:this.props.children;}
}

function AnatomyMesh({item,prediction,selected,xray,isolate,onSelect}:{item:Loaded;prediction:Prediction|null;selected:Vessel|null;xray:boolean;isolate:boolean;onSelect:(v:Vessel)=>void}){
  const vessel=item.part.target;
  const active=!!vessel&&(selected===null||vessel===selected);
  const p=vessel?prediction?.targets[vessel].probability:undefined;
  const targetColor=useMemo(()=>new Color(vessel?riskColor(p):item.part.surface==='great'?'#8096a3':selected?'#9e747b':'#b87b7c'),[vessel,p,item.part.surface,selected]);
  const [initialColor]=useState(()=>targetColor.clone());
  const material=useRef<MeshStandardMaterial>(null);
  const silhouette=useRef<MeshBasicMaterial>(null);
  const {invalidate}=useThree();
  const reducedMotion=useRef(false);
  useEffect(()=>{reducedMotion.current=window.matchMedia('(prefers-reduced-motion: reduce)').matches;invalidate();},[targetColor,active,xray,invalidate]);
  const targetOpacity=vessel?(active?1:.62):xray?.12:selected?.82:.91;
  const targetEmission=vessel?(selected===vessel?.85:active?.45:.12):0;
  useFrame((_,delta)=>{
    if(!material.current)return;
    const value=material.current;
    const factor=reducedMotion.current?1:1-Math.exp(-7*delta);
    value.color.lerp(targetColor,factor);
    if(vessel)value.emissive.lerp(targetColor,factor);
    value.opacity+=(targetOpacity-value.opacity)*factor;
    value.emissiveIntensity+=(targetEmission-value.emissiveIntensity)*factor;
    if(silhouette.current)silhouette.current.color.copy(value.color);
    const colorError=Math.abs(value.color.r-targetColor.r)+Math.abs(value.color.g-targetColor.g)+Math.abs(value.color.b-targetColor.b);
    if(colorError>.001||Math.abs(value.opacity-targetOpacity)>.001||Math.abs(value.emissiveIntensity-targetEmission)>.001)invalidate();
  });
  if(isolate && !vessel)return null;
  return <>
    {vessel===selected&&!isolate&&<mesh geometry={item.geometry} renderOrder={1} raycast={()=>null}>
      <meshBasicMaterial ref={silhouette} color={targetColor} side={DoubleSide} transparent opacity={.16} depthTest={false} depthWrite={false}/>
    </mesh>}
    <mesh geometry={item.geometry} onClick={vessel?(e)=>{e.stopPropagation();onSelect(vessel);}:undefined}
    onPointerOver={vessel?(e)=>{e.stopPropagation();document.body.style.cursor='pointer';}:undefined}
    onPointerOut={vessel?()=>{document.body.style.cursor='auto';}:undefined} renderOrder={vessel?2:0}>
    <meshStandardMaterial ref={material} color={initialColor} emissive={vessel?initialColor:'#000000'} emissiveIntensity={vessel?.45:0} side={DoubleSide}
      roughness={vessel?.32:.57} metalness={vessel?.22:.1}
      transparent
      depthWrite={!!vessel||!xray}/>
    </mesh>
  </>;
}

const CAMERA_DISTANCE=8.4;
const VIEW_DIRECTIONS:Record<Target,[number,number,number]>={CAD:[0,.05,1],LAD:[.45,.1,1],LCX:[1,.15,-.8],RCA:[-1,.12,.8]};
function CameraGuide({selected,focusVersion,spin}:{selected:Target;focusVersion:number;spin:boolean}){
  const {camera,invalidate}=useThree();
  const controls=useRef<OrbitControlsImpl>(null);
  const destination=useRef<{position:Vector3;target:Vector3}|null>(null);
  useEffect(()=>{
    if(!focusVersion)return;
    const target=new Vector3(0,.1,0);
    const position=new Vector3(...VIEW_DIRECTIONS[selected]).normalize().multiplyScalar(CAMERA_DISTANCE).add(target);
    if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){
      camera.position.copy(position);controls.current?.target.copy(target);controls.current?.update();
    }else destination.current={position,target};
    invalidate();
  },[camera,invalidate,selected,focusVersion]);
  useEffect(()=>{
    if(spin){destination.current=null;invalidate();}
  },[spin,invalidate]);
  useFrame((_,delta)=>{
    if(spin){invalidate();return;}
    if(!destination.current||!controls.current)return;
    const {position,target}=destination.current;
    const factor=1-Math.exp(-6*delta);
    camera.position.lerp(position,factor);controls.current.target.lerp(target,factor);controls.current.update();
    if(camera.position.distanceTo(position)<.005){camera.position.copy(position);controls.current.target.copy(target);controls.current.update();destination.current=null;}
    else invalidate();
  });
  return <OrbitControls ref={controls} makeDefault enablePan autoRotate={spin} autoRotateSpeed={.6} minDistance={3.6} maxDistance={14} target={[0,.1,0]} enableDamping dampingFactor={.08} onStart={()=>{destination.current=null;}}/>;
}

function moveLabel(el:HTMLButtonElement,x:number,y:number,visible:boolean){
  el.style.transform=`translate3d(${x}px,${y}px,0)`;
  el.style.visibility=visible?'visible':'hidden';
}

function VesselAnchors({items,labels,connectors,selected,layoutVersion}:{items:Loaded[];labels:React.RefObject<Partial<Record<Vessel,HTMLButtonElement|null>>>;connectors:React.RefObject<Partial<Record<Vessel,SVGGElement|null>>>;selected:Vessel|null;layoutVersion:string}){
  const {invalidate}=useThree();
  useEffect(()=>{invalidate();},[layoutVersion,selected,invalidate]);
  const point=useMemo(()=>new Vector3(),[]);
  const anchors=useMemo(()=>items.map(item=>{
    const positions=item.geometry.getAttribute('position');
    const samples:Vector3[]=[];
    for(let i=0;i<positions.count;i+=Math.max(1,Math.ceil(positions.count/180))){
      samples.push(new Vector3(positions.getX(i),positions.getY(i)-.25,positions.getZ(i)));
    }
    return {vessel:item.part.target!,samples};
  }),[items]);
  useFrame(({camera,size})=>{
    const occupied:{x:number;y:number;width:number;height:number}[]=[];
    const ordered=[...anchors].sort((a,b)=>Number(b.vessel===selected)-Number(a.vessel===selected));
    for(const {vessel,samples} of ordered){
      const el=labels.current[vessel];if(!el)continue;
      // Anchor to a real vertex on the near side of this artery's trunk.
      // A bounding-box center can lie inside the heart, away from the vessel.
      let nearest=samples[0],distance=Infinity;
      for(const sample of samples){const next=sample.distanceToSquared(camera.position);if(next<distance){nearest=sample;distance=next;}}
      point.copy(nearest).project(camera);
      const x=(point.x*.5+.5)*size.width,y=(-point.y*.5+.5)*size.height;
      const width=el.offsetWidth,height=el.offsetHeight;
      const candidates=[];
      // Place the selected label first, then fit the remaining labels around it.
      // Every connector still terminates on a real vessel vertex.
      for(const side of (vessel==='RCA'?[-1,1]:[1,-1]))for(const shift of [0,-1,1,-2,2]){
        const cx=Math.max(8,Math.min(size.width-width-8,x+(side<0?-width-28:28)));
        const cy=Math.max(38,Math.min(size.height-height-8,y-height/2+shift*(height+10)));
        const overlap=occupied.reduce((sum,box)=>sum+Math.max(0,Math.min(cx+width+8,box.x+box.width)-Math.max(cx-8,box.x))*Math.max(0,Math.min(cy+height+8,box.y+box.height)-Math.max(cy-8,box.y)),0);
        const edgeDistance=Math.abs(Math.max(cx,Math.min(cx+width,x))-x);
        const preferred=vessel==='RCA'?-1:1;
        candidates.push({x:cx,y:cy,cost:overlap*100+Math.abs(shift)*30+edgeDistance+(side===preferred?0:12)});
      }
      candidates.sort((a,b)=>a.cost-b.cost);
      const {x:labelX,y:labelY}=candidates[0];
      const visible=point.z>-1&&point.z<1&&x>=0&&x<=size.width&&y>=0&&y<=size.height;
      moveLabel(el,labelX,labelY,visible);
      if(visible)occupied.push({x:labelX,y:labelY,width,height});
      const group=connectors.current[vessel];
      if(group){
        group.style.setProperty('visibility',visible?'visible':'hidden');
        const line=group.children[0],circle=group.children[1];
        line.setAttribute('x1',String(x));line.setAttribute('y1',String(y));
        line.setAttribute('x2',String(Math.max(labelX,Math.min(labelX+width,x))));line.setAttribute('y2',String(labelY+height/2));
        circle.setAttribute('cx',String(x));circle.setAttribute('cy',String(y));
      }
    }
  });
  return null;
}

export default function HeartViewer({prediction,previousPrediction,predictionUpdatedAt,target,focusVersion,dirty,initialOrbit,onOpened,onSelect}:{prediction:Prediction|null;previousPrediction:Prediction|null;predictionUpdatedAt:number;target:Target;focusVersion:number;dirty:boolean;initialOrbit:boolean;onOpened:()=>void;onSelect:(v:Target)=>void}){
  const [loaded,setLoaded]=useState<Loaded[]>([]);
  const [error,setError]=useState('');
  const [spin,setSpin]=useState(initialOrbit);
  useEffect(()=>{onOpened();},[onOpened]);
  const [spinVersion,setSpinVersion]=useState(0);
  const [xray,setXray]=useState(false);
  const [isolate,setIsolate]=useState(false);
  const [reset,setReset]=useState(0);
  const [full,setFull]=useState(false);
  const [resetVersion,setResetVersion]=useState(0);
  const [clock,setClock]=useState(()=>Date.now());
  useEffect(()=>{
    const timer=window.setTimeout(()=>setClock(Date.now()),Math.max(0,predictionUpdatedAt+6500-Date.now()));
    return ()=>window.clearTimeout(timer);
  },[predictionUpdatedAt]);
  const showChanges=!!previousPrediction&&!dirty&&predictionUpdatedAt+6500>clock;
  const labels=useRef<Partial<Record<Vessel,HTMLButtonElement|null>>>({});
  const connectors=useRef<Partial<Record<Vessel,SVGGElement|null>>>({});
  useEffect(()=>{
    let live=true;
    Promise.all([fetch('/anatomy/manifest.json').then(r=>{if(!r.ok)throw new Error('Anatomy manifest could not load');return r.json() as Promise<Anatomy>;}),fetch('/anatomy/heart.bin').then(r=>{if(!r.ok)throw new Error('Anatomy geometry could not load');return r.arrayBuffer();})]).then(([manifest,buffer])=>{
      if(buffer.byteLength!==manifest.bytes)throw new Error('Anatomy integrity check failed');
      const result=manifest.parts.map(part=>{
        const geometry=new BufferGeometry();
        geometry.setAttribute('position',new BufferAttribute(new Float32Array(buffer,part.positions,part.vertexCount*3),3));
        geometry.setAttribute('normal',new BufferAttribute(new Float32Array(buffer,part.normals,part.vertexCount*3),3));
        geometry.setIndex(new BufferAttribute(new Uint32Array(buffer,part.indices,part.indexCount),1));
        geometry.computeBoundingBox();geometry.computeBoundingSphere();
        const box=geometry.boundingBox!;
        const center:[number,number,number]=[(box.min.x+box.max.x)/2,(box.min.y+box.max.y)/2,(box.min.z+box.max.z)/2];
        return {part,geometry,center};
      });
      if(live)setLoaded(result);else result.forEach(x=>x.geometry.dispose());
    }).catch(e=>{if(live)setError(e.message);});
    return ()=>{live=false;};
  },[]);
  useEffect(()=>()=>{loaded.forEach(x=>x.geometry.dispose());document.body.style.cursor='auto';},[loaded]);
  useEffect(()=>{if(!full)return;const handler=(e:KeyboardEvent)=>{if(e.key==='Escape')setFull(false);};window.addEventListener('keydown',handler);return ()=>window.removeEventListener('keydown',handler);},[full]);
  const labelParts=useMemo(()=>loaded.filter(x=>['FJ2631','FJ2649','FJ2723'].includes(x.part.id)),[loaded]);
  const choose=(v:Target)=>{setSpin(false);onSelect(v);};
  const rotating=spin&&spinVersion===focusVersion;
  const selected=target==='CAD'?null:target;
  const activeRisk=prediction?.targets[target];
  const guide=selected?ARTERY_GUIDE[selected]:null;
  return <section className={`heart-viewer ${full?'viewer-full':''}`} aria-label="Interactive coronary anatomy">
    <div className="viewer-heading">
      <div className="viewer-title"><select className="viewer-target-select" aria-label="View prediction target" value={target} onChange={e=>choose(e.target.value as Target)}>{TARGETS.map(t=><option key={t} value={t}>{t==='CAD'?'Overall CAD':`${t} · ${NAMES[t]}`}</option>)}</select><ChevronDown size={16} aria-hidden="true"/></div>
      {full&&<div className="selected-vessel-summary" aria-live="polite"><strong style={{color:riskColor(activeRisk?.probability)}}>{activeRisk?`${(activeRisk.probability*100).toFixed(1)}%`:'—'}</strong><span>{dirty&&prediction?'Previous estimate':target==='CAD'?'CAD probability':'Stenosis probability'}</span></div>}
      <div className="viewer-toolbar-actions">
        {guide&&<InfoPopover key={selected} label="Artery information" title={`${selected} anatomy`} buttonClassName="viewer-tool" trigger={<><BookOpen size={16}/><span>Artery info</span></>}>
          <div className="artery-guide" aria-label={`${selected} reference anatomy`}>
            <dl><div><dt>Course</dt><dd>{guide.course}</dd></div><div><dt>Usually supplies</dt><dd>{guide.supply}</dd></div></dl>
            <a href={guide.source} target="_blank" rel="noreferrer">General anatomy · individual territories vary ↗</a>
          </div>
        </InfoPopover>}
        <button className="icon-button on-dark" onClick={()=>setFull(!full)} aria-label={full?'Exit expanded anatomy':'Expand anatomy'} title={full?'Exit expanded anatomy':'Expand anatomy'}>{full?<Minimize2 size={17}/>:<Maximize2 size={17}/>}</button>
      </div>
    </div>
    <div className="anatomy-canvas" role="img" aria-label={`3D heart with selectable LAD, LCX and RCA. ${selected?`${selected} selected`:'Overall CAD overview'}.`}>
      {error?<div className="canvas-message">{error}<button onClick={()=>window.location.reload()}>Reload anatomy</button></div>:!loaded.length?<div className="canvas-message"><span className="loader"/>Preparing coronary anatomy…</div>:<CanvasBoundary><Canvas key={reset} frameloop="demand" style={{position:'absolute',inset:0}} camera={{position:[0,.35,CAMERA_DISTANCE],fov:35}} dpr={[1,1.5]} gl={{antialias:true,alpha:true,powerPreference:'low-power'}}>
        <ambientLight intensity={.55}/><hemisphereLight args={['#d1edfa','#29303d',1.1]}/>
        <directionalLight position={[3,5,5]} intensity={3.1} color="#ffe4d9"/>
        <directionalLight position={[-4,0,2]} intensity={1.5} color="#88cfec"/>
        <directionalLight position={[2,3,-4]} intensity={2.6} color="#77ded1"/>
        <Suspense fallback={null}>
          <group position={[0,-.25,0]}>{loaded.map(item=><AnatomyMesh key={item.part.id} {...{item,prediction,selected,xray,isolate}} onSelect={choose}/>)}</group>
          <VesselAnchors items={labelParts} {...{labels,connectors,selected}} layoutVersion={`${predictionUpdatedAt}-${showChanges}-${dirty}`}/>
          <CameraGuide selected={target} focusVersion={focusVersion>resetVersion?focusVersion:0} spin={rotating}/>
        </Suspense>
      </Canvas></CanvasBoundary>}
      <svg className="vessel-connectors" aria-hidden="true">{VESSELS.map(v=><g key={v} ref={el=>{connectors.current[v]=el;}} className={selected===v?'active':''}><line/><circle r="3"/></g>)}</svg>
      {labelParts.map(({part})=>{
        const vessel=part.target!;
        const probability=prediction?.targets[vessel].probability;
        const change=prediction&&previousPrediction?(probability!-previousPrediction.targets[vessel].probability)*100:null;
        const changing=showChanges&&change!==null&&Math.abs(change)>=.05;
        return <button key={part.id} ref={el=>{labels.current[vessel]=el;}} className={`artery-label projected-label ${styles.label} ${selected===vessel?'selected':''}`} onClick={()=>choose(vessel)} aria-pressed={selected===vessel} aria-label={`Select ${vessel} in 3D`} aria-describedby={`artery-probability-${vessel}`} title={`${NAMES[vessel]} · ${probability===undefined?'No prediction yet':`${dirty?'Previous prediction':'Estimated stenosis probability'}: ${pct(probability)}`}`}>
          <span className={styles.labelValue}><i style={{background:riskColor(probability)}}/><strong>{vessel}</strong><span id={`artery-probability-${vessel}`} className={styles.probability}>{probability===undefined?'—':pct(probability)}</span></span>
          {changing&&<span key={predictionUpdatedAt} className={styles.change} data-change-pp={change!.toFixed(1)} title="Compared with the previous prediction">{change!>0?'+':'−'}{Math.abs(change!).toFixed(1)} pp <small>vs last</small></span>}
        </button>;
      })}
      <div className="view-caption">Drag to rotate · Scroll to zoom · Click a vessel</div>
    </div>
    <div className="viewer-controls"><button onClick={()=>{setSpin(!rotating);setSpinVersion(focusVersion);}} aria-pressed={rotating}>{rotating?<Pause size={15}/>:<Play size={15}/>}<span>{rotating?'Pause':'Orbit'}</span></button><button onClick={()=>setXray(!xray)} aria-pressed={xray}><Layers size={15}/><span>X-ray</span></button><button onClick={()=>setIsolate(!isolate)} aria-pressed={isolate}><Focus size={15}/><span>Vessels only</span></button><button onClick={()=>{setReset(v=>v+1);setSpin(false);setResetVersion(focusVersion);}}><RotateCcw size={15}/><span>Reset</span></button></div>
    <div className="color-key" aria-label="Probability display bands, not clinical risk categories"><span>Probability</span><span><i style={{background:riskColor(0)}}/>&lt;30%</span><span><i style={{background:riskColor(.3)}}/>30–&lt;60%</span><span><i style={{background:riskColor(.6)}}/>≥60%</span></div>
    <p className="anatomy-note">Reference anatomy · Color shows probability, not blockage severity</p>
    <a className="anatomy-credit" href="https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html" target="_blank" rel="noreferrer">BodyParts3D / DBCLS · CC BY 4.0</a>
  </section>;
}
