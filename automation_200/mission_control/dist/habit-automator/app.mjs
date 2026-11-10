import {SCHEMA, STORAGE_KEY, emptyState, parseState, normalizeRoutine, normalizeStep, dueInfo, safeLink, shortcutLink, freshId, MAX_ROUTINES} from "./core.mjs";

const $ = id => document.getElementById(id);
const html = value => String(value ?? "").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#39;");
const nowISO = () => new Date().toISOString();
let state = emptyState(), draftSteps = [], editingId = null, storageReady = true;
const mission = "https://whoiwts110217-creator.github.io/CF-0/mission-control/";
const templates = [
  {key:"daily",name:"Morning mission check",description:"Review current priorities without changing any scheduled workers.",schedule:{type:"daily",time:"09:00",days:[]},steps:[
    {type:"check",label:"Choose today's single most important task"},
    {type:"link",label:"Review public Mission Control",target:mission},
    {type:"check",label:"Record what actually happened"}]},
  {key:"grant",name:"Grant inbox review",description:"Owner-reviewed email check; no automatic inbox access or submission.",schedule:{type:"weekly",time:"09:00",days:[1,2,3,4,5]},steps:[
    {type:"link",label:"Open your email inbox",target:"https://mail.google.com/"},
    {type:"check",label:"Review grant messages and deadlines"},
    {type:"check",label:"Log only confirmed outcomes"}]},
  {key:"focus",name:"Creative focus sprint",description:"A manual checklist you can launch when ready.",schedule:{type:"manual",time:"09:00",days:[]},steps:[
    {type:"check",label:"Select one current creative project"},
    {type:"check",label:"Work on one small deliverable"},
    {type:"check",label:"Capture the next action and source"}]},
  {key:"shortcut",name:"My iPhone Shortcut",description:"Launch an existing Shortcut you created in Apple's Shortcuts app.",schedule:{type:"manual",time:"09:00",days:[]},steps:[
    {type:"shortcut",label:"Launch your named Shortcut",target:"My Routine"},
    {type:"check",label:"Confirm the real-world outcome"}]}
];

