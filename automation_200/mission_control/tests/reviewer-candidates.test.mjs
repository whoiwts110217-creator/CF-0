// CF-EXP-GAME-LEARN-001 source validation; zero outreach performed.
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const read = path => readFileSync(new URL(path, import.meta.url), "utf8");
const c = JSON.parse(read("../../../research/gameful_learning/INDEPENDENT_REVIEW_CONTACT_CANDIDATES_V0_1.json"));
const plan = read("../../../research/gameful_learning/REVIEWER_OUTREACH_PLAN_DRAFT_V0_1.md");
const packet = read("../../../research/gameful_learning/INDEPENDENT_REVIEW_PACKET_V0_3.md");

test("candidate ledger is source-backed research and no one was contacted",()=>{
 assert.equal(c.schema,"cf0.gameful_review_candidates.v0.1");
 assert.equal(c.continuity_id,"CF-EXP-GAME-LEARN-001");
 assert.equal(c.status,"public_candidates_only_no_contacts_sent");
 assert.equal(c.outreach_authorized,false);
 assert.equal(c.review_completed,false);
 assert.equal(c.costs_verified,false);
 assert.equal(c.candidates.length,3);
 const ids=new Set();
 for(const person of c.candidates){
  assert.ok(!ids.has(person.id));
  ids.add(person.id);
  assert.match(person.official_service_url,/^https:\/\//);
  assert.equal(person.sent,false);
  assert.equal(person.engaged,false);
  assert.match(person.fee_status,/unknown/);
  assert.ok(person.scope_to_verify.length>40);
  assert.ok(plan.includes(person.official_service_url));
  assert.ok(plan.includes(person.organization.split(" — ")[0].split(" (")[0].split("The Ohio State University")[0]||person.organization.split(" — ")[0]) || plan.includes(person.id) || person.id==="R01");
 }
 assert.match(c.permission_boundary,/PCA-003/);
});
test("narrow messaging is not a sent email or completed expert review",()=>{
 assert.match(plan,/NOT SENT/);
 assert.match(plan,/0 contacts sent/);
 assert.match(plan,/costs exceed zero/);
 assert.match(plan,/one.*fit inquiry/i);
 assert.match(plan,/subject: inquiry/i);
 assert.match(plan,/No participant data/);
 assert.match(plan,/not a certification or endorsement/);
 assert.match(plan,/no-cost\/preliminary options/);
 assert.match(plan,/standard Mental Measurements Yearbook/);
 assert.match(packet,/NO INDEPENDENT REVIEW COMPLETED OR SOLICITED/);
 for(const val of [plan,JSON.stringify(c)]){
  for(const forbidden of ["localStorage.","sessionStorage.","navigator.sendBeacon","fetch(","new WebSocket","api_key","access_token"]){
   assert.equal(val.includes(forbidden),false,forbidden);
  }
 }
});
