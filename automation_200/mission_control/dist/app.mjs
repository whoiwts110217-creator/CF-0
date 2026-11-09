import { dashboardModel, filterTasks, GITHUB, HEALTH, loadLive, REPO, REGISTRY, TRACKER, trackerModel } from "./model.mjs";
import { taskAccess, contractTools, summarizeAccess } from "./access.mjs";
import { parseLocalDecision, parseLocalFocus, localTaskEvidence, localFocusSummary } from "./runtime.mjs";
import { loadWatchdog } from "./watchdog.mjs";

const byId = id => document.getElementById(id);
const refresh = byId("refresh");
const search = byId("search");
const filter = byId("filter");
const showRestricted = byId("show-restricted");
const localDecisionFile = byId("local-decision-file");
const localFocusFile = byId("local-focus-file");
const previous = byId("previous");
const next = byId("next");
const pageSize = 8;
const githubEvidence = /https:\/\/github\.com\/whoiwts110217-creator\/CF-0\/(?:actions\/runs\/\d+|commit\/[a-f0-9]{7,40})\b/g;
const checkedTime = new Intl.DateTimeFormat("en-US", {
  timeZone: "America/New_York", month: "short", day: "numeric",
  hour: "numeric", minute: "2-digit", timeZoneName: "short",
});
let page = 0;
let current;
let source = "snapshot";
let localDecision = null;
let localFocus = null;

function badge(id, text, tone) {
  const element = byId(id);
  element.textContent = text;
  element.dataset.tone = tone;
}

function appendEvidence(container, evidence) {
  let offset = 0;
  for (const match of evidence.matchAll(githubEvidence)) {
    container.append(evidence.slice(offset, match.index));
    const link = document.createElement("a");
    link.href = match[0];
    link.textContent = match[0].includes("/actions/runs/") ? "CI run" : "GitHub commit";
    container.append(link);
    offset = match.index + match[0].length;
  }
  container.append(evidence.slice(offset));
}

function taskRow(task, access) {
  const local = localTaskEvidence(task.id, localDecision, localFocus);
  const row = document.createElement("tr");
  const id = row.insertCell();
  id.className = "task-id";
  id.textContent = task.id;
  const details = document.createElement("details");
  const summary = document.createElement("summary");
  summary.textContent = task.title;
  const info = document.createElement("p");
  info.className = "task-info";
  info.textContent = [
    task.stream.replaceAll("_", " "),
    task.depends_on.length ? "Depends on " + task.depends_on.join(", ") : "No dependencies",
    task.physical_hp_required ? "Requires evidence from the physical HP" : "",
    "Source authority label: " + (task.authority || "unspecified") + " (not live execution authorization)",
    "Access gate: " + access.label,
    ...local.notes.map(note => "LOCAL FILE (not authenticated): " + note),
  ].filter(Boolean).join("\n");
  info.append("\n");
  appendEvidence(info, task.evidence || "Evidence pending");
  details.append(summary, info);
  row.insertCell().append(details);
  const status = document.createElement("span");
  status.className = "badge";
  status.dataset.tone = task.status === "verified" ? "mint" : "muted";
  status.textContent = task.status === "verified" ? "Verified" : "Planned";
  row.insertCell().append(status);
  const accessCell = row.insertCell();
  const accessLabel = document.createElement("span");
  accessLabel.className = "badge";
  accessLabel.dataset.tone = access.restricted ? "amber" : "muted";
  accessLabel.textContent = access.label;
  const power = document.createElement("small");
  power.className = "access-power";
  power.textContent = access.power;
  accessCell.append(accessLabel, power);
  if (local.notes.length) {
    const details = document.createElement("small");
    details.className = "access-power";
    details.textContent = local.notes.join(" · ");
    accessCell.append(details);
  }
  return row;
}

