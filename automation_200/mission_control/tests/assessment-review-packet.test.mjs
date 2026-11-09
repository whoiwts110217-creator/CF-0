// Source safety and checklist-coverage test. It does NOT constitute peer review.
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const read = name => readFileSync(new URL(name, import.meta.url), "utf8");
const packet = read("../../../research/gameful_learning/INDEPENDENT_REVIEW_PACKET_V0_3.md");
const rubric = JSON.parse(read("../../../research/gameful_learning/ASSESSMENT_RUBRIC_DRAFT_V0_3.json"));
test("external-review packet covers every exact source item once",()=>{
  assert.equal(rubric.items.length,12);
  for(const item of rubric.items) {
    const rowPrefix="| `"+item.id+"` | "+item.wave+" | "+item.topic+" |";
    assert.equal(packet.split(rowPrefix).length-1,1,"Review row missing or duplicated for "+item.id);
  }
  assert.match(packet,/Factual correctness/);
  assert.match(packet,/Construct fidelity/);
  assert.match(packet,/Two-facet separability/);
  assert.match(packet,/Acceptable alternatives/);
  assert.match(packet,/Clarity\/fairness/);
  assert.match(packet,/Form comparability/);
});
test("review requires independently verified evidence and never claims completion",()=>{
  assert.match(packet,/NO INDEPENDENT REVIEW COMPLETED OR SOLICITED/);
  assert.match(packet,/review_pending/);
  assert.match(packet,/participants_0/);
  assert.match(packet,/learning_efficacy_unverified/);
  assert.match(packet,/No external invitation or outreach was sent/);
  assert.match(packet,/not a secure blinded participant instrument/);
  assert.match(packet,/not an empirical item-difficulty estimate/);
  assert.match(packet,/two independently trained human scorers/);
});
test("review packet leaves no scoring, tracking or remote-control channel",()=>{
  const disallowed=["localStorage.","sessionStorage.","sendBeacon(","fetch(","new WebSocket","api_key","access_token","mcp__","execute_action","writeFileSync("];
  for(const word of disallowed)assert.equal(packet.includes(word),false,"Unsafe executable/credential token: "+word);
});