function announce(message, type="neutral") {
  const el = $("toast"); el.textContent = message; el.dataset.tone = type;
}
function save() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); storageReady=true; }
  catch { storageReady=false; announce("Private storage is unavailable. Export a backup before leaving.", "warn"); }
}
function load() {
  try {
    const value=localStorage.getItem(STORAGE_KEY);
    state=value?parseState(value):emptyState();
  } catch {state=emptyState();storageReady=false;announce("Saved state couldn't be read. No account data was accessed.", "warn");}
}
function routineById(id){return state.routines.find(r=>r.id===id);}
function scheduleLabel(r) {
  const s=r.schedule;
  if(s.type==="manual")return "On demand";
  if(s.type==="daily")return "Every day · "+s.time;
  const names=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
  return s.days.map(d=>names[d]).join(", ")+" · "+s.time;
}
function renderStats(){
  const due=state.routines.filter(r=>dueInfo(r).due).length;
  $("metric-routines").textContent=String(state.routines.length);
  $("metric-due").textContent=String(due);
  $("metric-finished").textContent=String(state.history.filter(h=>h.status==="owner_marked").length);
  $("storage-state").textContent=storageReady?"Saved privately on this device":"Temporary session only — export your backup";
}
function renderTemplates(){
  $("template-list").innerHTML=templates.map(t=>'<button class="template" type="button" data-template="'+t.key+'"><span class="template-plus">+</span><span><strong>'+html(t.name)+'</strong><small>'+html(t.description)+'</small></span></button>').join("");
}
function renderRoutines(){
  const list=$("routine-list");
  if(!state.routines.length){list.innerHTML='<div class="empty">No routines yet. Add a template or create one below.</div>';return;}
  const sorted=[...state.routines].sort((a,b)=>Number(dueInfo(b).due)-Number(dueInfo(a).due));
  list.innerHTML=sorted.map(r=>{
    const info=dueInfo(r);
    const stepCount=r.steps.length;
    return '<article class="routine-card'+(info.due?" overdue":"")+'">'+
      '<div class="routine-top"><span class="routine-status '+(!r.enabled?"paused":info.due?"due":"waiting")+'">'+
      (!r.enabled?"Paused":info.due?"Due now":r.schedule.type==="manual"?"Ready":"Scheduled")+'</span>'+
      '<span class="muted mono">'+html(scheduleLabel(r))+'</span></div>'+
      '<h3>'+html(r.title)+'</h3><p>'+html(r.description || "No description")+'</p>'+
      '<div class="routine-bottom"><small>'+stepCount+' step'+(stepCount===1?"":"s")+' · '+html(!r.enabled?"Not scheduled":info.label)+'</small>'+
      '<div class="actions">'+
      '<button class="small primary" data-action="start" data-id="'+html(r.id)+'" type="button">Run</button>'+
      '<button class="small" data-action="edit" data-id="'+html(r.id)+'" type="button">Edit</button>'+
      '<button class="small" data-action="toggle" data-id="'+html(r.id)+'" type="button">'+(r.enabled?"Pause":"Resume")+'</button>'+
      '<button class="small subtle" data-action="copy" data-id="'+html(r.id)+'" type="button">Copy</button>'+
      '<button class="small danger-text" data-action="delete" data-id="'+html(r.id)+'" type="button">Delete</button>'+
      '</div></div></article>';
  }).join("");
}
function renderRun(){
  const host=$("run-panel");
  const active=state.active;
  if(!active){host.innerHTML='<div class="empty">No routine running. Tap <strong>Run</strong> on any routine to start a guided checklist.</div>';return;}
  const r=routineById(active.routineId);
  if(!r){state.active=null;save();renderRun();return;}
  const finished=active.completedStepIds.length;
  host.innerHTML='<div class="run-top"><div><p class="eyebrow">ACTIVE · OWNER-GUIDED</p><h3>'+html(r.title)+'</h3><p>'+finished+'/'+r.steps.length+' steps marked complete. A launch is not proof of an outside result.</p></div><button class="small" data-stop-run type="button">End without completing</button></div>'+
    '<div class="progress-track"><div style="width:'+Math.round(100*finished/r.steps.length)+'%"></div></div>'+
    '<ol class="step-list">'+r.steps.map(s=>{
      const done=active.completedStepIds.includes(s.id);
      let launch='';
      if(s.type==="link")launch='<a class="small link-action" target="_blank" rel="noopener noreferrer" href="'+html(safeLink(s.target))+'">Open website ↗</a>';
      if(s.type==="shortcut")launch='<a class="small link-action" href="'+html(shortcutLink(s.target))+'">Launch Shortcut ↗</a>';
      return '<li class="'+(done?"step-done":"")+'"><div class="step-title"><span class="step-number">'+(done?"✓":r.steps.indexOf(s)+1)+'</span><span><strong>'+html(s.label)+'</strong><small>'+html(s.type==="check"?"Owner confirms":s.type==="link"?"Open an external website":"Requires an existing iPhone Shortcut")+'</small></span></div><div class="step-actions">'+launch+'<button type="button" class="small '+(done?"":"primary")+'" data-finish-step="'+html(s.id)+'" '+(done?"disabled":"")+'>'+(done?"Marked":"Mark done")+'</button></div></li>';
    }).join("")+'</ol>';
}
function renderHistory(){
  const host=$("history-list");
  if(!state.history.length){host.innerHTML='<p class="muted">No recorded runs yet. History records what you marked, not external account verification.</p>';return;}
  host.innerHTML=state.history.slice(0,20).map(h=>'<div class="history-entry"><span><strong>'+html(h.title || h.routineId)+'</strong><small>'+new Date(h.finishedAt).toLocaleString()+'</small></span><span class="receipt '+(h.status==="owner_marked"?"":"aborted")+'">'+(h.status==="owner_marked"?"Owner-marked":"Ended early")+'</span></div>').join("");
}
function render(){renderStats();renderRoutines();renderRun();renderHistory();}
function openForm(){
  $("builder").scrollIntoView({behavior:"smooth",block:"start"});
  $("routine-title").focus({preventScroll:true});
}
function drawDraft(){
  $("draft-steps").innerHTML=draftSteps.length?draftSteps.map((s,i)=>'<li><div><strong>'+html(s.label)+'</strong><small>'+html(s.type==="link"?"Website · "+s.target:s.type==="shortcut"?"Shortcut · "+s.target:"Confirmation")+'</small></div><button type="button" class="small" data-remove-step="'+i+'">Remove</button></li>').join(""):'<li class="muted">Add at least one action.</li>';
}
function clearForm(){
  editingId=null;draftSteps=[];$("routine-form").reset();$("routine-time").value="09:00";$("routine-schedule").value="daily";$("builder-title").textContent="Create a routine";$("form-submit").textContent="Save routine";drawDraft();toggleSchedule();
}
function toggleSchedule(){
  $("time-fields").hidden=$("routine-schedule").value==="manual";
  $("day-fields").hidden=$("routine-schedule").value!=="weekly";
}
function toggleStepTarget(){
  const kind=$("step-type").value;
  $("step-target-wrap").hidden=kind==="check";
  $("step-target-label").textContent=kind==="link"?"HTTPS website address":"Exact iPhone Shortcut name";
  $("step-target").placeholder=kind==="link"?"https://example.org":"My Routine";
}
function beginEdit(id){
  const r=routineById(id);if(!r)return;
  if(state.active?.routineId===id){announce("End the active run before editing its steps, to preserve the completion record.","warn");return;}
  editingId=id;draftSteps=r.steps.map(s=>({...s}));
  $("routine-title").value=r.title;$("routine-description").value=r.description;
  $("routine-schedule").value=r.schedule.type;$("routine-time").value=r.schedule.time;
  document.querySelectorAll("[name=weekday]").forEach(e=>e.checked=r.schedule.days.includes(Number(e.value)));
  $("builder-title").textContent="Edit routine";$("form-submit").textContent="Update routine";
  toggleSchedule();drawDraft();openForm();
}
function finishActive(status){
  if(!state.active)return;
  const r=routineById(state.active.routineId),a=state.active, finishedAt=nowISO();
  if(r && status==="owner_marked")r.lastRunAt=finishedAt;
  state.history.unshift({id:freshId("run"),routineId:a.routineId,title:r?.title||"Removed routine",startedAt:a.startedAt,finishedAt,status,steps:a.completedStepIds.length});
  state.history=state.history.slice(0,500);state.active=null;save();render();
  announce(status==="owner_marked"?"Recorded owner-marked completion; external actions not independently verified.":"Routine ended; not counted as complete.","ok");
}
function startRoutine(id){
  const r=routineById(id);if(!r)return;
  if(state.active){
    if(state.active.routineId===id){$("run-anchor").scrollIntoView({behavior:"smooth"});return;}
    if(!confirm("End the current unfinished routine and start this one?"))return;
    finishActive("aborted");
  }
  state.active={routineId:id,startedAt:nowISO(),completedStepIds:[]};save();render();
  $("run-anchor").scrollIntoView({behavior:"smooth"});announce("Routine started locally. Complete each step explicitly.");
}
function addTemplate(key){
  const t=templates.find(x=>x.key===key);if(!t)return;
  if(state.routines.length>=MAX_ROUTINES){announce("Routine limit reached. Export a backup and delete an old routine before adding more.","warn");return;}
  const r=normalizeRoutine({id:freshId("routine"),title:t.name,description:t.description,enabled:true,
    schedule:t.schedule,steps:t.steps.map(s=>({...s,id:freshId("step")})),createdAt:nowISO(),lastRunAt:null});
  state.routines.unshift(r);save();render();announce("Template added. No background action was started.","ok");
}
function handleAction(action,id){
  const r=routineById(id);if(!r)return;
  if(action==="start")return startRoutine(id);
  if(action==="edit")return beginEdit(id);
  if(action==="toggle"){r.enabled=!r.enabled;save();render();announce(r.enabled?"Routine resumed. Its schedule is visible only when the app is open.":"Routine paused.","ok");}
  if(action==="copy"){
    if(state.routines.length>=MAX_ROUTINES){announce("Routine limit reached. Export a backup before removing any routine.","warn");return;}
    const copy=normalizeRoutine({...r,id:freshId("routine"),title:r.title+" copy",lastRunAt:null,createdAt:nowISO(),steps:r.steps.map(s=>({...s,id:freshId("step")}))});state.routines.unshift(copy);save();render();announce("Routine copied.");}
  if(action==="delete" && confirm('Delete "'+r.title+'"? This cannot be undone without a backup.')){
    if(state.active?.routineId===id)finishActive("aborted");
    state.routines=state.routines.filter(x=>x.id!==id);save();render();announce("Routine deleted. Previous receipts remain in local history.");
  }
}
function submitRoutine(event){
  event.preventDefault();
  try{
    const existing=editingId?routineById(editingId):null;
    if(!existing && state.routines.length>=MAX_ROUTINES)throw Error("100-routine limit reached. Export a backup before deleting old routines.");
    if(existing && state.active?.routineId===existing.id)throw Error("End the active run before editing this routine.");
    const type=$("routine-schedule").value;
    const days=[...document.querySelectorAll("[name=weekday]:checked")].map(x=>Number(x.value));
    const value=normalizeRoutine({id:existing?.id||freshId("routine"),title:$("routine-title").value,
      description:$("routine-description").value,enabled:existing?.enabled??true,
      schedule:{type,time:$("routine-time").value,days},steps:draftSteps,
      createdAt:existing?.createdAt||nowISO(),lastRunAt:existing?.lastRunAt||null});
    if(existing){state.routines=state.routines.map(r=>r.id===existing.id?value:r);}
    else state.routines.unshift(value);
    save();clearForm();render();announce("Routine saved locally. Scheduling does not enable background execution.","ok");
  }catch(e){announce(e.message,"warn");}
}
function downloadBackup(){
  const blob=new Blob([JSON.stringify(state,null,2)],{type:"application/json"});
  const url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download="cf0-habit-automator-backup.json";
  document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  announce("Backup prepared. Keep it private; it may contain your routine names.","ok");
}
async function importBackup(file){
  if(!file)return;
  try{
    if(file.size>256*1024)throw Error("Backup exceeds 256 KB");
    const imported=parseState(await file.text());
    if(!confirm("Replace all locally saved routines and history with this backup?"))return;
    state=imported;save();clearForm();render();announce("Private backup restored on this device.","ok");
  }catch(e){announce("Import rejected: "+e.message,"warn");}
}
function installEvents(){
  $("template-list").addEventListener("click",e=>{const b=e.target.closest("[data-template]");if(b)addTemplate(b.dataset.template);});
  $("routine-list").addEventListener("click",e=>{const b=e.target.closest("[data-action]");if(b)handleAction(b.dataset.action,b.dataset.id);});
  $("draft-steps").addEventListener("click",e=>{const b=e.target.closest("[data-remove-step]");if(b){draftSteps.splice(Number(b.dataset.removeStep),1);drawDraft();}});
  $("run-panel").addEventListener("click",e=>{
    const b=e.target.closest("[data-finish-step], [data-stop-run]");
    if(!b)return;
    if(b.hasAttribute("data-stop-run")){if(confirm("End this routine without completing it?"))finishActive("aborted");return;}
    const id=b.dataset.finishStep;if(!state.active||state.active.completedStepIds.includes(id))return;
    const routine=routineById(state.active.routineId);if(!routine?.steps.some(s=>s.id===id))return;
    state.active.completedStepIds.push(id);
    if(state.active.completedStepIds.length===routine.steps.length)finishActive("owner_marked");
    else{save();render();announce("Step marked by owner.");}
  });
  $("routine-form").addEventListener("submit",submitRoutine);
  $("routine-schedule").addEventListener("change",toggleSchedule);
  $("step-type").addEventListener("change",toggleStepTarget);
  $("add-step").addEventListener("click",()=>{
    try{
      if(draftSteps.length>=12)throw Error("Maximum 12 steps per routine");
      const step=normalizeStep({id:freshId("step"),type:$("step-type").value,label:$("step-label").value,target:$("step-target").value},draftSteps.length);
      draftSteps.push(step);$("step-label").value="";$("step-target").value="";drawDraft();announce("Step added to draft.");
    }catch(e){announce(e.message,"warn");}
  });
  $("cancel-edit").addEventListener("click",clearForm);
  $("backup").addEventListener("click",downloadBackup);
  $("restore").addEventListener("change",async e=>{await importBackup(e.target.files?.[0]);e.target.value="";});
  $("erase").addEventListener("click",()=>{if(confirm("Erase all local routines and history on THIS device? Export a backup first if needed.")){state=emptyState();save();clearForm();render();announce("Local Habit Automator data cleared.");}});
  $("add-new").addEventListener("click",()=>{clearForm();openForm();});
  document.querySelectorAll("[data-help]").forEach(button=>button.addEventListener("click",()=>{
    const id=button.dataset.help,panel=$(id);panel.hidden=!panel.hidden;button.setAttribute("aria-expanded",String(!panel.hidden));
  }));
  document.addEventListener("visibilitychange",()=>{if(!document.hidden)render();});
  setInterval(()=>{if(!document.hidden)renderStats();},60000);
}
load();renderTemplates();clearForm();render();installEvents();toggleStepTarget();
if("serviceWorker" in navigator)window.addEventListener("load",()=>navigator.serviceWorker.register("./service-worker.js").catch(()=>{}));