function renderTasks() {
  if (!current) return;
  const counts = summarizeAccess(current.tasks);
  const statuses = new Map(current.tasks.map(task => [task.id, task.status]));
  const allMatches = filterTasks(current.tasks, filter.value, search.value);
  const matches = showRestricted.checked ? allMatches : allMatches.filter(task =>
    !taskAccess(task, statuses).restricted && !localTaskEvidence(task.id, localDecision, localFocus).localHold);
  const hidden = allMatches.length - matches.length;
  byId("restriction-summary").textContent =
    counts.verified + " verified · " + counts.source_candidate + " source candidates · " +
    (current.tasks.length - counts.verified - counts.source_candidate) + " held by access or dependencies." +
    (hidden ? " " + hidden + " restricted task(s) hidden by this filter." : "") +
    " Public classifications are source-only; imported local holds are separately labeled and never grant execution.";
  const total = matches.length;
  const pages = Math.max(1, Math.ceil(total / pageSize));
  page = Math.max(0, Math.min(page, pages - 1));
  const start = page * pageSize;
  const tasks = byId("tasks");
  tasks.replaceChildren(...matches.slice(start, start + pageSize).map(task => taskRow(task, taskAccess(task, statuses))));
  if (!total) {
    const cell = tasks.insertRow().insertCell();
    cell.colSpan = 4;
    cell.className = "empty";
    cell.textContent = "No work orders match these filters.";
  }
  byId("results").textContent = total ? (start + 1) + "–" + Math.min(start + pageSize, total) + " of " + total : "0 results";
  previous.disabled = page === 0;
  next.disabled = page + 1 >= pages;
}

function renderLocalEvidence() {
  byId("local-decision-status").textContent = localDecision
    ? "Imported local proposal: " + localDecision.selected.length + " source-work candidate(s), " +
      localDecision.heldTotal + " reported holds (" + localDecision.sampledHolds +
      " identified by task ID). Unverified local file; no source commit attestation."
    : "Not connected — no local decision report selected.";
  byId("local-focus-status").textContent = localFocusSummary(localFocus);
}

function renderTools() {
  if (!current) return;
  const tools = contractTools(current.contract);
  const rows = byId("tool-catalog");
  if (tools === null) {
    const row = document.createElement("tr");
    const cell = row.insertCell();
    cell.colSpan = 3;
    cell.className = "empty";
    cell.textContent = "Capability contract unavailable in this source snapshot. Open the linked contract on GitHub.";
    rows.replaceChildren(row);
    byId("tool-summary").textContent = "Cannot verify the tool inventory from the loaded source.";
    return;
  }
  const shown = tools.filter(tool => showRestricted.checked || !tool.restricted);
  const rendered = shown.map(tool => {
    const row = document.createElement("tr");
    const name = row.insertCell();
    name.textContent = tool.name;
    row.insertCell().textContent = tool.power;
    const statusCell = row.insertCell();
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.dataset.tone = tool.restricted ? "amber" : "muted";
    badge.textContent = tool.status === "active_source" ? "Source-present" : "Restricted · " + tool.status;
    const note = document.createElement("small");
    note.className = "access-power";
    note.textContent = tool.note;
    statusCell.append(badge, note);
    return row;
  });
  rows.replaceChildren(...rendered);
  byId("tool-summary").textContent = tools.length + " capability records from the public contract · " +
    tools.filter(tool => tool.restricted).length + " restricted/regressed" +
    (shown.length !== tools.length ? " · " + (tools.length - shown.length) + " hidden" : "") +
    ". Source-present does not establish HP deployment, unattended execution or financial permission.";
}

const healthBadges = {
  not_published: ["Not published", "amber"],
  available: ["Public report present", "muted"],
  invalid: ["Unreadable report", "amber"],
  unavailable: ["Unavailable", "muted"],
};

