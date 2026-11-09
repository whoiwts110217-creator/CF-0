// CF-EXP-GAME-LEARN-001 alternative development rubric checks.
// Technical consistency only: does NOT score people, validate items or prove learning.
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { MISSIONS } from "../dist/gameful.mjs";

const read = name => readFileSync(new URL(name, import.meta.url), "utf8");
const rubric = JSON.parse(read("../../../research/gameful_learning/ASSESSMENT_RUBRIC_DRAFT_V0_3.json"));
const worksheet = read("../../../research/gameful_learning/ASSESSMENT_WORKSHEET_DRAFT_V0_3.md");
const review = read("../../../research/gameful_learning/ASSESSMENT_SCORING_REVIEW_V0_3.md");
const older1 = JSON.parse(read("../../../research/gameful_learning/ASSESSMENT_KEY_DRAFT_V0_1.json"));
const older2 = JSON.parse(read("../../../research/gameful_learning/ASSESSMENT_KEY_DRAFT_V0_2.json"));

test("constructed-response design is development-only, original versions preserved", () => {
  assert.equal(rubric.schema, "cf0.gameful_learning_constructed_response_draft.v0.3");
  assert.equal(rubric.continuity_id, older1.continuity_id);
  assert.equal(rubric.continuity_id, older2.continuity_id);
  assert.deepEqual(rubric.parent_ids, older2.parent_ids);
  assert.equal(older1.items.length, 12);
  assert.equal(older2.items.length, 12);
  assert.equal(rubric.status, "public_development_candidate_not_validated");
  assert.equal(rubric.study_active, false);
  assert.equal(rubric.response_collection, false);
  assert.equal(rubric.randomized, false);
  assert.equal(rubric.no_automated_scoring, true);
  assert.match(worksheet, /NOT AN ACTIVE RESEARCH STUDY/);
  assert.match(review, /NOT INDEPENDENTLY REVIEWED/);
  assert.match(review, /No data collected/);
});

test("12 scenario prompts have two independently anchored scoring facets", () => {
  const topics = MISSIONS.map(x => x.id).sort();
  assert.deepEqual(rubric.intended_waves, ["baseline", "immediate", "delayed"]);
  assert.equal(rubric.items.length, 12);
  const ids = new Set();
  for (const it of rubric.items) {
    assert.ok(!ids.has(it.id), "Unique item ID "+it.id);
    ids.add(it.id);
    assert.ok(it.scenario.length >= 100 && it.scenario.length <= 280, "Readable scenario length "+it.id);
    assert.ok(!it.scenario.includes("?"), "Scenario must not give a binary forced-choice "+it.id);
    assert.ok(it.scenario.endsWith("."));
    assert.ok(it.reference_conclusion.length >= 40);
    assert.ok(it.reference_reason.length >= 50);
    assert.ok(it.facet_conclusion_accept.length >= 1);
    assert.ok(it.facet_evidence_accept.length >= 1);
    assert.ok(it.common_invalid_claims.length >= 1);
    assert.equal(worksheet.split("### "+it.id+"\n").length-1, 1, "Worksheet must show prompt exactly once "+it.id);
    assert.ok(worksheet.includes(it.scenario), "Exact worksheet/source parity "+it.id);
    assert.ok(rubric.source_refs[it.topic], "Source path "+it.topic);
    assert.ok(MISSIONS.some(m => m.id === it.topic));
    assert.ok(!rubric.items.some(other => other !== it && other.scenario === it.scenario), "No exact duplicate scenario");
  }
  for (const [wave, prefix] of [["baseline","B3"],["immediate","I3"],["delayed","D3"]]) {
    const items = rubric.items.filter(it => it.wave === wave);
    assert.equal(items.length, 4, "four items per wave");
    assert.ok(items.every(it => it.id.startsWith(prefix+"-")));
    assert.deepEqual(items.map(it => it.topic).sort(), topics);
  }
});

test("new 0–8 scale is transparent and not misrepresented as calibrated", () => {
  const s = rubric.scoring;
  assert.equal(s.item_min,0);assert.equal(s.item_max,2);
  assert.equal(s.wave_min,0);assert.equal(s.wave_max,8);
  assert.match(s.facet_conclusion,/one point/);
  assert.match(s.facet_evidence,/one point/);
  assert.match(s.missing,/not_scored/);
  assert.match(s.double_rating,/two independent/);
  assert.match(s.key_visibility,/PUBLIC/);
  for (const [conclusion, evidence, expected] of [[false,false,0],[true,false,1],[false,true,1],[true,true,2]]) {
    // Numeric arithmetic of TWO externally human-applied facet decisions,
    // NOT an automatic classifier of natural-language responses.
    assert.equal(Number(conclusion)+Number(evidence),expected);
  }
  assert.match(worksheet,/0–8 points/);
  assert.match(review,/equal item difficulty/i);
  assert.match(review,/human raters/);
  assert.match(review,/private, version-locked/);
});

test("no study execution or personal-data capture introduced by drafts", () => {
  assert.match(worksheet,/No participation, consent, randomization, response collection/);
  assert.match(worksheet,/no computer tool or AI should automatically grade/i);
  assert.match(review,/No such interview has happened/);
  for (const data of [worksheet,review,JSON.stringify(rubric)]) {
    for(const banned of ["localStorage.","sessionStorage.","sendBeacon(","fetch(","new WebSocket","api_key","access_token"]) {
      assert.equal(data.includes(banned),false,"No network, tracking or private credentials in artifact: "+banned);
    }
  }
});
