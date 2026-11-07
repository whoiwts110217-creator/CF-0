import { dashboardModel, filterTasks, GITHUB, loadLive, REGISTRY } from "./model.mjs";

const byId = id => document.getElementById(id);
const refresh = byId("refresh");
const search = byId("search");
const filter = byId("filter");
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

function taskRow(task) {
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
  return row;
}

function renderTasks() {
  if (!current) return;
  const matches = filterTasks(current.tasks, filter.value, search.value);
  const total = matches.length;
  const pages = Math.max(1, Math.ceil(total / pageSize));
  page = Math.max(0, Math.min(page, pages - 1));
  const start = page * pageSize;
  const tasks = byId("tasks");
  tasks.replaceChildren(...matches.slice(start, start + pageSize).map(taskRow));
  if (!total) {
    const cell = tasks.insertRow().insertCell();
    cell.colSpan = 3;
    cell.className = "empty";
    cell.textContent = "No work orders match these filters.";
  }
  byId("results").textContent = total ? (start + 1) + "–" + Math.min(start + pageSize, total) + " of " + total : "0 results";
  previous.disabled = page === 0;
  next.disabled = page + 1 >= pages;
}

const healthBadges = {
  not_published: ["Not published", "amber"],
  available: ["Public report present", "muted"],
  invalid: ["Unreadable report", "amber"],
  unavailable: ["Unavailable", "muted"],
};

function render(model, mode) {
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

  badge("source-badge", mode === "github" ? "GitHub main" : "Bundled snapshot", mode === "github" ? "mint" : "muted");
  search.disabled = false;
  filter.disabled = false;
  renderTasks();
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

const aiTrackerStatusURL = "https://raw.githubusercontent.com/whoiwts110217-creator/CF-0/main/docs/AI_TRACKER_STATUS.json";

async function refreshAITracker() {
  try {
    const response = await fetch(aiTrackerStatusURL + "?checked=" + Date.now(), {
      cache: "no-store", signal: AbortSignal.timeout(7000),
    });
    if (!response.ok) throw new Error("Public tracker status unavailable");
    const data = await response.json();
    if (data?.schema !== "cf0.ai_tracker.status.v1") throw new Error("Unknown tracker status schema");
    for (const key of ["public_comments_observed", "external_responses_verified", "independent_contributions_verified"]) {
      if (!Number.isSafeInteger(data[key]) || data[key] < 0) throw new Error("Invalid tracker count");
    }
    const date = Date.parse(data.updated_utc);
    if (!Number.isFinite(date)) throw new Error("Missing update time");
    byId("ai-comments").textContent = data.public_comments_observed;
    byId("ai-replies").textContent = data.external_responses_verified;
    byId("ai-contributions").textContent = data.independent_contributions_verified;
    const operational = data.phase === "scheduled_public_issue_monitor";
    badge("ai-tracker-badge", operational ? "Public issue monitor" : "Development snapshot", operational ? "mint" : "amber");
    byId("ai-status-note").textContent = "Last published check: " + checkedTime.format(new Date(date)) +
      ". Source: public Issue #16 monitor. Coverage is limited to GitHub issue comments.";
  } catch {
    badge("ai-tracker-badge", "Status unavailable", "amber");
    byId("ai-status-note").textContent = "Published tracker data could not be verified. Open the evidence snapshot on GitHub.";
  }
}

async function start() {
  try {
    const response = await fetch("./snapshot.json", { signal: AbortSignal.timeout(3000) });
    if (response.ok) render(await dashboardModel(await response.json()), "snapshot");
  } catch {
    // A missing fallback does not block the current GitHub read.
  }
  await Promise.all([refreshFromGitHub(), refreshAITracker()]);
}

search.addEventListener("input", () => { page = 0; renderTasks(); });
filter.addEventListener("change", () => { page = 0; renderTasks(); });
previous.addEventListener("click", () => { page--; renderTasks(); });
next.addEventListener("click", () => { page++; renderTasks(); });
refresh.addEventListener("click", () => { refreshFromGitHub(); refreshAITracker(); });
start();
