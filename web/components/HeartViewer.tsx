'use client';
import { Suspense, useEffect, useMemo, useRef, useState, Component, type ReactNode } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { BufferAttribute, BufferGeometry, Color, DoubleSide, MeshStandardMaterial, Vector3 } from 'three';
import { RotateCcw, Play, Pause, Layers, Focus, Maximize2, Minimize2, MousePointer2 } from 'lucide-react';
import { NAMES, Prediction, riskColor, VESSELS, Vessel } from '@/lib/types';

interface Part { id:string;name:string;target:Vessel|null;surface:string;positions:number;normals:number;indices:number;vertexCount:number;indexCount:number; }
interface Anatomy { parts:Part[];bytes:number;triangles:number;revision:string; }
interface Loaded { part:Part; geometry:BufferGeometry;center:[number,number,number]; }

class CanvasBoundary extends Component<{ children:ReactNode },{failed:boolean}> {
  state={failed:false};
  static getDerivedStateFromError(){return {failed:true};}
  render(){return this.state.failed?<div className="canvas-message">3D rendering is unavailable in this browser.<br/>Enable WebGL or use a modern browser. Vessel controls and evidence remain available.</div>:this.props.children;}
}

function AnatomyMesh({item,prediction,selected,xray,isolate,onSelect}:{item:Loaded;prediction:Prediction|null;selected:Vessel;xray:boolean;isolate:boolean;onSelect:(v:Vessel)=>void}){
  const material = useRef<MeshStandardMaterial>(null);
  const vessel=item.part.target;
  const active=vessel===selected;
  const p=vessel?prediction?.targets[vessel].probability:undefined;
  const targetColor=useMemo(()=>new Color(vessel?riskColor(p):item.part.surface==='great'?'#8096a3':'#b87b7c'),[vessel,p,item.part.surface]);
  useFrame(()=>{material.current?.color.lerp(targetColor,.12);});
  if(isolate && !vessel)return null;
  return <mesh geometry={item.geometry} onClick={vessel?(e)=>{e.stopPropagation();onSelect(vessel);}:undefined}
    onPointerOver={vessel?(e)=>{e.stopPropagation();document.body.style.cursor='pointer';}:undefined}
    onPointerOut={vessel?()=>{document.body.style.cursor='auto';}:undefined} renderOrder={vessel?2:0}>
    <meshStandardMaterial ref={material} color={targetColor} side={DoubleSide}
      roughness={vessel?.32:.57} metalness={vessel?.22:.1}
      emissive={vessel?riskColor(p):'#000000'} emissiveIntensity={vessel?(active?.3:.1):0}
      transparent={!vessel||!active} opacity={vessel?(active?1:.77):xray?.12:.91}
      depthWrite={!!vessel||!xray}/>
  </mesh>;
}

function Performance({onFps}:{onFps:(v:number)=>void}){
  const clock=useRef({frames:0,last:0});
  useFrame(({clock:c})=>{const t=c.elapsedTime;clock.current.frames++; if(t-clock.current.last>2){onFps(Math.round(clock.current.frames/(t-clock.current.last)));clock.current={frames:0,last:t};}});
  return null;
}

function moveLabel(el:HTMLButtonElement,x:number,y:number,visible:boolean){
  el.style.transform=`translate3d(${x}px,${y}px,0)`;
  el.style.visibility=visible?'visible':'hidden';
}

function VesselAnchors({items,labels}:{items:Loaded[];labels:React.RefObject<Partial<Record<Vessel,HTMLButtonElement|null>>>}){
  const point=useMemo(()=>new Vector3(),[]);
  useFrame(({camera,size})=>{
    for(const item of items){
      const el=labels.current[item.part.target!];if(!el)continue;
      point.set(item.center[0],item.center[1]-.25,item.center[2]).project(camera);
      const x=(point.x*.5+.5)*size.width,y=(-point.y*.5+.5)*size.height;
      // Project the actual mesh centroid; offset the label to keep vessels visible.
      const offset=item.part.target==='RCA'?-75:item.part.target==='LAD'?25:30;
      moveLabel(el,x+offset,y,point.z<1);
    }
  });
  return null;
}

