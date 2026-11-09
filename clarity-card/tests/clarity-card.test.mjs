import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext, Script } from "node:vm";

const html=readFileSync(new URL("../index.html",import.meta.url),"utf8");

test("Clarity Card is a complete, no-paywall local worksheet with public-safe support",()=>{
  const ids=["problem","guess","hypothesis","evidence","alternative","action","criterion"];
  for(const id of ids)assert.match(html,new RegExp('id="'+id+'"'));
  for(const id of ["clarity-form","card-preview","example","download","copy","print","status"])assert.match(html,new RegExp('id="'+id+'"'));
  assert.match(html,/name="viewport"/);
  assert.match(html,/href="\.\.\/first-drop\/"/);
  assert.match(html,/href="https:\/\/cash\.app\/\$LAZYBLACKBEAN"/);
  assert.match(html,/voluntarily support/);
  assert.match(html,/not<\/strong> a required price/);
  assert.match(html,/No sign-in/);
  assert.match(html,/does not send, save, or track responses/);
  assert.match(html,/max-width:760px/);
  assert.match(html,/@media print/);
  const idsAll=[...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
  assert.equal(new Set(idsAll).size,idsAll.length,"No duplicate IDs");
  assert.doesNotMatch(html,/<form[^>]+action=/i,"No external form submit");
  assert.doesNotMatch(html,/(?:fetch\s*\(|XMLHttpRequest|localStorage|sessionStorage|document\.cookie|sendBeacon|<iframe|<script[^>]+src=)/,"No tracking, persistence, or requests");
  assert.match(html,/No account or project state|not professional|no financial return/i);
});

test("Clarity Card actual inline code parses and safely renders, copies, and exports",async()=>{
  const script=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
  assert.ok(script?.length>1000);
  new Script(script,{filename:"clarity-card-inline.js"});
  class FakeElement{
    constructor(id){this.id=id;this.value="";this.textContent="";this.listeners={};this.focusCount=0;}
    addEventListener(type,fn){this.listeners[type]=fn;}
    click(){return this.listeners.click?.()}
    focus(){this.focusCount++}
  }
  const fields=["problem","guess","hypothesis","evidence","alternative","action","criterion"];
  const elements=new Map([...fields,"clarity-form","card-preview","status","example","download","copy","print"].map(id=>[id,new FakeElement(id)]));
  let copied="",printed=0,downloads=0,revoked=0;
  const doc={
    getElementById:id=>elements.get(id),
    createElement:tag=>{assert.equal(tag,"a");return {href:"",download:"",click(){downloads++},remove(){}};},
    body:{appendChild(){}}
  };
  const context={
    document:doc,Blob,URL:{createObjectURL:()=> "blob:test",revokeObjectURL:()=>revoked++},
    navigator:{clipboard:{writeText:async v=>{copied=v}}},
    window:{print:()=>printed++},
    requestAnimationFrame:cb=>cb(),
    setTimeout:cb=>cb()
  };
  runInNewContext(script,context,{timeout:1000});
  const preview=elements.get("card-preview");
  assert.match(preview.textContent,/Question:\n\(not recorded\)/);
  assert.match(preview.textContent,/STATUS: Draft worksheet/);
  elements.get("problem").value="Can strangers explain the site?";
  elements.get("problem").listeners.input();
  assert.match(preview.textContent,/Can strangers explain the site/);
  elements.get("example").click();
  assert.match(preview.textContent,/at least 2 of 3 consenting volunteers/);
  assert.match(preview.textContent,/Not collected yet/);
  assert.equal(elements.get("problem").focusCount,1);
  elements.get("copy").click();
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(copied,preview.textContent);
  elements.get("download").click();
  assert.equal(downloads,1);
  assert.equal(revoked,1);
  elements.get("print").click();
  assert.equal(printed,1);
  for(const f of fields)elements.get(f).value="";
  elements.get("clarity-form").listeners.reset();
  assert.match(preview.textContent,/not recorded/);
  assert.match(elements.get("status").textContent,/cleared/);
});

test("Navigation and multilingual homepage show the real free deliverable",()=>{
  const home=readFileSync(new URL("../../index.html",import.meta.url),"utf8");
  const first=readFileSync(new URL("../../first-drop/index.html",import.meta.url),"utf8");
  const translations=readFileSync(new URL("../../i18n/home.mjs",import.meta.url),"utf8");
  const sitemap=readFileSync(new URL("../../sitemap.xml",import.meta.url),"utf8");
  assert.match(home,/href="\.\/clarity-card\/">Build a free Clarity Card/);
  assert.match(first,/href="\.\.\/clarity-card\/">Use the free Clarity Card/);
  assert.match(translations,/"Build a free Clarity Card":/);
  assert.match(translations,/"es": "Crear una tarjeta/);
  assert.match(translations,/"fr": "Créer une fiche/);
  assert.match(translations,/"pt": "Criar um cartão/);
  assert.match(sitemap,/\/CF-0\/clarity-card\//);
});
