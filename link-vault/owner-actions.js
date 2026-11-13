/* CF-LINK-VAULT-001: local-only action checks, public-safe project view. */
(() => {
"use strict";
const get=id=>document.getElementById(id);
const BASE="https://github.com/whoiwts110217-creator/CF-0/blob/main/";
const CHECKS="cf_link_vault_owner_action_checks_v1",CACHE="cf_link_vault_owner_action_cache_v1";
const zones={now:"Do now",soon:"Deadline",ready:"Ready to test",conditional:"Only if needed",optional:"Optional",waiting:"Watching / hold",assistant:"Assistant work"};
const views={mine:["now","soon","ready"],later:["conditional","optional"],waiting:["waiting"],assistant:["assistant"],all:Object.keys(zones),done:[]};
const urlOK=value=>{try{const u=new URL(value);return u.protocol==="https:"&&!u.username&&!u.password}catch(_){return false}};
let catalog=[],revision="not loaded",view="mine",checks={},graph=null,registry=null,privateActions=[],query="",catalogDate="unknown";
try{const saved=JSON.parse(localStorage.getItem(CHECKS)||"{}");if(saved&&typeof saved==="object"&&!Array.isArray(saved))checks=Object.fromEntries(Object.entries(saved).filter(([k,v])=>/^CF-ACT-\d{3}$/.test(k)&&typeof v==="string"&&v.length<50))}catch(_){}
const html=[
'<section class="oa-shell" id="owner-actions" aria-labelledby="oa-title">',
'<div class="oa-head"><div><span class="oa-kicker">CAVEMAN FOCUS · ONE CONNECTED COCKPIT</span><h2 id="oa-title">Your action sphere</h2><p>Tap the sphere to choose a path. The side rail shows your actions and their exact doorways. Your searchable link vault continues below.</p></div><span class="oa-live">PUBLIC-SAFE · PERSONAL CHECKMARKS</span></div>',
'<div class="oa-layout"><div class="oa-system"><div class="oa-sphere" role="group" aria-label="Action map">',
'<div class="oa-equator" aria-hidden="true"></div><div class="oa-core" aria-hidden="true">CF</div>',
'<button type="button" class="oa-node" data-view="mine" aria-pressed="true">⚡ My turn<small>Priority actions</small></button>',
'<button type="button" class="oa-node" data-view="later" aria-pressed="false">◇ Later<small>Optional / gated</small></button>',
'<button type="button" class="oa-node" data-view="waiting" aria-pressed="false">◷ Waiting<small>Holds / replies</small></button>',
'<button type="button" class="oa-node" data-view="assistant" aria-pressed="false">⚙ AI work<small>Not your chore</small></button>',
'<button type="button" class="oa-node" data-view="all" aria-pressed="false">⌖ All paths<small>Whole picture</small></button>',
'</div><p class="oa-legend">Interactive navigation, not a remote-control switch. Neither HP execution nor account access is implied.</p></div>',
'<aside class="oa-rail" aria-label="Consolidated action side list"><div class="oa-rail-top"><h3>Side list · action rail</h3><span id="oa-count" class="oa-count">Loading…</span></div><div class="oa-tabs" role="tablist" aria-label="Action lanes">',
'<button type="button" id="oa-tab-mine" class="oa-tab" role="tab" aria-selected="true" aria-controls="oa-items" tabindex="0" data-view="mine">My turn</button><button type="button" id="oa-tab-later" class="oa-tab" role="tab" aria-selected="false" aria-controls="oa-items" tabindex="-1" data-view="later">Later</button><button type="button" id="oa-tab-waiting" class="oa-tab" role="tab" aria-selected="false" aria-controls="oa-items" tabindex="-1" data-view="waiting">Waiting</button><button type="button" id="oa-tab-assistant" class="oa-tab" role="tab" aria-selected="false" aria-controls="oa-items" tabindex="-1" data-view="assistant">AI work</button><button type="button" id="oa-tab-all" class="oa-tab" role="tab" aria-selected="false" aria-controls="oa-items" tabindex="-1" data-view="all">All</button><button type="button" id="oa-tab-done" class="oa-tab" role="tab" aria-selected="false" aria-controls="oa-items" tabindex="-1" data-view="done">Checked locally</button>',
'</div><label class="oa-search-label" for="oa-search">Find an action or project</label><input id="oa-search" type="search" class="oa-search" placeholder="Search action, source, project ID" autocomplete="off"><div id="oa-items" class="oa-items" role="tabpanel" tabindex="0" aria-labelledby="oa-tab-mine" aria-live="polite"><p class="oa-empty">Loading public action view…</p></div></aside></div>',
'<div class="oa-tools"><button type="button" id="oa-refresh" class="btn primary">↻ Refresh action view</button><button type="button" id="oa-cf200" class="btn">↻ Check CF-200 source</button><span id="oa-cf200-status" class="oa-status" role="status">CF-200 not checked</span><button type="button" id="oa-export" class="btn">↓ Backup my checks</button><label class="oa-small oa-import">Import private action manifest <input id="oa-import" type="file" accept="application/json,.json" aria-label="Import a local private action manifest JSON"></label><button type="button" id="oa-clear-private" class="btn" disabled>Clear private import</button><a class="oa-small" target="_blank" rel="noopener noreferrer" href="https://github.com/whoiwts110217-creator/CF-0/blob/main/link-vault/spider-hp/README.md">HP Walker · $0 local tool ↗</a><a class="oa-small" target="_blank" rel="noopener noreferrer" href="https://github.com/whoiwts110217-creator/CF-0/blob/main/docs/OWNER_JUNGLE_MAP.md">Full project map ↗</a><a class="oa-small" target="_blank" rel="noopener noreferrer" href="https://github.com/whoiwts110217-creator/CF-0/blob/main/docs/CURRENT_SOURCE_GATEWAY.md">Check current source ↗</a><span id="oa-status" class="oa-status" role="status">Not checked yet</span></div>',
'<p class="oa-note">Dated public-safe overlay, not a second task registry, automatic scan of private chats, or verified completion log. A reviewed import is a local candidate, not a fresh provider verification. Checkmarks stay in this browser unless exported. Never put personal contacts, passwords or raw exports on public GitHub.</p></section>'
].join("");
const compass=document.querySelector(".compass");if(!compass)return;
compass.insertAdjacentHTML("afterend",html);
if(location.hash==="#owner-actions"&&typeof requestAnimationFrame==="function")requestAnimationFrame(()=>get("owner-actions").scrollIntoView({block:"start"}));
function validData(data){
 if(!data||data.schema!=="cf.link.vault.owner_view.v1"||typeof data.revision!=="string"||!Array.isArray(data.actions)||data.actions.length<1||data.actions.length>75)throw Error("Wrong action view schema");
 const ids=new Set();for(const a of data.actions){
  if(!a||!/^CF-ACT-\d{3}$/.test(a.id)||ids.has(a.id)||!Object.prototype.hasOwnProperty.call(zones,a.zone)||!["owner","assistant"].includes(a.owner)||!["title","detail","action","link","label","source","proof","caution","priority"].every(k=>typeof a[k]==="string"&&a[k].length<750)||!urlOK(a.link)||!urlOK(a.source))throw Error("Invalid action record");
  ids.add(a.id);
 }
 return data;
}
const make=(tag,cls,txt)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(txt!==undefined)e.textContent=txt;return e};
function save(){try{localStorage.setItem(CHECKS,JSON.stringify(checks))}catch(_){get("oa-status").textContent="Local storage unavailable — export checks"}}
const viewTitles={mine:"My turn",later:"Later",waiting:"Waiting",assistant:"AI work",all:"All actions",done:"Checked locally"};
function show(next){
 if(!Object.prototype.hasOwnProperty.call(views,next))return;
 view=next;
 for(const b of document.querySelectorAll("#owner-actions [data-view]")){
  const selected=b.dataset.view===view;
  if(b.classList.contains("oa-tab")){
   b.setAttribute("aria-selected",String(selected));b.tabIndex=selected?0:-1;
  } else b.setAttribute("aria-pressed",String(selected));
 }
 const panel=get("oa-items"),tab=get("oa-tab-"+view);
 if(panel&&tab)panel.setAttribute("aria-labelledby",tab.id);
 const breadcrumb=get("cf-breadcrumb-zone");
 if(breadcrumb)breadcrumb.textContent=viewTitles[view]||"Action Sphere";
 render();window.dispatchEvent(new CustomEvent("cf-spider-view",{detail:{view}}));
}
function render(){
 const list=get("oa-items");list.replaceChildren();
 let all=catalog;
 const core=window.CFSpiderCore;
 if(core){
  try{
   const publicRows=catalog.map(a=>core.normalizeAction(a,"public_snapshot"));
   all=core.connect(publicRows.concat(privateActions),graph,registry).actions;
  }catch(_){get("oa-status").textContent="Spider source conflict — showing raw public snapshot";all=catalog}
 }
 const priority=all.filter(a=>a.owner==="owner"&&["now","soon","ready"].includes(a.zone)&&!checks[a.id]).length;
 const items=core?core.selectLane(all,view,checks,query):all.filter(a=>view==="done"?!!checks[a.id]:views[view].includes(a.zone)&&(view!=="mine"||!checks[a.id]));
 get("oa-count").textContent=items.length+" shown · "+priority+" priority";
 if(!items.length){list.append(make("p","oa-empty",catalog.length?"No items in this lane. Select All for everything.":"Offline and no saved action view. Retry refresh online."));return}
 for(const a of items){
  const card=make("article","oa-item");card.dataset.zone=a.zone;card.dataset.actionId=a.id;card.dataset.done=checks[a.id]?"true":"false";
  const top=make("div","oa-item-top");top.append(make("span","oa-pill",zones[a.zone]),make("span","oa-pill",a.priority));
  card.append(top,make("h4",null,a.title),make("p",null,a.action));
  if(a.project_id)card.append(make("p","oa-thread","Thread: "+a.project_id+(a.project_checked?" · linked project":" · source mapping pending")+(a.conflict?" · CONFLICT":"")));
  if(a.origin==="owner_local")card.append(make("p","oa-thread","PRIVATE · imported into this browser's memory only"));
  if(a.review_required)card.append(make("p","oa-warning","Possible action · NEEDS YOUR REVIEW · not confirmed outstanding"));
  if(a.origin==="owner_local"){
   const holder=make("label","oa-project-label","Connect privately to existing project");
   const picker=make("select","oa-project-select");
   const choices=[{id:"UNRESOLVED",title:"No project selected"}].concat(
    graph&&graph.schema==="cf0.public_topic_graph.v1"&&Array.isArray(graph.nodes)?
     graph.nodes.filter(n=>/^[A-Z][A-Z0-9-]{1,60}$/.test(n.id)).map(n=>({id:n.id,title:n.title})):[]);
   for(const choice of choices){
    const option=make("option",null,choice.id+" · "+choice.title);option.value=choice.id;picker.append(option);
   }
   picker.value=choices.some(o=>o.id===a.project_id)?a.project_id:"UNRESOLVED";
   picker.onchange=()=>{
    const item=privateActions.find(x=>x.id===a.id);
    if(!item||!choices.some(o=>o.id===picker.value))return;
    item.project_id=picker.value;
    render();get("oa-status").textContent="Project link set locally · no public changes";
   };
   holder.append(picker);card.append(holder);
  }
  if(a.conflict)card.append(make("p","oa-warning","Source disagreement — inspect originals before resolving"));
  if(a.due_date)card.append(make("p",a.due_state==="overdue"?"oa-warning":"oa-thread","Documented deadline: "+a.due_date+" · "+a.due_state));
  const buttons=make("div","oa-item-buttons");
  if(a.link&&urlOK(a.link)){
   const link=make("a","oa-small main",(a.label||"Open source")+" ↗");link.href=a.link;link.target="_blank";link.rel="noopener noreferrer";buttons.append(link);
  }else buttons.append(make("span","oa-small","Private indexed source · no web link"));
  const trace=make("button","oa-small oa-inspect","Trace thread");trace.type="button";buttons.append(trace);
  if(a.origin==="owner_local"&&a.review_required){
   const accept=make("button","oa-small","I checked — add to My turn");accept.type="button";
   accept.onclick=()=>{
    const item=privateActions.find(x=>x.id===a.id);
    if(!item)return;
    item.review_required=false;item.zone="ready";item.priority="LOCALLY REVIEWED";
    show("mine");get("oa-status").textContent="Owner-reviewed locally · not externally verified";
   };
   buttons.append(accept);
  }
  if(a.owner==="owner"&&a.zone!=="waiting"&&!a.review_required){
   const button=make("button","oa-small",checks[a.id]?"↶ Undo local check":"✓ I handled this locally");button.type="button";
   button.onclick=()=>{if(checks[a.id])delete checks[a.id];else checks[a.id]=new Date().toISOString();save();render()};buttons.append(button);
  }
  card.append(buttons);
  const detail=make("details");detail.append(make("summary",null,"Why · proof · original source"));
  detail.append(make("p",null,"Context: "+a.detail),make("p",null,"Proof: "+a.proof),make("p",null,"Caution: "+a.caution));
  if(a.source&&urlOK(a.source)){
   const src=make("a","oa-small","Original source ↗");src.href=a.source;src.target="_blank";src.rel="noopener noreferrer";detail.append(src);
  }
  if(a.source_refs&&a.source_refs.length){
   detail.append(make("p","oa-pointer","Indexed private evidence: "+a.source_refs.length+" source pointer(s) · not publicly fetchable"));
   for(const sourceRef of a.source_refs.slice(0,2))detail.append(make("p","oa-pointer",sourceRef));
  }
  if(a.review_required)detail.append(make("p","oa-warning","Candidate only. Read the original before promoting to an action; the request may already be resolved."));
  if(a.project_source&&/^[A-Za-z0-9_./-]+$/.test(a.project_source)){
   const project=make("a","oa-small","Parent project ↗");project.href=BASE+a.project_source;
   project.target="_blank";project.rel="noopener noreferrer";detail.append(project);
  }
  if(a.work_orders&&a.work_orders.length)detail.append(make("p",null,"Explicit CF-200 references: "+a.work_orders.map(t=>t.id+" ("+t.status+")").join(", ")));
  if(a.evidence_urls&&a.evidence_urls.length>1)detail.append(make("p",null,"Corroborating source links: "+a.evidence_urls.length));
  card.append(detail);list.append(card);
 }
}
function ageStamp(date){
 const start=Date.parse(String(date||"")+"T00:00:00Z");
 if(!Number.isFinite(start))return "age unknown";
 const days=Math.max(0,Math.floor((Date.now()-start)/86400000));
 return days>2?"STALE ("+days+" days old) — check current source":days+" days old";
}
function adopt(data,network){
 validData(data);catalog=data.actions;revision=data.revision;catalogDate=data.as_of;
 get("oa-status").textContent=(network?"Public snapshot fetched":"Saved snapshot, not checked now")+" · "+revision+" · "+catalogDate+" · "+ageStamp(catalogDate)+" · not provider verification";
 render();
}
async function refresh(){
 const button=get("oa-refresh");button.disabled=true;get("oa-status").textContent="Checking public view…";
 try{
  const response=await fetch("./owner-actions.json?check="+Date.now(),{cache:"no-store",credentials:"omit"});
  if(!response.ok)throw Error("HTTP "+response.status);
  const raw=await response.text();if(raw.length>100000)throw Error("Unexpected size");
  const data=validData(JSON.parse(raw));adopt(data,true);
  try{localStorage.setItem(CACHE,JSON.stringify(data))}catch(_){}
 }catch(_){get("oa-status").textContent="Offline / not checked now · "+revision+" · "+ageStamp(catalogDate)+" · saved view only";if(!catalog.length)render()}
 finally{button.disabled=false}
}
document.querySelectorAll("#owner-actions [data-view]").forEach(b=>b.addEventListener("click",()=>show(b.dataset.view)));
const actionTabs=document.querySelector("#owner-actions .oa-tabs");
if(actionTabs)actionTabs.addEventListener("keydown",event=>{
 if(!["ArrowLeft","ArrowRight","Home","End"].includes(event.key))return;
 const current=event.target.closest('[role="tab"]');
 const tabs=[...actionTabs.querySelectorAll('[role="tab"][data-view]')];
 if(!current||!tabs.includes(current))return;
 const i=tabs.indexOf(current);
 const next=event.key==="ArrowLeft"?(i-1+tabs.length)%tabs.length:
            event.key==="ArrowRight"?(i+1)%tabs.length:
            event.key==="Home"?0:tabs.length-1;
 event.preventDefault();show(tabs[next].dataset.view);tabs[next].focus();
});

get("oa-search").addEventListener("input",event=>{query=event.target.value;render()});
get("oa-cf200").addEventListener("click",async()=>{
 const button=get("oa-cf200"),status=get("oa-cf200-status");button.disabled=true;
 status.textContent="Reading public work-order source…";
 try{
  const response=await fetch("https://raw.githubusercontent.com/whoiwts110217-creator/CF-0/main/automation_200/registry.json",{cache:"no-store",credentials:"omit"});
  if(!response.ok)throw Error("HTTP "+response.status);
  const raw=await response.text();if(raw.length>175000)throw Error("Registry too large");
  const value=JSON.parse(raw);
  if(value.schema!=="CF200.1"||value.target!==200||!Array.isArray(value.tasks)||value.tasks.length!==200||
     !Number.isInteger(value.completed)||value.completed<0||value.completed>200||
     value.tasks.some(task=>!/^CF-\d{3}$/.test(task.id)||!["planned","verified"].includes(task.status)))
     throw Error("Registry schema or count mismatch");
  registry=value;
  status.textContent="CF-200 "+value.completed+"/200 source-verified · not HP/payment proof";
  render();
 }catch(_){
  registry=null;status.textContent="CF-200 unavailable or invalid · status unknown";render();
 }finally{button.disabled=false}
});
get("oa-clear-private").addEventListener("click",()=>{
 privateActions=[];
 get("oa-clear-private").disabled=true;
 get("oa-status").textContent="Private import cleared from current page memory";
 render();
});
get("oa-import").addEventListener("change",async event=>{
 const file=event.target.files&&event.target.files[0];if(!file)return;
 try{
  if(file.size>150000)throw Error("File too large (150 KB maximum)");
  if(!window.CFSpiderCore)throw Error("Spider Core unavailable");
  const imported=window.CFSpiderCore.validateManifest(JSON.parse(await file.text()));
  privateActions=imported;
  get("oa-clear-private").disabled=false;
  get("oa-status").textContent=privateActions.length+" private entries in memory only — never uploaded";
  render();
 }catch(err){get("oa-status").textContent="Import rejected: "+String(err.message||err).slice(0,100)}
 event.target.value="";
});
async function loadGraph(){
 try{
  const response=await fetch("https://raw.githubusercontent.com/whoiwts110217-creator/CF-0/main/docs/PUBLIC_CONTEXT_GRAPH.json",{cache:"no-store",credentials:"omit"});
  if(!response.ok)throw Error("graph unavailable");
  const raw=await response.text();if(raw.length>150000)throw Error("graph too large");
  const data=JSON.parse(raw);
  if(data.schema!=="cf0.public_topic_graph.v1"||!Array.isArray(data.nodes))throw Error("graph schema");
  graph=data;render();
 }catch(_){graph=null;render()}
}
loadGraph();
get("oa-refresh").addEventListener("click",refresh);
get("oa-export").addEventListener("click",()=>{
 const payload={schema:"cf.link.vault.owner.checks.v1",savedAt:new Date().toISOString(),checkedLocally:checks};
 const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json"});
 const uri=URL.createObjectURL(blob),link=make("a");link.href=uri;link.download="CF-Owner-Actions-Local-Checks.json";document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(uri),3000);
 get("oa-status").textContent="Backup requested. Check Safari Files / Downloads.";
});
window.addEventListener("cf-owner-checks-updated",()=>{try{const saved=JSON.parse(localStorage.getItem(CHECKS)||"{}");if(saved&&typeof saved==="object"&&!Array.isArray(saved)){checks=Object.fromEntries(Object.entries(saved).filter(([k,v])=>/^CF-ACT-\d{3}$/.test(k)&&typeof v==="string"&&v.length<50));render()}}catch(_){}});
try{adopt(validData(JSON.parse(localStorage.getItem(CACHE)||"null")),false)}catch(_){}
render();refresh();
})();
