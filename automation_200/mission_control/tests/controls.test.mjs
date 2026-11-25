import test from "node:test";
import assert from "node:assert/strict";
import {existsSync,readFileSync,readdirSync} from "node:fs";
import {fileURLToPath} from "node:url";
import path from "node:path";
import {CHATGPT_PLACEHOLDER_COUNT,SOURCES,records,parsePrivateInventory,inventoryStatus,shutdownPlan} from "../dist/controls.mjs";

const repoRoot=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../../..");
const workflowDirs=[
  path.join(repoRoot,".github/workflows"),
  path.join(repoRoot,"archive/workflows"),
];

function workflowFiles(){
  const names=[];
  for(const dir of workflowDirs){
    if(!existsSync(dir)) continue;
    for(const name of readdirSync(dir)){
      if(name.endsWith(".yml")||name.endsWith(".yaml")) names.push(name);
    }
  }
  return names;
}

function readWorkflow(id){
  for(const dir of workflowDirs){
    for(const ext of [".yml",".yaml"]){
      const file=path.join(dir,id+ext);
      if(existsSync(file)) return readFileSync(file,"utf8");
    }
  }
  throw new Error("missing workflow "+id);
}

test("every known scheduled channel is represented without exposing private task names",()=>{
  assert.equal(CHATGPT_PLACEHOLDER_COUNT,11);
  const existing=workflowFiles();
  assert.equal(SOURCES.github.length,existing.length,"Every real workflow file must have a source-only inventory row, including archived workflows");
  const scheduledCount=SOURCES.github.filter(x=>x.trigger==="schedule").length;
  const manualCount=SOURCES.github.filter(x=>x.trigger==="event").length;
  assert.equal(scheduledCount+manualCount,existing.length,"Every workflow must be classified");
  assert.deepEqual(SOURCES.github.map(x=>x.id).sort(),existing.map(x=>x.replace(/\.ya?ml$/,"")).sort(),
    "Dashboard inventory must match every workflow file in repo, including archive/workflows");
  for(const row of SOURCES.github){
    const f=readWorkflow(row.id);
    const scheduled=/(^|\n)  schedule:/.test(f);
    assert.equal(row.trigger==="schedule",scheduled,"Trigger mismatch for "+row.id);
  }
  assert.equal(SOURCES.windows.length,3);
  assert.equal(SOURCES.continuation.length,1);
  const all=records();
  assert.equal(all.length,CHATGPT_PLACEHOLDER_COUNT+SOURCES.github.length+SOURCES.windows.length+SOURCES.continuation.length);
  assert.equal(all.filter(x=>x.source==="chatgpt").length,11);
  assert.ok(all.filter(x=>x.source==="chatgpt").every(x=>x.title.startsWith("Private automation ")));
  assert.ok(all.filter(x=>x.source==="github").every(x=>x.url.startsWith("https://github.com/whoiwts110217-creator/CF-0/actions/workflows/")));
});

test("public free-browser monitor reflects its commented cron, never a claimed active marketing action",()=>{
  const source=SOURCES.github.find(x=>x.id==="cf0-free-browser-promotion");
  assert.ok(source,"New workflow has a source inventory row");
  assert.equal(source.trigger,"event");
  assert.equal(source.research,false,"Business monitor must not be silently included in research shutdown");
  assert.match(source.detail,/GET-only/i);
  assert.match(source.detail,/no posting/i);
  assert.match(source.detail,/cron commented out in source/i);
  const workflow=readWorkflow("cf0-free-browser-promotion");
  assert.doesNotMatch(workflow,/(^|\n)  schedule:/);
  assert.match(inventoryStatus({...source,source:"github"}),/live state unknown/);
});

test("AI Tracker PR-only regression workflow is source inventory, not a running monitor",()=>{
  const source=SOURCES.github.find(x=>x.id==="ai-tracker-pr-tests");
  assert.ok(source);
  assert.equal(source.trigger,"event");
  assert.equal(source.research,false);
  assert.match(source.detail,/Pull requests/);
  assert.match(source.detail,/offline unit tests only, not live monitoring/);
  assert.match(inventoryStatus({...source,source:"github"}),/live state unknown/);
});

