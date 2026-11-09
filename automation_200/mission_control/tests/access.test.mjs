import assert from "node:assert/strict";
import { test } from "node:test";
import { ACCESS_LABELS, taskAccess, summarizeAccess, contractTools } from "../dist/access.mjs";

const task = (id, stream = "receipt", extra = {}) => ({
  id, title: id, stream, status: "planned", depends_on: [],
  authority: "owner-reviewed", physical_hp_required: false, ...extra,
});

test("source-only proposals distinguish completion, dependency, HP and owner-local gates", () => {
  const tasks = [
    task("V", "receipt", { status: "verified" }),
    task("SRC"),
    task("HP", "hp_install"),
    task("DEVICE", "security", { physical_hp_required: true }),
    task("CF-042", "sidecar"),
    task("WAIT", "receipt", { depends_on: ["SRC"] }),
    task("READY", "receipt", { depends_on: ["V"] }),
  ];
  const totals = summarizeAccess(tasks);
  assert.deepEqual(totals, {
    verified: 1, source_candidate: 2, physical_hp_required: 1,
    hp_install_needs_local_review: 1, owner_local_evidence_required: 1,
    dependencies_unverified: 1,
  });
  const statuses = new Map(tasks.map(t => [t.id, t.status]));
  assert.equal(taskAccess(tasks[0], statuses).restricted, false);
  assert.equal(taskAccess(tasks[2], statuses).reason, "hp_install_needs_local_review");
  assert.equal(taskAccess(tasks[3], statuses).power, "Device-local / evidence-gated");
  assert.equal(taskAccess(tasks[4], statuses).reason, "owner_local_evidence_required");
  assert.equal(taskAccess(tasks[5], statuses).restricted, true);
  assert.equal(taskAccess(tasks[6], statuses).reason, "source_candidate");
  assert.ok(ACCESS_LABELS.source_candidate.includes("candidate"));
});

test("a source-reviewed task is never labeled as an execution permission", () => {
  const item = task("D", "public_finance");
  const result = taskAccess(item, [item]);
  assert.equal(result.reason, "source_candidate");
  assert.equal(result.power, "Financial preparation only");
  assert.equal(result.restricted, false);
});

test("capability catalog exposes historical regression without activating it", () => {
  const contract = { schema: "cf0.owner_capability_contract.v1", capabilities: [
    { id: "public_relay_ping", status: "active_source" },
    { id: "notepad_owner_launch", status: "regression_open" },
  ]};
  const rows = contractTools(contract);
  assert.equal(rows.length, 2);
  assert.deepEqual(rows.map(x => x.restricted), [false, true]);
  assert.match(rows[1].note, /not available/);
  assert.match(rows[0].power, /L1/);
  assert.equal(contractTools(null), null);
  assert.equal(contractTools({ ...contract, schema: "unknown" }), null);
  assert.equal(contractTools({ ...contract, capabilities: [...contract.capabilities, contract.capabilities[0]] }), null);
});

test("real registry source-gate counts add to 200 without changing source state", async () => {
  const fs = await import("node:fs/promises");
  const url = new URL("../../registry.json", import.meta.url);
  const registry = JSON.parse(await fs.readFile(url, "utf8"));
  const before = JSON.stringify(registry);
  const totals = summarizeAccess(registry.tasks);
  assert.equal(Object.values(totals).reduce((a, b) => a + b, 0), registry.tasks.length);
  assert.equal(totals.verified, registry.completed);
  assert.equal(before, JSON.stringify(registry));
});