function render(model, mode) {
  if (current && current.commit !== model.commit) {
    localDecision = null;
    localFocus = null;
    localDecisionFile.value = "";
    localFocusFile.value = "";
    byId("local-import-status").textContent = "Source commit changed: previous local overlays cleared. Reimport only matching private records.";
  }
  current = model;
  source = mode;
  const { commit, target, verified, checkpoint, ping, receiptPath, health } = model;
  const pinned = GITHUB + "/blob/" + commit + "/";
  const commitLink = byId("source-commit");
  commitLink.textContent = commit.slice(0, 8);
  commitLink.href = GITHUB + "/commit/" + commit;
  commitLink.title = commit;
  byId("registry-link").href = pinned + REGISTRY;
  byId("verified").textContent = verified;
  byId("target").textContent = target;
  byId("planned").textContent = (target - verified) + " planned";
  byId("checkpoint").textContent = checkpoint
    ? "Last checkpoint " + String(checkpoint).padStart(3, "0") : "Checkpoint summary unavailable";
  const progress = byId("progress");
  progress.max = target;
  progress.value = verified;
  badge("percent", new Intl.NumberFormat("en-US", { style: "percent", maximumFractionDigits: 1 }).format(verified / target) + " verified", "mint");

  const pingLink = byId("ping-link");
  pingLink.href = receiptPath ? pinned + receiptPath : pinned + "docs/PROJECT_STATUS.md";
  pingLink.setAttribute("aria-label", receiptPath ? "Matched public ping receipt" : "Public status source");
  if (ping === "matched") badge("ping-badge", "Receipt matched", "mint");
  else badge("ping-badge", ping === "unconfirmed" ? "Unconfirmed" : "Unavailable", "muted");
  badge("health-badge", ...healthBadges[health]);
  const healthLink = byId("health-link");
  healthLink.hidden = health !== "available";
  if (health === "available") healthLink.href = pinned + HEALTH;
  else healthLink.removeAttribute("href");

  badge("source-badge", mode === "github" ? "GitHub main" : "Bundled snapshot", mode === "github" ? "mint" : "muted");
  search.disabled = false;
  filter.disabled = false;
  showRestricted.disabled = false;
  renderTasks();
  renderTools();
  renderLocalEvidence();
}

async function refreshFromGitHub() {
  refresh.disabled = true;
  byId("source-status").textContent = "Checking the current GitHub commit…";
  try {
    render(await loadLive(), "github");
    byId("source-status").textContent = "Checked " + checkedTime.format(new Date()) + ". Evidence is pinned to this commit.";
  } catch {
    if (current) {
      if (source === "github") badge("source-badge", "Last GitHub read", "amber");
      byId("source-status").textContent = "GitHub refresh unavailable. Showing the evidence already loaded.";
    } else {
      badge("source-badge", "Source unavailable", "amber");
      byId("source-status").textContent = "Try refreshing or open the mission board on GitHub.";
    }
  } finally {
    refresh.disabled = false;
  }
}

const aiTrackerStatusURL = "https://raw.githubusercontent.com/" + REPO + "/main/" + TRACKER;
const trackerEvents = { push: "Push-triggered scan", schedule: "Scheduled scan", workflow_dispatch: "Manual scan" };

function renderAITracker(tracker) {
  byId("ai-comments").textContent = tracker?.comments ?? "—";
  byId("ai-replies").textContent = tracker?.nonOwnerComments ?? "—";
  byId("ai-contributions").textContent = tracker?.contributions ?? "—";
  for (const [id, url] of [["ai-run", tracker?.runUrl], ["ai-scheduled-run", tracker?.scheduledRunUrl]]) {
    const link = byId(id);
    link.hidden = !url;
    if (url) link.href = url;
    else link.removeAttribute("href");
  }
  if (!tracker) {
    badge("ai-tracker-badge", "Status unavailable", "amber");
    byId("ai-status-note").textContent = "A current public scan could not be loaded.";
    return;
  }
  const label = tracker.complete === false ? "Partial scan" : trackerEvents[tracker.event] ?? "Public issue scan";
  badge("ai-tracker-badge", label, tracker.complete === false ? "amber" : "mint");
  const scope = tracker.complete === false ? " This scan reached its comment limit." : "";
  byId("ai-status-note").textContent = "Issue #16 checked " + checkedTime.format(tracker.checkedAt) + "." + scope;
}

