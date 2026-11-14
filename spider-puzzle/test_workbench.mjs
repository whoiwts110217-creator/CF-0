import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
import vm from "node:vm";
const dir=path.dirname(fileURLToPath(import.meta.url));
const workbench=fs.readFileSync(path.join(dir,"workbench.html"),"utf8");
const inspector=fs.readFileSync(path.join(dir,"index.html"),"utf8");
const workflow=fs.readFileSync(path.join(dir,"../.github/workflows/publish-website.yml"),"utf8");
const script=workbench.match(/<script>([\s\S]*?)<\/script>/)?.[1];
const rows=JSON.parse(script.match(/const DATA=(\[[\s\S]*?\])\.map\(/)[1]);
const ids=rows.map(r=>r[0]);
const aliases=JSON.parse(inspector.match(/<script id="puzzle-data" type="application\/json">([\s\S]*?)<\/script>/)[1]).aliases;
const fn=script.slice(script.indexOf("function valid(input){"),script.indexOf("function snapshot()"));
function baseline(){
 return {schema:"cf0.spider.puzzle.manual-layout.v1",source_version:"v3.3.14",positions:Object.fromEntries(ids.map(id=>[id,{x:10,y:10}])),edges:[]};
}
function validate(input){
 return vm.runInNewContext("const IDS=new Set(ids);const LIMIT=36;"+fn+"valid(input);",{ids,input},{timeout:2000});
}
test("Workbench JavaScript parses",()=>assert.doesNotThrow(()=>new vm.Script(script)));
test("Exactly nine unique behavior aliases, not 1289 alleged finished skills",()=>{
 assert.equal(ids.length,9);assert.equal(new Set(ids).size,9);
 assert.deepEqual(rows.map(r=>[r[0],r[2]]),aliases.map(a=>[a.id,a.status]));
});
test("No external scripts, API credentials, or production execution",()=>{
 assert.doesNotMatch(workbench,/<script[^>]*src=/i);
 assert.doesNotMatch(script,/\b(fetch|eval|Function|WebSocket|XMLHttpRequest)\s*\(/);
 assert.match(workbench,/Nothing here executes code or controls your PC/);
});
test("Touch handles and keyboard movement are provided",()=>{
 assert.match(workbench,/touch-action:none/);
 assert.match(script,/setPointerCapture/);
 assert.match(script,/ArrowLeft/);
 assert.match(workbench,/aria-live="polite"/);
});
test("Initial state has zero connections; wiring is explicitly hypothetical",()=>{
 assert.match(script,/positions:structuredCloneSafe\(DEFAULT\),edges:\[\]/);
 assert.match(script,/HYPOTHESIS added, not verified/);
 assert.match(workbench,/hypothetical<\/strong> connections/);
});
test("Known source version, block IDs and positions are required",()=>{
 assert.ok(validate(baseline()));
 const extra=baseline();extra.positions["SPOOF-ID"]={x:2,y:2};assert.equal(validate(extra),null);
 const missing=baseline();delete missing.positions[ids[0]];assert.equal(validate(missing),null);
 const wrong=baseline();wrong.source_version="v0.0";assert.equal(validate(wrong),null);
 const out=baseline();out.positions[ids[0]].x=-1;assert.equal(validate(out),null);
 const nonfinite=baseline();nonfinite.positions[ids[0]].x=Infinity;assert.equal(validate(nonfinite),null);
});
test("Hypothesis wire validator rejects unknown, duplicate and self links",()=>{
 const valid=baseline();valid.edges=[{from:ids[0],to:ids[1]}];assert.ok(validate(valid));
 const unknown=baseline();unknown.edges=[{from:ids[0],to:"FAKE"}];assert.equal(validate(unknown),null);
 const self=baseline();self.edges=[{from:ids[0],to:ids[0]}];assert.equal(validate(self),null);
 const dup=baseline();dup.edges=[{from:ids[0],to:ids[1]},{from:ids[0],to:ids[1]}];assert.equal(validate(dup),null);
 const many=baseline();many.edges=Array.from({length:37},()=>({from:ids[0],to:ids[1]}));assert.equal(validate(many),null);
});
test("Mobile inspector links to workbench and Pages stages both",()=>{
 assert.match(inspector,/href="\.\/workbench\.html"/);
 assert.match(workflow,/cp spider-puzzle\/workbench\.html _site\/spider-puzzle\/workbench\.html/);
 assert.match(workflow,/assert Path\("_site\/spider-puzzle\/workbench\.html"\).is_file\(\)/);
});
