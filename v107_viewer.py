from pathlib import Path
import base64, json


def rigged_model_html(motion, safe_gpu=True):
    asset=Path(__file__).with_name('PhysioSentinel_Skeleton_Rigged_v1.glb')
    if not asset.exists():
        return "<div style='padding:20px;color:#ff8c8c'>Falta PhysioSentinel_Skeleton_Rigged_v1.glb en el despliegue.</div>"
    b64=base64.b64encode(asset.read_bytes()).decode('ascii')
    motion_json=json.dumps(motion,ensure_ascii=False,separators=(',',':'))
    safe_js='true' if safe_gpu else 'false'
    tpl=r'''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:#07111d;color:#dce8f5;font:13px system-ui;height:100%;overflow:hidden}.wrap{display:grid;grid-template-columns:360px 1fr;height:720px}.hud{padding:14px;background:#0a1420;border-right:1px solid #1d3347;overflow:auto}.view{position:relative;min-width:0}.view canvas{position:absolute;inset:0;width:100%;height:100%;display:block}.ok{color:#62e6a7;font-weight:800}.safe{color:#ffcf6e;font-weight:700}.stage{margin:6px 0;padding:6px 8px;border-radius:6px;background:#0c1b2a}.stage.ok2{color:#6ee7a8}.stage.err{color:#ff8c8c}.frame{font-weight:800;margin:8px 0}.controls{display:flex;flex-wrap:wrap;gap:6px;margin:9px 0}button{padding:7px 10px;border:0;border-radius:7px;cursor:pointer}button:disabled{opacity:.38}.active{outline:2px solid #63d9ff}.diag{white-space:pre-wrap;color:#9fc4e8;line-height:1.35}.warn{color:#ffca74;margin-top:10px}.dl{display:inline-block;padding:7px 10px;border-radius:7px;background:#dce8f5;color:#07111d;text-decoration:none;font-weight:700;margin-top:6px}input{width:100%}</style></head><body><div class="wrap"><div class="hud">
<div class="ok">V107.1 · ESQUELETO PRE-RIGGEADO · DELTA DE REPOSO</div><div class="safe">🛡️ GPU SAFE · nodos y pivotes definidos en el modelo</div>
<div id="rigStage" class="stage">Rig: iniciando…</div><div id="engineStage" class="stage">Three.js: pendiente</div><div id="loaderStage" class="stage">GLTFLoader: pendiente</div><div id="modelStage" class="stage">Modelo V107: pendiente</div><div id="nodesStage" class="stage">Nodos anatómicos: pendiente</div><div id="renderStage" class="stage">Primer render: pendiente</div>
<div class="frame" id="frame">Frame —</div><div class="controls"><button id="play">▶ Reproducir</button><button id="prev">−1</button><button id="next">+1</button><button id="reset">Reset</button><button id="fit">Reencuadrar</button><button id="record">⏺ Grabar ciclo</button></div>
<div class="controls"><button id="rig">Rig</button><button id="bones" disabled>Esqueleto</button><button id="both" disabled class="active">Rig + Esqueleto</button></div><div id="download"></div><input id="scrub" type="range" min="0" max="0" value="0"><div id="diag" class="diag">Preparando secuencia…</div><div class="warn">V107.1 aplica cada pose V104 como delta respecto al frame 0 sobre las matrices de reposo del GLB. El modelo conserva su jerarquía y proporciones; no hay acumulación entre frames.</div></div>
<div class="view"><canvas id="gl"></canvas></div></div>
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three'; import {OrbitControls} from 'three/addons/controls/OrbitControls.js'; import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
const SAFE=__SAFE__, motion=__MOTION__, F=motion.frames||[], MODEL_B64='__MODEL__'; const $=s=>document.querySelector(s); const canvas=$('#gl');
const setStage=(id,text,kind='')=>{const e=$(id);e.textContent=text;e.className='stage '+(kind==='ok'?'ok2':kind==='err'?'err':'')};
setStage('#rigStage','Rig: OK · '+F.length+' frames','ok'); setStage('#engineStage','Three.js: OK','ok'); setStage('#loaderStage','GLTFLoader + OrbitControls: OK','ok');
const renderer=new THREE.WebGLRenderer({canvas,antialias:false,powerPreference:'low-power',preserveDrawingBuffer:false}); renderer.setPixelRatio(SAFE?1:Math.min(devicePixelRatio,1.5)); renderer.setClearColor(0x07111d,1); renderer.outputColorSpace=THREE.SRGBColorSpace;
const scene=new THREE.Scene(); scene.background=new THREE.Color(0x07111d); const camera=new THREE.PerspectiveCamera(32,1,.01,100); const controls=new OrbitControls(camera,canvas); controls.enableDamping=false;
scene.add(new THREE.HemisphereLight(0xffffff,0x25364a,2.0)); const key=new THREE.DirectionalLight(0xffffff,2.2); key.position.set(3,5,5); scene.add(key); const grid=new THREE.GridHelper(4,16,0x2a4a67,0x173047); scene.add(grid);
const rigGroup=new THREE.Group(); scene.add(rigGroup); const rigMat=new THREE.LineBasicMaterial({color:0x00e5ff}); const ptMat=new THREE.PointsMaterial({color:0xffd166,size:.035,sizeAttenuation:true});
const modelJointGroup=new THREE.Group(); scene.add(modelJointGroup); const modelPtMat=new THREE.PointsMaterial({color:0xff4fd8,size:.045,sizeAttenuation:true});
const JOINTS=['Head','Neck','LShoulder','RShoulder','LElbow','RElbow','LWrist','RWrist','Hip','LHip','RHip','LKnee','RKnee','LAnkle','RAnkle','LHeel','RHeel','LBigToe','RBigToe'];
const LINKS=[['Neck','LShoulder'],['LShoulder','LElbow'],['LElbow','LWrist'],['Neck','RShoulder'],['RShoulder','RElbow'],['RElbow','RWrist'],['Neck','Hip'],['LHip','RHip'],['Hip','LHip'],['Hip','RHip'],['LHip','LKnee'],['LKnee','LAnkle'],['LAnkle','LBigToe'],['RHip','RKnee'],['RKnee','RAnkle'],['RAnkle','RBigToe']];
function rawP(f,n){const p=f?.joints?.[n]||f?.xyz?.[n]||f?.points?.[n]; if(!p)return null; const a=Array.isArray(p)?p:[p.x,p.y,p.z]; return a.length>=3&&a.every(Number.isFinite)?new THREE.Vector3(+a[0],+a[1],+a[2]):null}
function avg(...vs){const a=vs.filter(Boolean); if(!a.length)return null; return a.reduce((s,v)=>s.add(v),new THREE.Vector3()).multiplyScalar(1/a.length)}
const f0=F[0]||{}; const hip0=avg(rawP(f0,'LHip'),rawP(f0,'RHip'),rawP(f0,'Hip'))||new THREE.Vector3(); let ys=[]; for(const n of JOINTS){const p=rawP(f0,n);if(p)ys.push(p.y)} const bodyRange=Math.max(.5,(ys.length?(Math.max(...ys)-Math.min(...ys)):1)); const MAP_SCALE=2.65/bodyRange;
function MAPP(p){return p?p.clone().sub(hip0).multiplyScalar(MAP_SCALE):null} function P(f,n){return MAPP(rawP(f,n))}
let model=null,nodes={},restWorld={},restDesired=null,current=0,playing=false,last=0,mode='both',recorder=null,recording=false,chunks=[];const FRAME_MS=1000/24;
const required=['Pelvis','Spine','Thorax','Neck','Head','Femur_L','Tibia_L','Foot_L','Femur_R','Tibia_R','Foot_R','Humerus_L','Forearm_L','Hand_L','Humerus_R','Forearm_R','Hand_R'];
const AXIS_YN=new THREE.Vector3(0,-1,0),AXIS_YP=new THREE.Vector3(0,1,0),AXIS_ZP=new THREE.Vector3(0,0,1);
function basisMatrix(origin,xv,yv){const x=xv.clone().normalize(),y=yv.clone().normalize();let z=new THREE.Vector3().crossVectors(x,y);if(z.lengthSq()<1e-8)z.set(0,0,1);z.normalize();y.crossVectors(z,x).normalize();const M=new THREE.Matrix4().makeBasis(x,y,z);M.setPosition(origin);return M}
function segMatrix(a,b,axis){if(!a||!b)return new THREE.Matrix4();const d=b.clone().sub(a);if(d.lengthSq()<1e-10)d.set(0,1,0);const q=new THREE.Quaternion().setFromUnitVectors(axis,d.clone().normalize());return new THREE.Matrix4().compose(a,q,new THREE.Vector3(1,1,1))}
function desired(f){const LH=P(f,'LHip'),RH=P(f,'RHip'),H=P(f,'Hip')||avg(LH,RH),LS=P(f,'LShoulder'),RS=P(f,'RShoulder'),SM=avg(LS,RS),N=P(f,'Neck')||SM,HD=P(f,'Head')||P(f,'Nose')||N;const out={};const px=(LH&&RH)?RH.clone().sub(LH):new THREE.Vector3(1,0,0),py=(SM&&H)?SM.clone().sub(H):new THREE.Vector3(0,1,0);out.Pelvis=basisMatrix(H||new THREE.Vector3(),px,py);out.Spine=segMatrix(H,SM,AXIS_YP);const tx=(LS&&RS)?RS.clone().sub(LS):px,ty=(N&&SM)?N.clone().sub(SM):py;out.Thorax=basisMatrix(SM||H||new THREE.Vector3(),tx,ty);out.Neck=segMatrix(N,HD,AXIS_YP);out.Head=new THREE.Matrix4().makeTranslation(HD?.x||0,HD?.y||0,HD?.z||0);for(const side of['L','R']){out['Femur_'+side]=segMatrix(P(f,side+'Hip'),P(f,side+'Knee'),AXIS_YN);out['Tibia_'+side]=segMatrix(P(f,side+'Knee'),P(f,side+'Ankle'),AXIS_YN);out['Foot_'+side]=segMatrix(P(f,side+'Ankle'),P(f,side+'BigToe')||P(f,side+'Heel'),AXIS_ZP);out['Humerus_'+side]=segMatrix(P(f,side+'Shoulder'),P(f,side+'Elbow'),AXIS_YN);out['Forearm_'+side]=segMatrix(P(f,side+'Elbow'),P(f,side+'Wrist'),AXIS_YN);const w=P(f,side+'Wrist');out['Hand_'+side]=new THREE.Matrix4().makeTranslation(w?.x||0,w?.y||0,w?.z||0)}return out}
const parent={Pelvis:null,Spine:'Pelvis',Thorax:'Spine',Neck:'Thorax',Head:'Neck',Femur_L:'Pelvis',Tibia_L:'Femur_L',Foot_L:'Tibia_L',Femur_R:'Pelvis',Tibia_R:'Femur_R',Foot_R:'Tibia_R',Humerus_L:'Thorax',Forearm_L:'Humerus_L',Hand_L:'Forearm_L',Humerus_R:'Thorax',Forearm_R:'Humerus_R',Hand_R:'Forearm_R'};
function setWorld(name,M,parentName,worlds){const o=nodes[name];if(!o)return;let local=M.clone();if(parentName&&worlds[parentName])local=new THREE.Matrix4().copy(worlds[parentName]).invert().multiply(M);o.matrixAutoUpdate=false;o.matrix.copy(local);o.matrixWorldNeedsUpdate=true;worlds[name]=M.clone()}
function updateRig(f){while(rigGroup.children.length){const o=rigGroup.children.pop();o.geometry?.dispose?.()}const lp=[];for(const [a,b] of LINKS){const A=P(f,a),B=P(f,b);if(A&&B)lp.push(...A.toArray(),...B.toArray())}const lg=new THREE.BufferGeometry();lg.setAttribute('position',new THREE.Float32BufferAttribute(lp,3));rigGroup.add(new THREE.LineSegments(lg,rigMat));const pp=[];for(const n of JOINTS){const q=P(f,n);if(q)pp.push(...q.toArray())}const pg=new THREE.BufferGeometry();pg.setAttribute('position',new THREE.Float32BufferAttribute(pp,3));rigGroup.add(new THREE.Points(pg,ptMat))}
function updateModelJointDebug(){
  while(modelJointGroup.children.length){const o=modelJointGroup.children.pop();o.geometry?.dispose?.()}
  if(!model)return; const pp=[];
  for(const name of required){const o=nodes[name];if(!o)continue;const q=new THREE.Vector3();o.getWorldPosition(q);pp.push(...q.toArray())}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pp,3));modelJointGroup.add(new THREE.Points(g,modelPtMat));
}
function updateModel(f){
  if(!model||!restDesired)return;
  const d=desired(f);
  // Cada segmento usa: targetWorld = desired(t) * inv(desired(rest)) * modelRestWorld.
  // No se reutiliza la pose del frame anterior.
  for(const name of required){
    const o=nodes[name], Dt=d[name], D0=restDesired[name], R0=restWorld[name];
    if(!o||!Dt||!D0||!R0)continue;
    const delta=new THREE.Matrix4().copy(Dt).multiply(new THREE.Matrix4().copy(D0).invert());
    const targetWorld=new THREE.Matrix4().copy(delta).multiply(R0);
    let local=targetWorld.clone();
    const par=o.parent;
    if(par){par.updateMatrixWorld(true);local=new THREE.Matrix4().copy(par.matrixWorld).invert().multiply(targetWorld)}
    o.matrixAutoUpdate=false;o.matrix.copy(local);o.matrixWorldNeedsUpdate=true;o.updateMatrixWorld(true);
  }
  model.updateMatrixWorld(true);
  updateModelJointDebug();
}
function apply(n){if(!F.length)return;current=(n+F.length)%F.length;const f=F[current];updateRig(f);updateModel(f);$('#frame').textContent=(playing?'ANIMACIÓN ACTIVA':'DETENIDA')+' · Frame '+(current+1)+' / '+F.length;$('#scrub').value=current;render()}
function setMode(m){mode=m;$('#rig').classList.toggle('active',m==='rig');$('#bones').classList.toggle('active',m==='bones');$('#both').classList.toggle('active',m==='both');rigGroup.visible=m!=='bones';modelJointGroup.visible=m==='both';if(model)model.visible=m!=='rig';render()}
function resize(){const r=canvas.getBoundingClientRect(),w=Math.max(2,r.width|0),h=Math.max(2,r.height|0);if(canvas.width!==w||canvas.height!==h)renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()}
function fit(){const box=new THREE.Box3();if(rigGroup.visible)box.expandByObject(rigGroup);if(model?.visible)box.expandByObject(model);if(box.isEmpty())return;const sz=box.getSize(new THREE.Vector3()),cc=box.getCenter(new THREE.Vector3()),rad=Math.max(sz.x,sz.y,sz.z)/2||1,d=rad/Math.tan(THREE.MathUtils.degToRad(camera.fov)/2)*1.55;camera.position.set(cc.x,cc.y+sz.y*.02,cc.z+d);camera.near=Math.max(.01,d/1000);camera.far=Math.max(50,d*20);camera.updateProjectionMatrix();controls.target.copy(cc);controls.update();grid.position.y=cc.y-sz.y*.55;render()}
function render(){resize();renderer.render(scene,camera)}
async function loadModel(){try{setStage('#modelStage','Modelo V107: decodificando GLB local…');const bin=Uint8Array.from(atob(MODEL_B64),c=>c.charCodeAt(0));const url=URL.createObjectURL(new Blob([bin],{type:'model/gltf-binary'}));const gltf=await new GLTFLoader().loadAsync(url);URL.revokeObjectURL(url);model=gltf.scene;scene.add(model);model.traverse(o=>{if(o.isMesh){o.frustumCulled=false;const col=o.material?.color?.clone?.()||new THREE.Color(0xd8d0c0);o.material=new THREE.MeshLambertMaterial({color:col,side:THREE.DoubleSide})}});for(const n of required)nodes[n]=model.getObjectByName(n);const found=required.filter(n=>nodes[n]).length;setStage('#modelStage','Modelo V107.1: GLB local OK','ok');setStage('#nodesStage','Nodos anatómicos: '+found+' / '+required.length+(found===required.length?' OK':''),found===required.length?'ok':'err');if(found!==required.length)throw new Error('faltan nodos del modelo');model.updateMatrixWorld(true);restDesired=desired(F[0]||{});for(const n of required){if(nodes[n])restWorld[n]=nodes[n].matrixWorld.clone()}model.traverse(o=>{if(o.isMesh)o.material=new THREE.MeshLambertMaterial({color:0xe8e1d2,side:THREE.DoubleSide})});$('#bones').disabled=false;$('#both').disabled=false;apply(0);setMode('both');fit();setStage('#renderStage','Primer render WebGL: OK · retargeting delta-rest','ok');$('#diag').textContent='V107.1 GLB pre-riggeado\nFrames: '+F.length+'\nEscala V104→modelo: '+MAP_SCALE.toFixed(4)+'\nRetargeting: desired(t) × inverse(desired(rest)) × modelRestWorld\nPuntos magenta = orígenes articulares del modelo; cian = rig V104.'}catch(e){setStage('#modelStage','Modelo V107: ERROR · '+e.message,'err');$('#diag').textContent='ERROR V107: '+e.stack}}
$('#scrub').max=Math.max(0,F.length-1);$('#play').onclick=e=>{playing=!playing;e.target.textContent=playing?'⏸ Pausa':'▶ Reproducir'};$('#prev').onclick=()=>{playing=false;apply(current-1)};$('#next').onclick=()=>{playing=false;apply(current+1)};$('#reset').onclick=()=>{playing=false;apply(0)};$('#fit').onclick=fit;$('#rig').onclick=()=>setMode('rig');$('#bones').onclick=()=>setMode('bones');$('#both').onclick=()=>setMode('both');$('#scrub').oninput=e=>{playing=false;apply(+e.target.value)};
function mime(){for(const m of ['video/mp4;codecs=h264','video/mp4','video/webm;codecs=vp9','video/webm'])if(window.MediaRecorder&&MediaRecorder.isTypeSupported(m))return m;return ''}
$('#record').onclick=()=>{if(!canvas.captureStream||!window.MediaRecorder)return;const m=mime();try{recorder=new MediaRecorder(canvas.captureStream(24),m?{mimeType:m}:undefined)}catch(e){$('#diag').textContent+='\nGrabación ERROR: '+e;return}chunks=[];recording=true;$('#download').innerHTML='';recorder.ondataavailable=e=>{if(e.data?.size)chunks.push(e.data)};recorder.onstop=()=>{recording=false;const type=recorder.mimeType||m||'video/webm',ext=type.includes('mp4')?'mp4':'webm',blob=new Blob(chunks,{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.className='dl';a.href=url;a.download='PhysioSentinel_V107_1_'+mode+'.'+ext;a.textContent='⬇ Descargar vídeo '+mode+' ('+ext.toUpperCase()+')';$('#download').appendChild(a)};apply(0);recorder.start(250);playing=true};
function loop(t){if(playing&&t-last>FRAME_MS){last=t;const old=current;apply(current+1);if(recording&&old===F.length-1&&current===0){playing=false;try{recorder.stop()}catch(e){}}}requestAnimationFrame(loop)}
window.addEventListener('resize',render);window.addEventListener('error',e=>setStage('#renderStage','JavaScript ERROR · '+e.message,'err'));window.addEventListener('unhandledrejection',e=>setStage('#renderStage','Promise ERROR · '+String(e.reason),'err'));
setStage('#renderStage','WebGL inicializado','ok');apply(0);loadModel();requestAnimationFrame(loop);
</script></body></html>'''
    return tpl.replace('__SAFE__',safe_js).replace('__MOTION__',motion_json).replace('__MODEL__',b64)