async function refreshCloudWatchdog() {
  try {
    const run = await loadWatchdog();
    const state = run.status === "completed"
      ? run.conclusion === "success" ? ["Passed · cloud", "mint"] : ["Not passed · cloud", "amber"]
      : ["Running / queued · cloud", "muted"];
    badge("watchdog-badge", ...state);
    const link = byId("watchdog-link");
    link.hidden = false;
    link.href = run.link;
    const kind = run.event === "schedule" ? "scheduled" : run.event === "push" ? "push-triggered" : "manual";
    byId("watchdog-note").textContent =
      "Last " + kind + " cloud run " + checkedTime.format(run.createdAt) +
      " · commit " + run.commit.slice(0, 8) +
      ". This does not prove an HP task ran or that ChatGPT continued autonomously.";
  } catch {
    badge("watchdog-badge", "Unavailable", "amber");
    byId("watchdog-link").hidden = true;
    byId("watchdog-link").removeAttribute("href");
    byId("watchdog-note").textContent =
      "Cloud watchdog metadata unavailable. No conclusion about the HP or scheduled tasks can be drawn.";
  }
}

async function refreshAITracker() {
  try {
    const response = await fetch(aiTrackerStatusURL + "?checked=" + Date.now(), {
      cache: "no-store", credentials: "omit", redirect: "error", signal: AbortSignal.timeout(7000),
    });
    if (!response.ok) throw new Error("Public tracker status unavailable");
    renderAITracker(trackerModel(await response.json()));
  } catch {
    renderAITracker(null);
  }
}

async function start() {
  try {
    const response = await fetch("./snapshot.json", { signal: AbortSignal.timeout(3000) });
    if (response.ok) render(await dashboardModel(await response.json()), "snapshot");
  } catch {
    // A missing fallback does not block the current GitHub read.
  }
  await Promise.all([refreshFromGitHub(), refreshAITracker(), refreshCloudWatchdog()]);
}

async function importLocalFile(input, parse, key) {
  if (!current || !input.files?.[0]) return;
  const file = input.files[0];
  // No upload or permanent browser storage: read from the selected File in memory.
  try {
    if (file.size > 65536) throw new Error("file_too_large");
    const parsed = parse(JSON.parse(await file.text()), current.tasks);
    if (key === "decision") localDecision = parsed;
    else localFocus = parsed;
    byId("local-import-status").textContent = "Local " + key + " file parsed in this browser only. Not authenticated; no upload or action executed.";
  } catch {
    if (key === "decision") localDecision = null;
    else localFocus = null;
    byId("local-import-status").textContent = "Local " + key + " file rejected. Verify its schema and task IDs against the current registry.";
  }
  page = 0;
  renderTasks();
  renderLocalEvidence();
}

localDecisionFile.addEventListener("change", () => importLocalFile(localDecisionFile, parseLocalDecision, "decision"));
localFocusFile.addEventListener("change", () => importLocalFile(localFocusFile, parseLocalFocus, "focus"));
byId("clear-local-evidence").addEventListener("click", () => {
  localDecision = null;
  localFocus = null;
  localDecisionFile.value = "";
  localFocusFile.value = "";
  byId("local-import-status").textContent = "Local overlays cleared from this view.";
  page = 0;
  renderTasks();
  renderLocalEvidence();
});

search.addEventListener("input", () => { page = 0; renderTasks(); });
filter.addEventListener("change", () => { page = 0; renderTasks(); });
showRestricted.addEventListener("change", () => { page = 0; renderTasks(); renderTools(); });
previous.addEventListener("click", () => { page--; renderTasks(); });
next.addEventListener("click", () => { page++; renderTasks(); });
refresh.addEventListener("click", () => { refreshFromGitHub(); refreshAITracker(); refreshCloudWatchdog(); });
start();
