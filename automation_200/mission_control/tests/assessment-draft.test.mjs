// CF-EXP-GAME-LEARN-001 draft instrument integrity, NOT proof of learning efficacy.
// Kept under existing read-only CI to catch public instrument/key drift.
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { MISSIONS } from "../dist/gameful.mjs";

const instrument = JSON.parse(readFileSync(
  new URL("../../../research/gameful_learning/ASSESSMENT_KEY_DRAFT_V0_1.json", import.meta.url), "utf8"
));
const worksheet = readFileSync(
  new URL("../../../research/gameful_learning/ASSESSMENT_WORKSHEET_DRAFT_V0_1.md", import.meta.url), "utf8"
);

test("three-wave assessment is public draft only, never a running study", () => {
  assert.equal(instrument.schema, "cf0.gameful_learning_assessment_draft.v1");
  assert.equal(instrument.continuity_id, "CF-EXP-GAME-LEARN-001");
  assert.equal(instrument.state, "draft_not_running");
  assert.equal(instrument.no_collection, true);
  assert.match(worksheet, /NOT an active study/);
  assert.match(worksheet, /public packet makes item leakage possible/);
  assert.match(worksheet, /No response collection/);
});

test("instrument covers all four original topics in all three distinct waves", () => {
  assert.equal(instrument.items.length, 12);
  const ids = new Set();
  const topics = MISSIONS.map(x => x.id).sort();
  for (const item of instrument.items) {
    assert.ok(!ids.has(item.id), "Duplicate scenario id "+item.id);
    ids.add(item.id);
    assert.equal(typeof item.question, "string");
    assert.ok(item.question.length >= 70 && item.question.length <= 245, "Scenario must be one short question: "+item.id);
    assert.equal(typeof item.answer, "boolean");
    assert.ok(item.reason.length > 25);
    assert.ok(worksheet.includes("`"+item.id+"`"), "Missing worksheet item "+item.id);
    assert.ok(worksheet.includes(item.question), "Worksheet must match exact scenario text "+item.id);
    const source = MISSIONS.find(x => x.id === item.topic);
    assert.ok(source, "Unknown source topic "+item.topic);
    assert.equal(instrument.sources[item.topic], source.sourceUrl);
    assert.notEqual(item.question, source.claim);
    assert.notEqual(item.question, source.transferClaim);
  }
  assert.equal(ids.size, 12);
  for (const [phase, prefix] of [["baseline","B"],["immediate","I"],["delayed","D"]]) {
    const subset = instrument.items.filter(x => x.phase === phase);
    assert.equal(subset.length, 4, "Each wave has exactly four scenarios");
    assert.deepEqual(subset.map(x => x.topic).sort(), topics, "Exactly one per topic per wave");
    assert.ok(subset.every(x => x.id.startsWith(prefix+"-")));
    assert.equal(subset.filter(x => x.answer).length, 2, "Two TRUE keys per wave");
    assert.equal(subset.filter(x => !x.answer).length, 2, "Two FALSE keys per wave");
    for (const item of subset) {
      assert.equal(worksheet.split("`"+item.id+"`").length - 1, 1, "Worksheet ID must appear exactly once");
    }
  }
});

test("instrument and evaluator drafts never claim recruitment or live accounts", () => {
  assert.match(worksheet, /36–60.hour window/);
  assert.match(worksheet, /attrition separately/);
  assert.match(worksheet, /not collecting research responses/);
  for (const file of [worksheet, JSON.stringify(instrument)]) {
    assert.doesNotMatch(file, /localStorage\.|sessionStorage\.|navigator\.sendBeacon|fetch\(|new WebSocket|api_key|access_token/i);
  }
});
