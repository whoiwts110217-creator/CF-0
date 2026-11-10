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
 const graph=JSON.parse(readFileSync(new URL("../docs/PUBLIC_CONTEXT_GRAPH.json",root),"utf8"));
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
test("snapshot age flags stale and future-dated public evidence",()=>{
 assert.equal(core.snapshotAge("2026-10-01","2026-11-10"),"stale");
 assert.equal(core.snapshotAge("2026-11-11","2026-11-10"),"future_conflict");
 assert.equal(core.snapshotAge("2026-11-10","2026-11-10"),"dated_snapshot");
 assert.equal(core.snapshotAge("unknown","2026-11-10"),"unknown");
});
test("overdue documented deadline is not a verified task outcome",()=>{
 assert.equal(core.dueState("2026-11-13","2026-11-12"),"upcoming");
 assert.equal(core.dueState("2026-11-13","2026-11-13"),"due_today");
 assert.equal(core.dueState("2026-11-13","2026-11-14"),"overdue");
 const a=core.normalizeAction({...item,due_date:"2026-11-13"},"public_snapshot");
 assert.equal(a.due_date,"2026-11-13");
 assert.equal(a.evidence_level,"public_source_snapshot");
});

test("indexed private actions can be reviewed without invented web URLs",()=>{
 const digest="a".repeat(64);
 const ref="indexed-chat:sha256:"+digest+":source-ordinal:0:msg-1";
 const local={id:"LOCAL-"+"b".repeat(24),zone:"conditional",owner:"owner",priority:"REVIEW",
   title:"Review action",action:"Check the original private message",source_ref:ref,
   source_refs:[ref],source:"",link:"",review_required:true,project_id:"UNRESOLVED"};
 const out=core.validateManifest({schema:"cf0.spider.action_manifest.v1",actions:[local]});
 assert.equal(out.length,1);
 assert.equal(out[0].source,"");
 assert.equal(out[0].link,"");
 assert.deepEqual(out[0].source_refs,[ref]);
 assert.equal(out[0].review_required,true);
 assert.equal(out[0].origin,"owner_local");
 assert.equal(out[0].evidence_level,"owner_imported_unverified");
});
test("private indexed duplicates retain every actual private source pointer",()=>{
 const first="indexed-chat:sha256:"+"a".repeat(64)+":source-ordinal:0:m1";
 const second="indexed-chat:sha256:"+"b".repeat(64)+":source-ordinal:0:m1";
 const base={id:"LOCAL-"+"f".repeat(24),zone:"conditional",owner:"owner",
   title:"Review",action:"Check private source",source_ref:first,source_refs:[first],
   project_id:"UNRESOLVED",link:"",source:""};
 const a=core.normalizeAction(base,"owner_local");
 const b=core.normalizeAction({...base,source_ref:second,source_refs:[second]},"owner_local");
 const merged=core.coalesce([a,b]);
 assert.equal(merged.length,1);
 assert.deepEqual(merged[0].source_refs,[first,second]);
 assert.deepEqual(merged[0].evidence_urls,[]);
});
test("private import rejects fake locators, credentials and mismatched ref lists",()=>{
 const valid="indexed-chat:sha256:"+"b".repeat(64)+":c1:m1";
 const row={id:"LOCAL-X",zone:"conditional",owner:"owner",title:"Review",
   action:"Check source",project_id:"UNRESOLVED",source_ref:valid};
 assert.throws(()=>core.normalizeAction({...row,source_ref:"file:///home/private/secrets.json"},"owner_local"),/Invalid action/);
 assert.throws(()=>core.normalizeAction({...row,source_refs:["indexed-chat:fake"]},"owner_local"),/Invalid private source/);
 assert.throws(()=>core.normalizeAction({...row,link:"https://user:password@chatgpt.com/c/id"},"owner_local"),/Invalid action/);
 assert.throws(()=>core.normalizeAction({...row,id:"CF-ACT-101"},"public_snapshot"),/Invalid action/);
 assert.throws(()=>core.validateManifest({schema:"cf0.spider.action_manifest.v1",actions:[row,row]}),/Duplicate imported/);
});
test("review-only entries stay out of urgent My turn until owner changes the lane",()=>{
 const ref="indexed-chat:sha256:"+"c".repeat(64)+":c1:m1";
 const a=core.normalizeAction({id:"LOCAL-1234",zone:"conditional",owner:"owner",
   title:"Possible",action:"Verify",source_ref:ref,review_required:true},"owner_local");
 assert.equal(core.selectLane(core.coalesce([a]),"mine",{},"").length,0);
 assert.equal(core.selectLane(core.coalesce([a]),"later",{},"").length,1);
 assert.equal(core.connect([a],null,null).provenance.private_upload,false);
});
