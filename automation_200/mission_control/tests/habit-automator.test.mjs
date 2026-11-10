import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {spawnSync} from "node:child_process";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import {SCHEMA,emptyState,normalizeStep,normalizeRoutine,parseState,dueInfo,safeLink,shortcutLink,MAX_ROUTINES} from "../dist/habit-automator/core.mjs";

const here=dirname(fileURLToPath(import.meta.url));
const app=join(here,"../dist/habit-automator");
function routine(schedule, lastRunAt=null) {
  return normalizeRoutine({id:"r1",title:"Check",enabled:true,schedule,lastRunAt,
    steps:[{id:"s1",type:"check",label:"Verify result"}]});
}
test("v1 private local-state backup is schema checked",()=>{
  assert.equal(emptyState().schema,SCHEMA);
  assert.equal(parseState(JSON.stringify(emptyState())).routines.length,0);
  assert.throws(()=>parseState('{"schema":"other","routines":[]}'),/Not a Habit Automator/);
  assert.throws(()=>parseState(JSON.stringify({schema:SCHEMA,routines:[routine({type:"manual"}),routine({type:"manual"})]})),/Duplicate routine/);
});
test("remote launch link is HTTPS only; named Shortcut is encoded",()=>{
  assert.equal(safeLink("javascript:alert(1)"),null);
  assert.equal(safeLink("http://example.com"),null);
  assert.equal(safeLink("https://a:b@example.com"),null);
  assert.equal(safeLink("https://example.com/path"),"https://example.com/path");
  assert.equal(shortcutLink("Focus & Go"),"shortcuts://run-shortcut?name=Focus%20%26%20Go");
  assert.throws(()=>normalizeStep({type:"link",label:"Bad",target:"javascript:alert(1)"}),/HTTPS/);
});
test("daily due status respects completion within the latest scheduled window",()=>{
  const now=new Date(2026,10,9,12,30);
  const d={type:"daily",time:"09:00",days:[]};
  assert.equal(dueInfo(routine(d),now).due,true);
  assert.equal(dueInfo(routine(d,new Date(2026,10,9,10).toISOString()),now).due,false);
  assert.equal(dueInfo(routine(d,new Date(2026,10,8,18).toISOString()),now).due,true);
  assert.equal(dueInfo(routine({type:"manual",time:"09:00",days:[]}),now).due,false);
});
test("weekly recurrence uses the owner device's local weekdays",()=>{
  const mon=new Date(2026,10,9,11);
  const r=routine({type:"weekly",time:"09:00",days:[1]});
  assert.equal(dueInfo(r,mon).due,true);
  assert.equal(dueInfo(r,new Date(2026,10,9,8)).due,true); // last Monday still unmarked
  r.enabled=false;
  assert.equal(dueInfo(r,mon).due,false);
  assert.throws(()=>routine({type:"weekly",time:"09:00",days:[]}),/weekday/);
});
test("imports sanitize, limit routines and reject non-HTTPS stored links",()=>{
  const r=routine({type:"manual",time:"09:00",days:[]});
  r.steps=[{id:"safe",type:"link",label:"Open",target:"https://example.org"}];
  assert.equal(parseState({schema:SCHEMA,routines:[r],history:[],active:null}).routines.length,1);
  r.steps[0].target="data:text/html,alert(1)";
  assert.throws(()=>parseState({schema:SCHEMA,routines:[r]}),/HTTPS/);
  assert.throws(()=>parseState({schema:SCHEMA,routines:Array(101).fill(r)}),/backup/);
});
test("iPhone app shell exposes real controls and no advertised remote switch",()=>{
  const page=readFileSync(join(app,"index.html"),"utf8");
  const script=readFileSync(join(app,"app.mjs"),"utf8");
  const manifest=JSON.parse(readFileSync(join(app,"manifest.webmanifest"),"utf8"));
  const sw=readFileSync(join(app,"service-worker.js"),"utf8");
  const ids=["routine-list","run-panel","routine-form","template-list","backup","restore","erase","routine-schedule","step-target"];
  for(const id of ids)assert.match(page,new RegExp('id="'+id+'"'));
  assert.match(page,/No background execution/);
  assert.match(script,/owner_marked/);
  assert.match(sw,/if\(target.origin!==scope.origin/);
  assert.equal(manifest.display,"standalone");
  assert.equal(manifest.scope,"./");
  assert.ok(manifest.icons.some(x=>x.src==="./icon-180.png"));
  assert.match(page,/apple-touch-icon.*icon-180.png/);
});

test("iPhone module JavaScript sources pass node syntax check",()=>{
  for(const file of ["app.mjs","core.mjs","service-worker.js"]){
    const result=spawnSync(process.execPath,["--check",join(app,file)],{encoding:"utf8"});
    assert.equal(result.status,0,result.stderr || file+" failed syntax check");
  }
});


test("untrusted backups cannot invent valid-looking missing IDs or active progress",()=>{
  const step=normalizeStep({type:"check",label:"Owner confirms"});
  assert.equal(step.id,"step-0");
  const original=normalizeRoutine({title:"Unnamed ID",schedule:{type:"manual"},steps:[{type:"check",label:"Check"}]});
  assert.equal(original.id,"routine-0");
  const imported=parseState({schema:SCHEMA,routines:[original],history:[],active:{
    routineId:"routine-0",startedAt:new Date(2026,10,9).toISOString(),completedStepIds:["ghost-step","step-0"]
  }});
  assert.deepEqual(imported.active.completedStepIds,["step-0"]);
});

test("stored routine capacity is enforced by both backup parser and UI creation paths",()=>{
  assert.equal(MAX_ROUTINES,100);
  const one=routine({type:"manual"});
  const unique=Array.from({length:MAX_ROUTINES},(_,i)=>({...one,id:"r"+i}));
  assert.equal(parseState({schema:SCHEMA,routines:unique}).routines.length,MAX_ROUTINES);
  assert.throws(()=>parseState({schema:SCHEMA,routines:[...unique,{...one,id:"overflow"}]}),/backup/);
  const ui=readFileSync(join(app,"app.mjs"),"utf8");
  assert.match(ui,/function addTemplate\(key\)[\s\S]*?state\.routines\.length>=MAX_ROUTINES/);
  assert.match(ui,/if\(action==="copy"\)[\s\S]*?state\.routines\.length>=MAX_ROUTINES/);
  assert.match(ui,/function submitRoutine\(event\)[\s\S]*?state\.routines\.length>=MAX_ROUTINES/);
});

test("the UI preserves active run step identities during edits",()=>{
  const ui=readFileSync(join(app,"app.mjs"),"utf8");
  assert.match(ui,/function beginEdit\(id\)[\s\S]*?state\.active\?\.routineId===id/);
  assert.match(ui,/function submitRoutine\(event\)[\s\S]*?state\.active\?\.routineId===existing\.id/);
});

test("backup import never claims persistent success if local storage rejects the write",()=>{
  const ui=readFileSync(join(app,"app.mjs"),"utf8");
  assert.match(ui,/storageReady=true; return true;/);
  assert.match(ui,/storageReady=false;[^\n]+return false;/);
  assert.match(ui,/state=imported;const persisted=save\(\);/);
  assert.match(ui,/announce\(persisted \? "Private backup restored on this device\." : "Backup loaded for this session only\./);
  assert.match(ui,/persisted\?"ok":"warn"/);
});
