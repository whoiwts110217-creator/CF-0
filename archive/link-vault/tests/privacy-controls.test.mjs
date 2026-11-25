import test from "node:test";
import assert from "node:assert/strict";
import {createRequire} from "node:module";
import {readFileSync} from "node:fs";
const require=createRequire(import.meta.url);
const {OWNED_KEYS,purgeLocalData}=require("../privacy-controls.js");

test("purge clears only Link Vault owner-private storage, not unrelated site data or public catalog",()=>{
 const data=new Map([
  ["cf_link_vault_v1",'{ "custom":[{"url":"https://example.net/private"}]}'],
  ["cf_link_vault_owner_action_checks_v1",'{ "CF-ACT-001":"checked" }'],
  ["cf_link_vault_public_catalog_v2","public safe data"],
  ["cf_link_vault_owner_action_cache_v1","public safe action view"],
  ["unrelated_other_web_app","must remain"]
 ]);
 const removed=[];
 const fake={removeItem(key){removed.push(key);data.delete(key)}};
 const cleared=purgeLocalData(fake);
 assert.deepEqual(cleared,[...OWNED_KEYS]);
 assert.deepEqual(removed,[...OWNED_KEYS]);
 assert.equal(data.has("cf_link_vault_v1"),false);
 assert.equal(data.has("cf_link_vault_owner_action_checks_v1"),false);
 assert.equal(data.get("cf_link_vault_public_catalog_v2"),"public safe data");
 assert.equal(data.get("unrelated_other_web_app"),"must remain");
});
test("purge rejects missing browser storage without claiming deletion",()=>{
 assert.throws(()=>purgeLocalData(null),/storage unavailable/i);
 assert.throws(()=>purgeLocalData({}),/storage unavailable/i);
});
test("privacy dialog presents shared-origin and plaintext-backup caveats",()=>{
 const html=readFileSync(new URL("../index.html",import.meta.url),"utf8");
 for(const id of ["privacy","privacy-dialog","privacy-clear","privacy-confirmation","privacy-status"]){
  assert.ok(html.includes('id="'+id+'"'),id);
 }
 assert.match(html,/same (?:website )?origin/i);
 assert.match(html,/not encrypted/i);
 assert.match(html,/src=".\/privacy-controls.js"/);
});
test("no broad storage.clear or network transmission in privacy reset",()=>{
 const source=readFileSync(new URL("../privacy-controls.js",import.meta.url),"utf8");
 assert.doesNotMatch(source,/localStorage\.clear\s*\(/);
 assert.doesNotMatch(source,/fetch\s*\(|XMLHttpRequest|sendBeacon/);
 assert.match(source,/input\.value!=="CLEAR"/);
});
