import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync,readdirSync} from "node:fs";
import {CHATGPT_PLACEHOLDER_COUNT,SOURCES,records,parsePrivateInventory,inventoryStatus,shutdownPlan} from "../dist/controls.mjs";

test("every known scheduled channel is represented without exposing private task names",()=>{
  assert.equal(CHATGPT_PLACEHOLDER_COUNT,10);
  assert.equal(SOURCES.github.length,20);
  assert.equal(SOURCES.github.filter(x=>x.trigger==="schedule").length,5);
  assert.equal(SOURCES.github.filter(x=>x.trigger==="event").length,15);
  const workflowDir=new URL("../../../.github/workflows/",import.meta.url);
  const existing=readdirSync(workflowDir).filter(x=>x.endsWith(".yml")||x.endsWith(".yaml"));
  assert.equal(existing.length,20);
  assert.deepEqual(SOURCES.github.map(x=>x.id).sort(),existing.map(x=>x.replace(/\.ya?ml$/,"")).sort(),
    "Dashboard inventory must match every workflow file in repo");
  for(const row of SOURCES.github){
    const f=readFileSync(new URL(row.id+".yml",workflowDir),"utf8");
    const scheduled=/(^|\n)  schedule:/.test(f);
    assert.equal(row.trigger==="schedule",scheduled,"Trigger mismatch for "+row.id);
  }
  assert.equal(SOURCES.windows.length,3);
  assert.equal(SOURCES.continuation.length,1);
  const all=records();
  assert.equal(all.length,34);
  assert.equal(all.filter(x=>x.source==="chatgpt").length,10);
  assert.ok(all.filter(x=>x.source==="chatgpt").every(x=>x.title.startsWith("Private automation ")));
  assert.ok(all.filter(x=>x.source==="github").every(x=>x.url.startsWith("https://github.com/whoiwts110217-creator/CF-0/actions/workflows/")));
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
  assert.match(inventoryStatus(records(a)[1]),/Last reported paused/);
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
    "control-continuation","control-stage-research","control-copy-stage","control-plan-preview"])
    assert.ok(html.includes('id="'+id+'"'),"Missing "+id);
  assert.match(html,/type="checkbox" role="switch" disabled/);
  assert.match(html,/src="\.\/controls-ui\.mjs"/);
  assert.match(ui,/addEventListener\("change",importPrivate\)/);
  assert.match(ui,/disabled=true/);
  assert.doesNotMatch(ui,/fetch\(|sendMessage\(|exec\(|localStorage\.|sessionStorage\./);
});
