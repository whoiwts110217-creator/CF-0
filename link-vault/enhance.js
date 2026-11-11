/* CF-LINK-VAULT-001 · Versioned public refresh and local iPhone corrections */
(() => {
"use strict";
const CATALOG_CACHE="cf_link_vault_public_catalog_v2";
let baseCatalog=DIRECTORY.slice();
let editSession=null;
let catalogRevision="bundled fallback";
let lastChecked=null;
const sourceLink="https://github.com/whoiwts110217-creator/CF-0/blob/main/link-vault/links.json";
const get=id=>document.getElementById(id);
function validHTTPS(value) {
 try { const u=new URL(value); return u.protocol==="https:" && !!u.hostname && !u.username && !u.password ? u.href : null }
 catch (_) { return null }
}
function validItem(item) {
 return item && typeof item.id==="string" && item.id.length<80 && /^[a-z0-9_-]+$/i.test(item.id) &&
 typeof item.title==="string" && item.title.trim().length>=1 && item.title.length<=105 &&
 typeof item.url==="string" && !!validHTTPS(item.url) &&
 typeof item.category==="string" && item.category.length<=50 &&
 typeof item.note==="string" && item.note.length<=260 &&
 ["live","source","external","unverified"].includes(item.status);
}
function verifyCatalog(data) {
 if (!data || data.schema!=="cf.link.vault.public.v2" || typeof data.revision!=="string" ||
 !Array.isArray(data.links) || data.links.length<40 || data.links.length>500) throw Error("Public catalog format is invalid");
 if(data.links.some(x=>!validItem(x)))throw Error("Public catalog has an invalid entry");
 const ids=new Set(data.links.map(x=>x.id));
 if(ids.size!==data.links.length)throw Error("Duplicate public link IDs");
 return data;
}
function readSaved() {
 try { const obj=JSON.parse(localStorage.getItem(STORAGE)||"{}"); return obj && typeof obj==="object"?obj:{} }
 catch (_) { return {} }
}
const previous=readSaved();
state.overrides=previous.overrides && typeof previous.overrides==="object" && !Array.isArray(previous.overrides)?previous.overrides:{};
state.lastOpened=previous.lastOpened && typeof previous.lastOpened==="object"?previous.lastOpened:null;
function store() { save() }
function updateStamp(text) { get("catalog-status").textContent=text }
function applyLocal() {
 DIRECTORY=baseCatalog.map(item=>{
   const fix=Object.prototype.hasOwnProperty.call(state.overrides,item.id)?state.overrides[item.id]:null;
   if(!fix || typeof fix!=="object" || !validHTTPS(fix.url)||typeof fix.title!=="string") return item;
   return {...item,title:fix.title.slice(0,105),url:validHTTPS(fix.url),note:typeof fix.note==="string"?fix.note.slice(0,260):item.note};
 });
}
function formatDate(value) {
 try { return new Date(value).toLocaleString(undefined,{month:"short",day:"numeric",hour:"numeric",minute:"2-digit"}) } catch (_) {return "earlier"}
}
function adoptCatalog(data, fetchedAt, network) {
 verifyCatalog(data);
 baseCatalog=data.links.map(x=>({...x}));
 catalogRevision=data.revision;
 lastChecked=fetchedAt||null;
 applyLocal();
 updateStamp((network?"Updated public catalog":"Saved catalog")+" · "+catalogRevision+
 (lastChecked?" · checked "+formatDate(lastChecked):" · check time unknown"));
 render();
}
async function refreshCatalog(manual=false) {
 const btn=get("refresh");btn.disabled=true;
 updateStamp(manual?"Checking public links now…":"Checking latest public catalog…");
 try {
   const response=await fetch("./links.json?check="+Date.now(),{cache:"no-store",credentials:"omit"});
   if(!response.ok)throw Error("HTTP "+response.status);
   const raw=await response.text();
   if(raw.length>250000)throw Error("Catalog is unexpectedly large");
   const data=verifyCatalog(JSON.parse(raw));
   const fetchedAt=new Date().toISOString();
   adoptCatalog(data,fetchedAt,true);
   try { localStorage.setItem(CATALOG_CACHE,JSON.stringify({data,fetchedAt})) } catch (_) {}
   if(manual)toast("Public catalog refreshed. Personal edits were preserved.");
 } catch (e) {
   const old=lastChecked?" · last checked "+formatDate(lastChecked):"";
   updateStamp("Offline / not checked now"+old+" · showing saved links");
   if(manual)toast("Could not check public catalog. Saved links still work; retry when online.");
 } finally { btn.disabled=false }
}
function remember(item) {
 if(!item || !validHTTPS(item.url))return;
 state.lastOpened={id:item.id||null,title:String(item.title||"Last link").slice(0,105),url:item.url,at:new Date().toISOString()};
 store();showTrail();
}
function showTrail() {
 const link=get("resume"),row=get("return-trail"),r=state.lastOpened;
 if(!r||!validHTTPS(r.url)){link.textContent="Open any link to leave a trail";link.href="https://whoiwts110217-creator.github.io/CF-0/";row.hidden=false;return}
 link.href=r.url;link.textContent=r.title+" ↗";row.hidden=false;
}
function currentMatches() {
 const q=query.trim().toLocaleLowerCase();
 return all().filter(l=>(filter==="All"||filter==="★ Favorites"&&state.favorites.includes(l.url)||l.category===filter)&&
 (!q||[l.title,l.url,l.category,l.note].join(" ").toLocaleLowerCase().includes(q)));
}
function openEditor(item,custom) {
 editSession={id:item.id,custom,originalUrl:item.url};
 get("dialog-title").textContent=custom?"Edit personal shortcut":"Fix this public link locally";
 get("new-title").value=item.title;get("new-url").value=item.url;
 get("new-cat").value=categories.includes(item.category)?item.category:"My links";
 get("new-cat").disabled=!custom;
 get("save-link").textContent="Save correction";
 if(get("add-dialog").showModal)get("add-dialog").showModal();
}
function resetEditor() {
 editSession=null;get("add-form").reset();
 get("new-cat").disabled=false;get("dialog-title").textContent="Add a shortcut";
 get("save-link").textContent="Save link";
}
function changeFavoriteURL(from,to) {
 if(from===to)return;
 if(state.favorites.includes(from)){state.favorites=state.favorites.filter(x=>x!==from);state.favorites.push(to)}
 if(state.lastOpened && state.lastOpened.url===from)state.lastOpened.url=to;
}
const legacyRender=render;
render=function() {
 legacyRender();
 showTrail();
 const matches=currentMatches(),cards=Array.from(get("cards").children);
 cards.forEach((card,i)=>{
   const item=matches[i];if(!item)return;
   const custom=state.custom.some(x=>x.id===item.id);
   const hasOverride=Object.prototype.hasOwnProperty.call(state.overrides,item.id);
   const link=card.querySelector("a.open");
   if(link)link.addEventListener("click",()=>remember(item));
   if(hasOverride&&!custom){const badge=card.querySelector(".state");if(badge)badge.textContent="Your local correction"}
   const actions=document.createElement("div");actions.className="foot-actions";
   const edit=document.createElement("button");edit.type="button";edit.className="mini";edit.textContent=custom?"Edit":"Fix link";edit.setAttribute("aria-label",(custom?"Edit ":"Fix ")+item.title);
   edit.onclick=()=>openEditor(item,custom);actions.append(edit);
   if(custom){
     const del=document.createElement("button");del.type="button";del.className="mini warn";del.textContent="Remove";
     del.onclick=()=>{
       if(!confirm("Remove this personal shortcut from this device?"))return;
       state.custom=state.custom.filter(x=>x.id!==item.id);state.favorites=state.favorites.filter(x=>x!==item.url);
       store();render();toast("Personal shortcut removed.");
     };actions.append(del);
   } else if(hasOverride) {
     const reset=document.createElement("button");reset.type="button";reset.className="mini";reset.textContent="Use public version";
     reset.onclick=()=>{
       const before=DIRECTORY.find(x=>x.id===item.id);
       delete state.overrides[item.id];applyLocal();
       const after=DIRECTORY.find(x=>x.id===item.id);if(before&&after)changeFavoriteURL(before.url,after.url);
       store();render();toast("Restored the public link on this device.");
     };actions.append(reset);
   }
   card.append(actions);
 });
};
get("add").onclick=()=>{
 resetEditor();
 if(get("add-dialog").showModal)get("add-dialog").showModal();
};
get("cancel").onclick=()=>{get("add-dialog").close();resetEditor()};
get("add-dialog").addEventListener("close",resetEditor);
get("add-form").onsubmit=e=>{
 e.preventDefault();
 const title=get("new-title").value.trim(),url=validHTTPS(get("new-url").value.trim());
 if(!title||title.length>105||!url){toast("Use a name and complete https:// URL.");return}
 if(editSession){
   const ed=editSession;
   if(ed.custom){
     state.custom=state.custom.map(x=>x.id===ed.id?{...x,title,url,category:get("new-cat").value,note:"Personal shortcut on this device"}:x);
   }else{
     const parent=baseCatalog.find(x=>x.id===ed.id);
     if(!parent){toast("This public link has changed. Refresh and retry.");return}
     state.overrides[ed.id]={title,url,note:parent.note};
   }
   changeFavoriteURL(ed.originalUrl,url);
   applyLocal();toast("Saved only on this device. Public GitHub is unchanged.");
 }else{
   if(state.custom.some(x=>x.url===url)){toast("You already have this personal shortcut.");return}
   state.custom.push({id:"local-"+Date.now()+"-"+Math.floor(Math.random()*100000),title,url,category:get("new-cat").value,status:"personal",note:"Personal shortcut on this device"});
   filter="My links";query="";get("q").value="";toast("Saved only on this device.");
 }
 store();get("add-dialog").close();resetEditor();render();
};
get("export").onclick=()=>{
 let ownerActionChecks={};try{ownerActionChecks=JSON.parse(localStorage.getItem("cf_link_vault_owner_action_checks_v1")||"{}")}catch(_){}
 const backup={schema:"cf.link.vault.backup.v1",savedAt:new Date().toISOString(),
 favorites:state.favorites,custom:state.custom,overrides:state.overrides,lastOpened:state.lastOpened,ownerActionChecks};
 const blob=new Blob([JSON.stringify(backup,null,2)],{type:"application/json"});
 const url=URL.createObjectURL(blob),a=document.createElement("a");
 a.href=url;a.download="CF-Link-Vault-Personal-Backup.json";document.body.append(a);a.click();a.remove();
 setTimeout(()=>URL.revokeObjectURL(url),2500);
 toast("Backup download requested. Check Safari Downloads / Files.");
};
get("import").onchange=async e=>{
 const file=e.target.files&&e.target.files[0];
 if(!file)return;
 // The user chooses whether to save imported personal URLs in shared-origin, unencrypted storage.
 if(!window.confirm("Import personal links into this browser? URLs and titles are NOT encrypted. Other pages on this website origin may read saved browser data. Do not import passwords, tokens, or sensitive account links. Choose Cancel to keep your data unchanged.")){
   e.target.value="";
   return;
 }
 try{
   if(file.size>300000)throw Error("File is too large");
   const obj=JSON.parse(await file.text());
   if(obj.schema!=="cf.link.vault.backup.v1"||!Array.isArray(obj.favorites)||!Array.isArray(obj.custom))throw Error("Not a Link Vault backup");
   const seen=new Set(state.custom.map(x=>x.url));
   for(const c of obj.custom.slice(0,500)){
     if(typeof c.title!=="string"||!c.title.trim()||c.title.length>105||!validHTTPS(c.url)||seen.has(c.url))continue;
     state.custom.push({id:"local-"+Date.now()+"-"+state.custom.length,title:c.title,url:validHTTPS(c.url),category:categories.includes(c.category)?c.category:"My links",status:"personal",note:"Imported personal shortcut"});seen.add(c.url);
   }
   for(const u of obj.favorites.slice(0,500)){if(typeof u==="string"&&validHTTPS(u)&&!state.favorites.includes(u))state.favorites.push(u)}
   if(obj.overrides && typeof obj.overrides==="object"&&!Array.isArray(obj.overrides)){
     for(const [id,val] of Object.entries(obj.overrides)){
       if(!baseCatalog.some(x=>x.id===id)||!val||!validHTTPS(val.url)||typeof val.title!=="string"||val.title.length>105)continue;
       state.overrides[id]={title:val.title,url:validHTTPS(val.url),note:typeof val.note==="string"?val.note.slice(0,260):""};
     }
   }
   if(obj.ownerActionChecks&&typeof obj.ownerActionChecks==="object"&&!Array.isArray(obj.ownerActionChecks)){
    const safe=Object.fromEntries(Object.entries(obj.ownerActionChecks).filter(([id,v])=>/^CF-ACT-\d{3}$/.test(id)&&typeof v==="string"&&v.length<50));
    try{localStorage.setItem("cf_link_vault_owner_action_checks_v1",JSON.stringify(safe));window.dispatchEvent(new Event("cf-owner-checks-updated"))}catch(_){}
   }
   applyLocal();store();render();toast("Personal links, corrections and any action checks imported.");
 }catch(err){toast("Import failed: "+err.message)}
 e.target.value="";
};
for(const route of document.querySelectorAll(".route")){
 route.addEventListener("click",()=>remember({id:"route",title:route.dataset.route||route.textContent,url:route.href}));
}
get("resume").addEventListener("click",()=>{const r=state.lastOpened;if(r)remember(r)});
get("refresh").onclick=()=>refreshCatalog(true);
try {
 const cached=JSON.parse(localStorage.getItem(CATALOG_CACHE)||"null");
 if(cached && cached.data && cached.fetchedAt)adoptCatalog(cached.data,cached.fetchedAt,false);
 else {applyLocal();render()}
}catch(_){applyLocal();render()}
refreshCatalog(false);
if("serviceWorker" in navigator){
 let switched=false;
 navigator.serviceWorker.addEventListener("controllerchange",()=>{
   if(!switched){switched=true;location.reload()}
 });
}
})();