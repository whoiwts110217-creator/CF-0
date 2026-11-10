/* CF-LINK-VAULT-001: local-only action checks, public-safe project view. */
(() => {
"use strict";
const get=id=>document.getElementById(id);
const BASE="https://github.com/whoiwts110217-creator/CF-0/blob/main/";
const CHECKS="cf_link_vault_owner_action_checks_v1",CACHE="cf_link_vault_owner_action_cache_v1";
const zones={now:"Do now",soon:"Deadline",ready:"Ready to test",conditional:"Only if needed",optional:"Optional",waiting:"Watching / hold",assistant:"Assistant work"};
const views={mine:["now","soon","ready"],later:["conditional","optional"],waiting:["waiting"],assistant:["assistant"],all:Object.keys(zones),done:[]};
const urlOK=value=>{try{const u=new URL(value);return u.protocol==="https:"&&!u.username&&!u.password}catch(_){return false}};
let catalog=[],revision="not loaded",view="mine",checks={};
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
'<aside class="oa-rail" aria-label="Consolidated action side list"><div class="oa-rail-top"><h3>Side list · action rail</h3><span id="oa-count" class="oa-count">Loading…</span></div><div class="oa-tabs">',
'<button type="button" class="oa-tab" data-view="mine" aria-pressed="true">My turn</button><button type="button" class="oa-tab" data-view="later" aria-pressed="false">Later</button><button type="button" class="oa-tab" data-view="waiting" aria-pressed="false">Waiting</button><button type="button" class="oa-tab" data-view="assistant" aria-pressed="false">AI work</button><button type="button" class="oa-tab" data-view="all" aria-pressed="false">All</button><button type="button" class="oa-tab" data-view="done" aria-pressed="false">Checked locally</button>',
'</div><div id="oa-items" class="oa-items" aria-live="polite"><p class="oa-empty">Loading public action view…</p></div></aside></div>',
'<div class="oa-tools"><button type="button" id="oa-refresh" class="btn primary">↻ Refresh action view</button><button type="button" id="oa-export" class="btn">↓ Backup my checks</button><a class="oa-small" target="_blank" rel="noopener noreferrer" href="https://github.com/whoiwts110217-creator/CF-0/blob/main/docs/OWNER_JUNGLE_MAP.md">Full project map ↗</a><span id="oa-status" class="oa-status" role="status">Not checked yet</span></div>',
'<p class="oa-note">Dated public-safe overlay, not a second task registry, automatic scan of private chats, or verified completion log. Checkmarks stay in this browser unless exported. Never put personal contacts, passwords or raw exports on public GitHub.</p></section>'
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
function show(next){view=next;for(const b of document.querySelectorAll("#owner-actions [data-view]"))b.setAttribute("aria-pressed",String(b.dataset.view===view));render()}
function render(){
 const list=get("oa-items");list.replaceChildren();
 const priority=catalog.filter(a=>a.owner==="owner"&&["now","soon","ready"].includes(a.zone)&&!checks[a.id]).length;
 const items=catalog.filter(a=>view==="done"?!!checks[a.id]:views[view].includes(a.zone)&&(view!=="mine"||!checks[a.id]));
 get("oa-count").textContent=items.length+" shown · "+priority+" priority";
 if(!items.length){list.append(make("p","oa-empty",catalog.length?"No items in this lane. Select All for everything.":"Offline and no saved action view. Retry refresh online."));return}
 for(const a of items){
  const card=make("article","oa-item");card.dataset.zone=a.zone;card.dataset.done=checks[a.id]?"true":"false";
  const top=make("div","oa-item-top");top.append(make("span","oa-pill",zones[a.zone]),make("span","oa-pill",a.priority));
  card.append(top,make("h4",null,a.title),make("p",null,a.action));
  const buttons=make("div","oa-item-buttons");const link=make("a","oa-small main",a.label+" ↗");link.href=a.link;link.target="_blank";link.rel="noopener noreferrer";buttons.append(link);
  if(a.owner==="owner"&&a.zone!=="waiting"){
   const button=make("button","oa-small",checks[a.id]?"↶ Undo local check":"✓ I handled this locally");button.type="button";
   button.onclick=()=>{if(checks[a.id])delete checks[a.id];else checks[a.id]=new Date().toISOString();save();render()};buttons.append(button);
  }
  card.append(buttons);
  const detail=make("details");detail.append(make("summary",null,"Why · proof · original source"));
  detail.append(make("p",null,"Context: "+a.detail),make("p",null,"Proof: "+a.proof),make("p",null,"Caution: "+a.caution));
  const src=make("a","oa-small","Original source ↗");src.href=a.source;src.target="_blank";src.rel="noopener noreferrer";detail.append(src);
  card.append(detail);list.append(card);
 }
}
function adopt(data,network){validData(data);catalog=data.actions;revision=data.revision;get("oa-status").textContent=(network?"Public view refreshed":"Saved view · not checked now")+" · "+revision+" · "+data.as_of;render()}
async function refresh(){
 const button=get("oa-refresh");button.disabled=true;get("oa-status").textContent="Checking public view…";
 try{
  const response=await fetch("./owner-actions.json?check="+Date.now(),{cache:"no-store",credentials:"omit"});
  if(!response.ok)throw Error("HTTP "+response.status);
  const raw=await response.text();if(raw.length>100000)throw Error("Unexpected size");
  const data=validData(JSON.parse(raw));adopt(data,true);
  try{localStorage.setItem(CACHE,JSON.stringify(data))}catch(_){}
 }catch(_){get("oa-status").textContent="Offline / not checked now · "+revision+" · saved view only";if(!catalog.length)render()}
 finally{button.disabled=false}
}
document.querySelectorAll("#owner-actions [data-view]").forEach(b=>b.addEventListener("click",()=>show(b.dataset.view)));
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
