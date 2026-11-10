import test from "node:test";
import assert from "node:assert/strict";
import {createRequire} from "node:module";
import {readFileSync} from "node:fs";
const require=createRequire(import.meta.url);
const core=require("../spider-core.js");
const root=new URL("../",import.meta.url);
const source=JSON.parse(readFileSync(new URL("owner-actions.json",root),"utf8"));
const item={id:"CF-ACT-090",zone:"ready",owner:"owner",priority:"P1",title:"Verify route",
 action:"Inspect the source",proof:"Matching source",link:"https://github.com/example/repo",
 source:"https://github.com/example/repo/issues/1",project_id:"AUTO-08"};
test("original public snapshot connects to named projects",()=>{
 const graph=JSON.parse(readFileSync(new URL("../../docs/PUBLIC_CONTEXT_GRAPH.json",root),"utf8"));
 const out=core.connect(source.actions.map(x=>core.normalizeAction(x,"public_snapshot")),graph,null);
 assert.equal(out.schema,"cf0.spider.core.v1");
 assert.equal(out.actions.length,22);
 assert.equal(out.actions.filter(x=>x.project_checked).length,22);
 assert.equal(out.missing.length,0);
 assert.ok(out.edges.some(x=>x.kind==="belongs_to"&&x.to==="AUTO-08"));
 assert.equal(out.provenance.remote_conversation_access,false);
 assert.equal(out.provenance.completion_mutations,false);
});
test("no accidental fuzzy merge across wording or projects",()=>{
 const a={...item,id:"CF-ACT-090",equivalence_key:"exact"};
 const b={...item,id:"CF-ACT-091",equivalence_key:"exact",project_id:"FIN-09"};
 assert.equal(core.coalesce([a,b]).length,2);
 assert.equal(core.coalesce([{...item,id:"CF-ACT-090"},{...item,id:"CF-ACT-091"}]).length,2);
});
test("explicit equivalence key merges without losing source references",()=>{
 const a={...item,equivalence_key:"same"};
 const b={...a,id:"CF-ACT-091",source:"https://github.com/example/repo/issues/2"};
 const out=core.coalesce([a,b]);
 assert.equal(out.length,1);
 assert.deepEqual(out[0].view_ids,["CF-ACT-090","CF-ACT-091"]);
 assert.equal(out[0].evidence_urls.length,2);
});
test("contradictory zone or proof remains flagged, not silently completed",()=>{
 const a={...item,equivalence_key:"same"};
 const b={...a,id:"CF-ACT-091",zone:"waiting",proof:"Opposing evidence"};
 assert.equal(core.coalesce([a,b])[0].conflict,true);
 assert.equal(core.coalesce([a,b])[0].zone,"ready");
});
test("same public ID with conflicting identity fails closed",()=>{
 assert.throws(()=>core.coalesce([item,{...item,project_id:"FIN-09"}]),/Conflicting action ID/);
});
test("unresolved canonical project or work order exposes gaps",()=>{
 const out=core.connect([core.normalizeAction({...item,task_ids:["CF-999"]},"public_snapshot")],
    {schema:"cf0.public_topic_graph.v1",nodes:[]},{schema:"CF200.1",tasks:[]});
 assert.deepEqual(out.missing,[{action:"CF-ACT-090",missing_project:"AUTO-08"},
   {action:"CF-ACT-090",missing_work_order:"CF-999"}]);
});
test("actual task status only comes from exact registry ID",()=>{
 const out=core.connect([core.normalizeAction({...item,task_ids:["CF-137"]},"public_snapshot")],
  {schema:"cf0.public_topic_graph.v1",nodes:[{id:"AUTO-08",title:"Runner",source:"docs/x.md"}]},
  {schema:"CF200.1",tasks:[{id:"CF-137",status:"planned",title:"Grant status",evidence:""}]});
 assert.equal(out.actions[0].work_orders[0].status,"planned");
 assert.equal(out.edges.filter(x=>x.kind==="canonical_work_order").length,1);
});
test("missing or unsafe evidence is rejected",()=>{
 assert.throws(()=>core.normalizeAction({...item,source:""},"public_snapshot"),/Invalid action/);
 assert.throws(()=>core.normalizeAction({...item,source:"javascript:alert(1)"},"public_snapshot"),/Invalid action/);
 assert.throws(()=>core.normalizeAction({...item,link:"https://user:password@example.com"},"public_snapshot"),/Invalid action/);
});
test("local import is bounded, explicit and private",()=>{
 assert.throws(()=>core.validateManifest({schema:"other",actions:[]}),/Requires/);
 const out=core.validateManifest({schema:"cf0.spider.action_manifest.v1",actions:[{...item,id:"LOCAL-1",
   source:"https://chatgpt.com/c/example-source"}]});
 assert.equal(out.length,1);
 assert.equal(out[0].evidence_level,"owner_imported_unverified");
 assert.equal(out[0].origin,"owner_local");
});
test("local reminders never imply canonical verified tasks",()=>{
 const out=core.selectLane(core.coalesce([item]),"done",{"CF-ACT-090":"2026-11-10T00:00:00Z"},"");
 assert.equal(out.length,1);
 assert.equal(out[0].evidence_level,"public_source_snapshot");
});
test("priority rail, optional lane, and search are deterministic",()=>{
 const b={...item,id:"CF-ACT-091",zone:"optional",title:"Budget"};
 assert.equal(core.selectLane(core.coalesce([b,item]),"mine",{},"").length,1);
 assert.equal(core.selectLane(core.coalesce([b,item]),"later",{},"Budget").length,1);
 assert.equal(core.selectLane(core.coalesce([b,item]),"mine",{"CF-ACT-090":"checked"},"").length,0);
});
test("no private chat URLs, contact rows or tokens are shipped in public view",()=>{
 const raw=JSON.stringify(source);
 assert.ok(!raw.includes("chatgpt.com/c/"));
 assert.ok(!raw.includes("@gmail.com"));
 assert.ok(!raw.includes("access_token="));
});