export default function HeartViewer({prediction,selected,onSelect}:{prediction:Prediction|null;selected:Vessel;onSelect:(v:Vessel)=>void}){
  const [loaded,setLoaded]=useState<Loaded[]>([]);
  const [error,setError]=useState('');
  const [spin,setSpin]=useState(false);
  const [xray,setXray]=useState(false);
  const [isolate,setIsolate]=useState(false);
  const [reset,setReset]=useState(0);
  const [full,setFull]=useState(false);
  const [fps,setFps]=useState<number|null>(null);
  const labels=useRef<Partial<Record<Vessel,HTMLButtonElement|null>>>({});
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
  const labelParts=loaded.filter(x=>['FJ2631','FJ2649','FJ2723'].includes(x.part.id));
  return <section className={`heart-viewer ${full?'viewer-full':''}`} aria-label="Interactive coronary anatomy">
    <div className="viewer-heading"><div><span className="eyebrow light">CORONARY ANATOMY</span><h2>Risk, in perspective.</h2></div><button className="icon-button on-dark" onClick={()=>setFull(!full)} aria-label={full?'Exit expanded anatomy':'Expand anatomy'}>{full?<Minimize2 size={17}/>:<Maximize2 size={17}/>}</button></div>
    <div className="viewer-topline"><span><i className="live-dot"/> {loaded.length?'63 anatomical structures':'Loading anatomical structures'}</span><span>{fps?`${fps} FPS · live`:'WebGL · interactive'}</span></div>
    <div className="anatomy-canvas" role="img" aria-label={`3D heart with selectable LAD, LCX and RCA. ${selected} selected.`}>
      {error?<div className="canvas-message">{error}<button onClick={()=>window.location.reload()}>Reload anatomy</button></div>:!loaded.length?<div className="canvas-message"><span className="loader"/>Preparing coronary anatomy…</div>:<CanvasBoundary><Canvas key={reset} style={{position:'absolute',inset:0}} camera={{position:[0,.35,7.3],fov:35}} dpr={[1,1.5]} gl={{antialias:true,alpha:true,powerPreference:'low-power'}}>
        <ambientLight intensity={.55}/><hemisphereLight args={['#d1edfa','#29303d',1.1]}/>
        <directionalLight position={[3,5,5]} intensity={3.1} color="#ffe4d9"/>
        <directionalLight position={[-4,0,2]} intensity={1.5} color="#88cfec"/>
        <directionalLight position={[2,3,-4]} intensity={2.6} color="#77ded1"/>
        <Suspense fallback={null}>
          <group position={[0,-.25,0]}>{loaded.map(item=><AnatomyMesh key={item.part.id} {...{item,prediction,selected,xray,isolate,onSelect}}/>)}</group>
          <VesselAnchors items={labelParts} labels={labels}/>
          <OrbitControls makeDefault enablePan autoRotate={spin} autoRotateSpeed={.6} minDistance={3.6} maxDistance={14} target={[0,.1,0]} enableDamping dampingFactor={.08}/>
        </Suspense><Performance onFps={setFps}/>
      </Canvas></CanvasBoundary>}
      {labelParts.map(({part})=><button key={part.id} ref={el=>{labels.current[part.target!]=el;}} className={`artery-label projected-label ${selected===part.target?'selected':''}`} onClick={()=>onSelect(part.target!)} aria-pressed={selected===part.target} aria-label={`Select ${part.target} in 3D`}><i style={{background:riskColor(prediction?.targets[part.target!].probability)}}/>{part.target}</button>)}
      <div className="orientation"><span>RESET VIEW</span><div><i>ANTERIOR</i></div></div>
    </div>
    <div className="viewer-hint"><MousePointer2 size={13}/> Drag to rotate · Scroll to zoom · Click a vessel</div>
    <div className="viewer-controls"><button onClick={()=>setSpin(!spin)} aria-pressed={spin}>{spin?<Pause size={15}/>:<Play size={15}/>}<span>{spin?'Pause':'Orbit'}</span></button><button onClick={()=>setXray(!xray)} aria-pressed={xray}><Layers size={15}/><span>X-ray</span></button><button onClick={()=>setIsolate(!isolate)} aria-pressed={isolate}><Focus size={15}/><span>Vessels only</span></button><button onClick={()=>{setReset(v=>v+1);setSpin(false);}}><RotateCcw size={15}/><span>Reset</span></button></div>
    <div className="vessel-selector">{VESSELS.map(v=><button key={v} className={selected===v?'active':''} onClick={()=>onSelect(v)} aria-pressed={selected===v}><i style={{background:riskColor(prediction?.targets[v].probability)}}/><span><strong>{v}</strong><small>{NAMES[v]}</small></span><b>{prediction?`${Math.round(prediction.targets[v].probability*100)}%`:'—'}</b></button>)}</div>
    <div className="color-key" aria-label="Probability display bands, not clinical risk categories"><span>Probability</span><span><i style={{background:riskColor(0)}}/>&lt;30%</span><span><i style={{background:riskColor(.3)}}/>30–&lt;60%</span><span><i style={{background:riskColor(.6)}}/>≥60%</span></div>
    <p className="anatomy-note">Reference anatomy · Vessel-level estimates · No lesion localization</p>
    <a className="anatomy-credit" href="https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html" target="_blank" rel="noreferrer">BodyParts3D / DBCLS · CC BY 4.0</a>
  </section>;
}