test("private imported names are in-memory display data only and never treated as live controls",()=>{
  const a=parsePrivateInventory({schema:"cf0.private_automation_inventory.v1",automations:[
    {id:"private_1",title:" Research Brief ",is_enabled:true,research:true,secret:"should not survive"},
    {id:"private_2",title:"Grant Watch",is_enabled:false,research:false,token:"secret"}
  ]});
  assert.equal(a.length,2);
  assert.equal(a[0].title,"Research Brief");
  assert.equal("secret" in a[0],false);
  assert.equal("id" in a[0],false);
  assert.equal(records(a).filter(x=>x.source==="chatgpt").length,2);
  assert.match(inventoryStatus(records(a)[0]),/Last reported enabled/);
  assert.match(inventoryStatus(records(a)[1]),/Last reported not enabled/);
  assert.doesNotMatch(inventoryStatus(records(a)[1]),/Last reported paused/);
});
test("rejects invalid imports and duplicate task identifiers",()=>{
  assert.throws(()=>parsePrivateInventory({schema:"x",automations:[]}));
  assert.throws(()=>parsePrivateInventory({schema:"cf0.private_automation_inventory.v1",automations:[{id:"a",title:"A",is_enabled:"yes"}]}));
  assert.throws(()=>parsePrivateInventory({schema:"cf0.private_automation_inventory.v1",automations:[
    {id:"a",title:"A",is_enabled:true},{id:"a",title:"B",is_enabled:false}
  ]}));
  assert.throws(()=>parsePrivateInventory({schema:"cf0.private_automation_inventory.v1",automations:new Array(51).fill({})}));
});
test("shutdown planner does not claim that cloud or local actions occurred",()=>{
  const all=records();
  const staged=new Set(["github:ai-tracker-monitor","windows:CavemanFocusCF0FastLane"]);
  const text=shutdownPlan(all,staged);
  assert.match(text,/DRAFT ONLY/);
  assert.match(text,/No automations were paused, cancelled, or disabled/);
  assert.match(text,/AI Tracker/);
  assert.match(text,/Fast Lane/);
  assert.doesNotMatch(text,/grant monitoring.*disabled/i);
});
test("source HTML exposes all four categories with a disabled master switch and real JS handler",()=>{
  const html=readFileSync(new URL("../dist/index.html",import.meta.url),"utf8");
  const ui=readFileSync(new URL("../dist/controls-ui.mjs",import.meta.url),"utf8");
  for(const id of ["automation-controls","control-chatgpt","control-github","control-windows",
    "control-continuation","control-stage-research","control-copy-stage","control-plan-preview",
    "control-github-count","control-github-description"])
    assert.ok(html.includes('id="'+id+'"'),"Missing "+id);
  assert.match(html,/type="checkbox" role="switch" disabled/);
  assert.match(html,/src="\.\/controls-ui\.mjs"/);
  assert.match(ui,/addEventListener\("change",importPrivate\)/);
  assert.match(ui,/disabled=true/);
  assert.match(ui,/const workflowRecords=rows\.filter/);
  assert.match(ui,/control-github-count/);
  assert.match(ui,/control-github-description/);
  assert.doesNotMatch(html,/20 workflows: 5 scheduled, 15 event\/manual/);
  assert.doesNotMatch(ui,/fetch\(|sendMessage\(|exec\(|localStorage\.|sessionStorage\./);
});


test("master controller orientation retains every provider and fails closed on unverified controls",()=>{
  const html=readFileSync(new URL("../dist/index.html",import.meta.url),"utf8");
  const ui=readFileSync(new URL("../dist/controls-ui.mjs",import.meta.url),"utf8");
  for(const id of ["control-now","control-master","control-evidence","control-chatgpt","control-github","control-windows","control-continuation","control-stage-research"])
    assert.ok(html.includes('id="'+id+'"'),"Missing existing controller feature "+id);
  for(const target of ["control-now","control-master","control-evidence"])
    assert.ok(html.includes('href="#'+target+'"'),"Missing quick navigation to "+target);
  assert.match(html,/No global running count is asserted/);
  assert.match(html,/master controls remain disconnected/i);
  assert.match(html,/role="switch" disabled/);
  assert.match(ui,/Evidence: public workflow source only; current enabled\/running state not queried/);
  assert.match(ui,/Evidence: documented owner-local task; physical status not queried/);
  assert.match(ui,/Evidence: Chrome runner source only; installed\/live control not verified/);
  assert.match(ui,/Evidence: historic placeholder; no account readback/);
  assert.match(ui,/disabled=true/);
  assert.doesNotMatch(ui,/fetch\(|sendMessage\(|exec\(|localStorage\.|sessionStorage\./);
});


test("dated owner snapshot retains observation time without authenticating provider state",()=>{
  const observed_at="2026-11-09T20:00:00-05:00";
  const rows=parsePrivateInventory({schema:"cf0.private_automation_inventory.v1",observed_at,
    automations:[{id:"private-task",title:"Example",is_enabled:true,token:"do-not-expose"}]});
  assert.equal(rows[0].observedAt,observed_at);
  assert.equal("id" in rows[0],false);
  assert.equal("token" in rows[0],false);
  const rendered=records(rows)[0];
  assert.match(rendered.detail,/Owner-supplied snapshot observed/);
  assert.match(rendered.detail,/not an authenticated live connection/);
  assert.throws(()=>parsePrivateInventory({schema:"cf0.private_automation_inventory.v1",
    observed_at:"yesterday",automations:[]}));
});

test("Mission Control opens real ChatGPT Scheduled without publishing private task state",()=>{
  const html=readFileSync(new URL("../dist/index.html",import.meta.url),"utf8");
  assert.match(html, /id="open-live-chatgpt-tasks" href="https:\/\/chatgpt\.com\/scheduled"/);
  assert.match(html, /Authoritative account controls live in ChatGPT Scheduled/);
  assert.match(html, /rel="noopener noreferrer"/);
  assert.doesNotMatch(html, /Caveman Focus cash pilot|Bridge Builders Reply Watch/);
});
