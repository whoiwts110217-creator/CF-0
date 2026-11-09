import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { test } from "node:test";
import { parseLocalDecision, parseLocalFocus, localTaskEvidence, localFocusSummary } from "../dist/runtime.mjs";

const tasks = [
  { id: "CF-001", status: "verified" },
  { id: "CF-002", status: "planned" },
  { id: "CF-003", status: "planned" },
  { id: "CF-004", status: "planned" },
];
const proposal = {
  schema: "cf200.decision_proposal.v1", read_only: true,
  execution_authorized: false, hp_identity_attested: false,
  hp_health_state: "unavailable", selected_count: 1,
  selected: [{ id: "CF-002", action: "propose_source_work_only" }],
  held_counts: { explicitly_blocked: 1 },
  held_examples: [{ id: "CF-003", reason: "explicitly_blocked" }],
};
const focus = {
  schema: "cf200.resumable_focus.v1",
  active: { task_id: "CF-002", checkpoint_ref: "PRIVATE:secret-do-not-render" },
  paused: [{ task_id: "CF-003", checkpoint_ref: "PRIVATE:another-hidden-id" }],
};

test("local decision has only bounded, labeled, unverified evidence", () => {
  const parsed = parseLocalDecision(proposal, tasks);
  assert.deepEqual(parsed.selected, ["CF-002"]);
  assert.equal(parsed.held.get("CF-003"), "explicitly_blocked");
  assert.equal(parsed.sampledHolds, 1);
  assert.equal(parsed.heldTotal, 1);
  assert.equal(parsed.attributedCommit, null);
  assert.equal(parsed.executionAuthorized, false);
  assert.equal(localTaskEvidence("CF-003", parsed, null).localHold, true);
  assert.equal(localTaskEvidence("CF-004", parsed, null).localHold, false);
  assert.match(localTaskEvidence("CF-002", parsed, null).notes[0], /not executed/);
});

test("focus parser strips sensitive checkpoint pointers while preserving pause/active IDs", () => {
  const parsed = parseLocalFocus(focus, tasks);
  assert.deepEqual(parsed.active, { id: "CF-002", hasCheckpoint: true });
  assert.deepEqual(parsed.paused, [{ id: "CF-003", hasCheckpoint: true }]);
  assert.equal(parsed.checkpointContentsRead, false);
  assert.doesNotMatch(JSON.stringify(parsed), /PRIVATE:|secret-do-not-render/);
  assert.match(localFocusSummary(parsed), /1 paused task/);
  assert.match(localTaskEvidence("CF-003", null, parsed).notes[0], /paused/);
});

test("invalid reports and unauthorized claims fail closed", () => {
  for (const value of [
    { ...proposal, execution_authorized: true },
    { ...proposal, hp_identity_attested: true },
    { ...proposal, held_examples: [{ id: "CF-001", reason: "explicitly_blocked" }] },
    { ...proposal, held_examples: [{ id: "CF-003", reason: "new_permission" }] },
    { ...proposal, held_examples: [{ id: "UNKNOWN", reason: "explicitly_blocked" }] },
    { ...proposal, held_counts: { explicitly_blocked: 0 } },
    { ...proposal, selected: [{ id: "CF-003", action: "run" }] },
    { ...proposal, selected_count: 2 },
    { ...proposal, health_state: "healthy", hp_health_state: "healthy" },
    null,
  ]) {
    assert.throws(() => parseLocalDecision(value, tasks));
  }
});

test("duplicates, invalid refs, unknown task IDs and paused-without-checkpoint fail closed", () => {
  for (const value of [
    { ...focus, paused: [{ task_id: "CF-002", checkpoint_ref: "private" }] },
    { ...focus, active: { task_id: "UNKNOWN", checkpoint_ref: null } },
    { ...focus, paused: [{ task_id: "CF-003", checkpoint_ref: null }] },
    { ...focus, active: { task_id: "CF-002", checkpoint_ref: "invalid\nref" } },
    { ...focus, active: { task_id: "CF-002", checkpoint_ref: "X".repeat(241) } },
    { ...focus, active: { task_id: "CF-002" } },
    { ...focus, schema: "unreviewed.state.v2" },
  ]) assert.throws(() => parseLocalFocus(value, tasks));
});

test("real registry current source IDs can be imported safely without mutating records", async () => {
  const registry = JSON.parse(await readFile(new URL("../../registry.json", import.meta.url), "utf8"));
  const before = JSON.stringify(registry);
  const firstPlanned = registry.tasks.find(task => task.status === "planned");
  const actual = parseLocalFocus({
    schema: focus.schema, active: { task_id: firstPlanned.id, checkpoint_ref: null }, paused: [],
  }, registry.tasks);
  assert.equal(actual.active.id, firstPlanned.id);
  assert.equal(JSON.stringify(registry), before);
});

test("static page provides explicit local-only file import, clear and status controls", async () => {
  const html = await readFile(new URL("../dist/index.html", import.meta.url), "utf8");
  const app = await readFile(new URL("../dist/app.mjs", import.meta.url), "utf8");
  for (const id of ["runtime-evidence", "local-decision-file", "local-focus-file", "clear-local-evidence", "local-import-status"]) {
    assert.ok(html.includes('id="' + id + '"'));
  }
  assert.match(app, /await file\.text\(\)/);
  assert.doesNotMatch(app, /uploadLocal|fetch\(file/);
});
