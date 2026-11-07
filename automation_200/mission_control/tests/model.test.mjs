import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { test } from "node:test";
import { dashboardModel, filterTasks, GITHUB, HEALTH, loadLive, pingPaths, REGISTRY, registryModel, STATE, trackerModel } from "../dist/model.mjs";

const commit = "a".repeat(40);
const id = "9b4a1726-f1c7-4efd-bcea-dba621ef87b0";
const fixture = {
  schema: "CF200.1",
  target: 200,
  completed: 1,
  tasks: Array.from({ length: 200 }, (_, index) => ({
    id: "CF-" + String(index + 1).padStart(3, "0"),
    title: index === 0 ? "Validate the ping command" : "Planned work",
    stream: index === 0 ? "chat_command" : "receipt",
    status: index === 0 ? "verified" : "planned",
    evidence: index === 0 ? "Synthetic verification" : null,
    depends_on: index === 0 ? [] : ["CF-001"],
    physical_hp_required: false,
  })),
};
const state = {
  schema: "cf0.public_continuity.v1",
  cf200: { verified: 1, target: 200, last_numbered_checkpoint: 1 },
  hp: { public_ping_request_id: id },
};
const request = { action: "ping", args: {}, expires: 7201, id, issued: 1, v: 1 };
const receipt = {
  id,
  request_sha256: createHash("sha256").update(JSON.stringify(request)).digest("hex"),
  status: "completed",
  result: { pong: true, protocol: 1 },
  v: 1,
};
const tracker = {
  schema: "cf0.ai_tracker.status.v1",
  phase: "scheduled_public_issue_monitor",
  issue_url: GITHUB + "/issues/16",
  updated_utc: "2026-11-07T10:45:00+00:00",
  public_comments_observed: 2,
  external_responses_verified: 1,
  independent_contributions_verified: 0,
  comment_scan_complete: true,
  last_check_event: "push",
  last_check_run_url: GITHUB + "/actions/runs/123",
  last_scheduled_run_url: "https://example.org/actions/runs/122",
};

test("counts verified work orders and searches titles, IDs, and streams", () => {
  const { verified, tasks } = registryModel(fixture);
  assert.equal(verified, 1);
  assert.equal(filterTasks(tasks, "planned", "RECEIPT").length, 199);
  assert.deepEqual(filterTasks(tasks, "verified", "CF-001 CHAT ping").map(task => task.id), ["CF-001"]);
  assert.equal(filterTasks(tasks, "planned", "CF-001").length, 0);
});

test("rejects count drift and duplicate IDs", () => {
  assert.throws(() => registryModel({ ...fixture, completed: 2 }), /Conflicting/);
  const tasks = [...fixture.tasks];
  tasks[1] = tasks[0];
  assert.throws(() => registryModel({ ...fixture, tasks }), /Invalid work order ID/);
});

test("distinguishes matched public ping evidence from invalid results or unsafe paths", async () => {
  const data = { commit, registry: fixture, state, ping: { request, receipt }, health: "not_published" };
  const model = await dashboardModel(data);
  assert.equal(model.ping, "matched");
  assert.equal(model.health, "not_published");
  const bad = { ...data, ping: { request, receipt: { ...receipt, request_sha256: "0".repeat(64) } } };
  assert.equal((await dashboardModel(bad)).ping, "unconfirmed");
  assert.equal(pingPaths({ hp: { public_ping_request_id: "../malicious" } }), null);
});

test("checks a v2 ping response digest and rejects a missing or altered digest", async () => {
  const data = { commit, registry: fixture, state, health: "not_published" };
  const current = {
    ...receipt,
    v: 2,
    result: { protocol: 1, pong: true },
    response_sha256: createHash("sha256").update(JSON.stringify(receipt.result)).digest("hex"),
  };
  assert.equal((await dashboardModel({ ...data, ping: { request, receipt: current } })).ping, "matched");
  for (const invalid of [{ ...current, response_sha256: "0".repeat(64) }, { ...receipt, v: 2 }]) {
    assert.equal((await dashboardModel({ ...data, ping: { request, receipt: invalid } })).ping, "unconfirmed");
  }
});

test("keeps registry progress when the dated checkpoint summary drifts", async () => {
  const oldState = { ...state, cf200: { ...state.cf200, verified: 0 } };
  const model = await dashboardModel({ commit, registry: fixture, state: oldState, health: "unavailable" });
  assert.equal(model.verified, 1);
  assert.equal(model.checkpoint, null);
  assert.equal(model.ping, "unavailable");
});

test("fetches evidence at one immutable commit and separates 404 from unavailable", async () => {
  const paths = pingPaths(state);
  const documents = new Map([[REGISTRY, fixture], [STATE, state], [paths.inbox, request], [paths.receipt, receipt]]);
  const requested = [];
  const reply = (body, status = 200) => new Response(JSON.stringify(body), { status });
  const github = async (url, options) => {
    assert.equal(options.credentials, "omit");
    requested.push(url);
    if (url.endsWith("/git/ref/heads/main")) return reply({ ref: "refs/heads/main", object: { sha: commit, type: "commit" } });
    const [, file] = url.split("/" + commit + "/");
    if (file === HEALTH) return reply(null, 404);
    return reply(documents.get(file));
  };
  const model = await loadLive(github);
  assert.equal(model.commit, commit);
  assert.equal(model.health, "not_published");
  assert.equal(model.ping, "matched");
  assert.equal(requested.length, 6);
  assert.ok(requested.slice(1).every(url => url.includes("/" + commit + "/")));
  const blocked = (url, options) => url.endsWith(HEALTH) ? reply(null, 503) : github(url, options);
  assert.equal((await loadLive(blocked)).health, "unavailable");
  await assert.rejects(loadLive(async () => reply(null, 403)), /unavailable/);
});

test("reads tracker scan provenance and keeps workflow links on the CF-0 repository", () => {
  assert.deepEqual(trackerModel(tracker), {
    checkedAt: Date.parse(tracker.updated_utc),
    comments: 2, nonOwnerComments: 1, contributions: 0, complete: true, event: "push",
    runUrl: tracker.last_check_run_url, scheduledRunUrl: null,
  });
  const partial = { ...tracker, comment_scan_complete: false, last_scheduled_run_url: GITHUB + "/actions/runs/122" };
  assert.equal(trackerModel(partial).complete, false);
  assert.equal(trackerModel(partial).scheduledRunUrl, partial.last_scheduled_run_url);
  const legacy = { ...tracker, last_check_run_url: null, comment_scan_complete: undefined, monitor_code_test_run: tracker.last_check_run_url };
  assert.equal(trackerModel(legacy).complete, null);
  assert.equal(trackerModel(legacy).runUrl, legacy.monitor_code_test_run);
});

test("keeps static or contradictory tracker counts out of the dashboard", () => {
  for (const invalid of [
    null,
    { ...tracker, phase: "development", updated_utc: "2026-11-07" },
    { ...tracker, public_comments_observed: 0, external_responses_verified: 1 },
    { ...tracker, issue_url: GITHUB + "/issues/17" },
  ]) {
    assert.equal(trackerModel(invalid), null);
  }
});
