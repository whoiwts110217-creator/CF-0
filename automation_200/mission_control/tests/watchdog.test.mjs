import assert from "node:assert/strict";
import { test } from "node:test";
import { watchdogModel, loadWatchdog, WATCHDOG_URL } from "../dist/watchdog.mjs";

const good = {
  id: 42601591734, path: ".github/workflows/cf0-channel-watchdog.yml",
  head_branch: "main", head_sha: "a".repeat(40), event: "schedule",
  status: "completed", conclusion: "success", created_at: "2026-11-09T10:32:27Z",
  repository: { full_name: "whoiwts110217-creator/CF-0" },
};

test("realistic public watchdog metadata preserves cloud/HP boundary", () => {
  const result = watchdogModel({ workflow_runs: [good] });
  assert.equal(result.status, "completed");
  assert.equal(result.conclusion, "success");
  assert.equal(result.event, "schedule");
  assert.match(result.link, /github\.com\/whoiwts110217-creator\/CF-0\/actions\/runs\/42601591734$/);
  assert.equal(result.hpIdentityAttested, false);
  assert.equal(result.taskExecuted, false);
});

test("rejects spoofed repositories, branches, workflow paths, timestamps and conclusions", () => {
  for (const patch of [
    { head_branch: "dev" }, { path: ".github/workflows/other.yml" },
    { repository: { full_name: "attacker/repo" } }, { id: -5 },
    { head_sha: "../override" }, { event: "pull_request" },
    { status: "completed", conclusion: null },
    { status: "in_progress", conclusion: "success" },
    { created_at: "invalid" }, { created_at: "2026-11-09T10:32:27-05:00" },
  ]) assert.equal(watchdogModel({ workflow_runs: [{ ...good, ...patch }] }), null);
  assert.equal(watchdogModel({ workflow_runs: [] }), null);
  assert.equal(watchdogModel({ workflow_runs: [good, good] }), null);
  assert.equal(watchdogModel(null), null);
});

test("public loader uses anonymous read-only GitHub request and validates reply", async () => {
  let called = false;
  const expected = await loadWatchdog(async (url, options) => {
    assert.equal(url, WATCHDOG_URL);
    assert.equal(options.credentials, "omit");
    assert.equal(options.redirect, "error");
    assert.equal(options.cache, "no-store");
    called = true;
    return { ok: true, json: async () => ({ workflow_runs: [good] }) };
  });
  assert.ok(called);
  assert.equal(expected.id, good.id);
  await assert.rejects(loadWatchdog(async () => ({ ok: false })), /unavailable/);
  await assert.rejects(loadWatchdog(async () => ({ ok: true, json: async () => ({ workflow_runs: [] }) })), /Invalid/);
});

test("Mission Control includes an explicit cloud-only watchdog evidence row", async () => {
  const { readFile } = await import("node:fs/promises");
  const html = await readFile(new URL("../dist/index.html", import.meta.url), "utf8");
  const app = await readFile(new URL("../dist/app.mjs", import.meta.url), "utf8");
  for (const id of ["watchdog-link", "watchdog-badge", "watchdog-note"]) {
    assert.ok(html.includes('id="' + id + '"'));
  }
  assert.match(app, /refreshCloudWatchdog/);
  assert.match(app, /does not prove an HP task ran/);
});
