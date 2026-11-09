// CF-EXP-GAME-LEARN-001 v0.2 candidate checks: source parity, NOT psychometric validation.
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { MISSIONS } from "../dist/gameful.mjs";

const read = path => readFileSync(new URL(path, import.meta.url), "utf8");
const key = JSON.parse(read("../../../research/gameful_learning/ASSESSMENT_KEY_DRAFT_V0_2.json"));
const sheet = read("../../../research/gameful_learning/ASSESSMENT_WORKSHEET_DRAFT_V0_2.md");
const review = read("../../../research/gameful_learning/ASSESSMENT_ITEM_REVIEW_2026-11-09.md");
const original = JSON.parse(read("../../../research/gameful_learning/ASSESSMENT_KEY_DRAFT_V0_1.json"));

test("v0.2 is a versioned, public draft, with the v0.1 baseline preserved", () => {
  assert.equal(key.schema, "cf0.gameful_learning_assessment_draft.v2");
  assert.equal(key.continuity_id, original.continuity_id);
  assert.deepEqual(key.parent_ids, original.parent_ids);
  assert.equal(key.supersedes_candidate, "research/gameful_learning/ASSESSMENT_KEY_DRAFT_V0_1.json");
  assert.equal(key.status, "replacement_candidate_not_validated");
  assert.equal(key.study_active, false);
  assert.equal(key.no_collection, true);
  assert.equal(original.schema, "cf0.gameful_learning_assessment_draft.v1");
  assert.equal(original.items.length, 12);
  assert.match(sheet, /NOT a live study/);
  assert.match(sheet, /public key compromises blinded use/);
  assert.match(sheet, /stores or submits nothing/);
  assert.match(review, /Not an external blind peer review/);
  assert.match(review, /A1\. Mixed response grammar/);
  assert.match(review, /A8\. No authorized study execution/);
});

test("all revised statements are declarative, uniquely keyed, and reproducible", () => {
  assert.equal(key.items.length, 12);
  const ids = new Set();
  const missionTopics = MISSIONS.map(x => x.id).sort();
  const answerPatterns = [];
  for (const item of key.items) {
    assert.ok(!ids.has(item.id), "Duplicate ID " + item.id);
    ids.add(item.id);
    assert.ok(item.statement.length >= 90 && item.statement.length <= 250, "Statement length "+item.id);
    assert.ok(item.statement.endsWith("."), "Expected declarative sentence "+item.id);
    assert.ok(!item.statement.includes("?"), "No yes/no question with TRUE/FALSE response: "+item.id);
    assert.equal(typeof item.answer, "boolean");
    assert.ok(item.reason.length >= 45, "Provide explicit reasoning: "+item.id);
    const occurrence = sheet.split("`"+item.id+"`").length-1;
    assert.equal(occurrence, 1, "Worksheet should contain item exactly once: "+item.id);
    assert.ok(sheet.includes(item.statement), "Exact statement text drift: "+item.id);
    const source = MISSIONS.find(m => m.id === item.topic);
    assert.ok(source, "Known topic: "+item.topic);
    assert.equal(key.sources[item.topic], source.sourceUrl, "Evidence link for "+item.id);
    assert.notEqual(item.statement, source.claim);
    assert.notEqual(item.statement, source.transferClaim);
  }
  for (const [phase, prefix] of [["baseline","B2"],["immediate","I2"],["delayed","D2"]]) {
    const matches = key.items.filter(x => x.phase === phase);
    assert.equal(matches.length, 4);
    assert.ok(matches.every(x => x.id.startsWith(prefix+"-")));
    assert.deepEqual(matches.map(x => x.topic).sort(), missionTopics);
    assert.equal(matches.filter(x => x.answer).length, 2);
    assert.equal(matches.filter(x => !x.answer).length, 2);
    answerPatterns.push(matches.map(x => x.answer ? "T" : "F").join(""));
  }
  assert.equal(new Set(answerPatterns).size, 3, "Avoid reusing identical known answer-key sequence");
});

test("development candidate has no data capture or account/network capabilities", () => {
  for (const raw of [sheet, review, JSON.stringify(key)]) {
    for (const banned of ["localStorage.", "sessionStorage.", "sendBeacon(", "fetch(", "new WebSocket", "api_key", "access_token"]) {
      assert.ok(!raw.includes(banned), "No collection/execution string: "+banned);
    }
  }
  assert.match(sheet, /36–60 hours/);
  assert.match(sheet, /attribution/);
  assert.match(review, /50%/);
});


test("candidate forms avoid verbatim question reuse and obvious token clones", () => {
  // A lexical smoke check only. It does not prove psychometric parallelism,
  // independent constructs, matched difficulty, or real transfer.
  const stop = new Set("a an the and or this that is are as it its by to for with of in on from one every these those has have was were be after before alone than supports against claimed claim at no not so same more then can enough".split(" "));
  const terms = value => new Set(value.toLowerCase().replace(/[^a-z0-9 ]/g," ")
    .split(/\\s+/).filter(token => token.length > 2 && !stop.has(token)));
  const overlap = (a,b) => {
    const A=terms(a),B=terms(b);
    const intersection=[...A].filter(word => B.has(word)).length;
    return intersection/(A.size+B.size-intersection);
  };
  for(const topic of MISSIONS.map(x=>x.id)){
    const items=key.items.filter(x=>x.topic===topic);
    for(let i=0;i<items.length;i++)for(let j=i+1;j<items.length;j++){
      assert.notEqual(items[i].statement,items[j].statement, "No verbatim cross-wave repeats");
      assert.ok(overlap(items[i].statement,items[j].statement) < 0.4,
        "Manual wording review warranted for "+items[i].id+" vs "+items[j].id);
    }
  }
  for(const item of key.items) {
    for(const earlier of original.items) {
      assert.notEqual(item.statement,earlier.question,"Candidate must not silently copy earlier question");
    }
  }
});
