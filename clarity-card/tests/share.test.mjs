import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
const script = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
const url = "https://whoiwts110217-creator.github.io/CF-0/clarity-card/";
function boot({share,copy,secure=true}={}) {
  assert.ok(script);
  const actions = {};
  const fieldIds = ["problem","guess","hypothesis","evidence","alternative","action","criterion"];
  const fields = Object.fromEntries(fieldIds.map(id=>[id,{value:"",addEventListener(){},focus(){}}]));
  const status = {textContent:""};
  const buttons = Object.fromEntries(["example","download","copy","share-link","print"].map(id=>[id,{addEventListener(type,fn){actions[id]=fn}}]));
  const elems = {...fields,...buttons,status,"card-preview":{textContent:""},"clarity-form":{addEventListener(){}}};
  const navigator = {};
  if(share) navigator.share=share;
  if(copy) navigator.clipboard={writeText:copy};
  const prompts=[];
  const window={isSecureContext:secure,prompt:(...args)=>prompts.push(args)};
  runInNewContext(script,{navigator,window,document:{getElementById:id=>elems[id]}},{timeout:1500});
  return {actions,fields,status,prompts};
}
test("visible share control leaves save/copy/print in place",()=>{
  for(const id of ["share-link","download","copy","print"]) assert.ok(html.includes('id="'+id+'"'));
  assert.match(html,/share the free tool link, not your worksheet/i);
});
test("native share sends the public link and no worksheet data",async()=>{
  const calls=[],p=boot({share:async payload=>calls.push(payload)});
  p.fields.problem.value="PRIVATE_CONTENT";
  await p.actions["share-link"]();
  assert.equal(calls[0].url,url);
  assert.ok(!JSON.stringify(calls).includes("PRIVATE_CONTENT"));
});
test("share cancellation never falls back; blocked clipboard only prompts for the link",async()=>{
  let copied=false;
  const a=boot({share:async()=>{throw{name:"AbortError"}},copy:async()=>{copied=true}});
  await a.actions["share-link"]();
  assert.equal(copied,false);assert.equal(a.prompts.length,0);
  const b=boot({copy:async()=>{throw new Error("blocked")}});
  b.fields.problem.value="SECRET";
  await b.actions["share-link"]();
  assert.equal(b.prompts[0][1],url);assert.ok(!JSON.stringify(b.prompts).includes("SECRET"));
});
test("without native share the clipboard receives only the URL",async()=>{
  const copied=[],p=boot({copy:async value=>copied.push(value)});
  p.fields.evidence.value="CONFIDENTIAL";
  await p.actions["share-link"]();
  assert.deepEqual(copied,[url]);assert.match(p.status.textContent,/worksheet was not shared/i);
});
