// Local-only runtime evidence presentation. Never uploads, executes or authorizes.
// Parsed private checkpoint references are deliberately discarded before rendering.
const HOLD_REASONS = new Set([
  "explicitly_blocked", "task_context_future_issued", "task_context_expired",
  "physical_hp_required", "hp_install_needs_local_review",
  "owner_local_evidence_required", "dependencies_unverified",
  "retry_limit_reached", "retry_cooldown",
]);
const KNOWN_HEALTH = new Set([
  "not_published", "fresh_public_report", "reported_problem", "late", "stale",
  "future_timestamp", "invalid", "unavailable",
]);

function taskMap(tasks) {
  if (!Array.isArray(tasks) || tasks.length > 500) throw new Error("invalid_registry");
  const byId = new Map();
  for (const task of tasks) {
    if (typeof task?.id !== "string" || byId.has(task.id)) throw new Error("invalid_task_ids");
    byId.set(task.id, task);
  }
  return byId;
}

function plain(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function idFor(value, byId) {
  if (typeof value !== "string" || !byId.has(value)) throw new Error("unknown_task_id");
  return value;
}

export function parseLocalDecision(value, tasks) {
  const byId = taskMap(tasks);
  if (!plain(value) || value.schema !== "cf200.decision_proposal.v1"
      || value.read_only !== true || value.execution_authorized !== false
      || value.hp_identity_attested !== false || !Array.isArray(value.selected)
      || !Array.isArray(value.held_examples) || !plain(value.held_counts)
      || !Number.isInteger(value.selected_count)
      || value.selected_count !== value.selected.length || value.selected.length > 20
      || value.held_examples.length > 10 || !KNOWN_HEALTH.has(value.hp_health_state)) {
    throw new Error("invalid_decision_report");
  }
  const selected = [];
  const selectedSeen = new Set();
  for (const item of value.selected) {
    const id = idFor(item?.id, byId);
    if (!plain(item) || selectedSeen.has(id) || byId.get(id).status !== "planned"
        || item.action !== "propose_source_work_only") throw new Error("invalid_selected_task");
    selectedSeen.add(id);
    selected.push(id);
  }
  const held = new Map();
  for (const item of value.held_examples) {
    const id = idFor(item?.id, byId);
    if (!plain(item) || held.has(id) || selectedSeen.has(id) || !HOLD_REASONS.has(item.reason)
        || byId.get(id).status !== "planned") throw new Error("invalid_hold_record");
    held.set(id, item.reason);
  }
  let heldTotal = 0;
  for (const [key, count] of Object.entries(value.held_counts)) {
    if (!HOLD_REASONS.has(key) || !Number.isSafeInteger(count) || count < 0 || count > tasks.length) {
      throw new Error("invalid_held_counts");
    }
    heldTotal += count;
  }
  if (heldTotal > tasks.length || held.size > heldTotal) throw new Error("inconsistent_held_counts");
  // The standard report includes at most 10 held_examples. Do not claim a
  // reason for unlisted tasks or interpret proposed work as authorized.
  return {
    kind: "local_decision", selected, held, heldTotal,
    sampledHolds: held.size, health: value.hp_health_state,
    attributedCommit: null, executionAuthorized: false,
  };
}

export function parseLocalFocus(value, tasks) {
  const byId = taskMap(tasks);
  if (!plain(value) || value.schema !== "cf200.resumable_focus.v1"
      || !Object.hasOwn(value, "active") || !Array.isArray(value.paused)
      || value.paused.length > tasks.length) throw new Error("invalid_focus_state");
  const seen = new Set();
  function readItem(item, paused) {
    if (!plain(item) || Object.keys(item).sort().join(",") !== "checkpoint_ref,task_id") {
      throw new Error("invalid_focus_item");
    }
    const id = idFor(item.task_id, byId);
    if (seen.has(id)) throw new Error("duplicate_focus_task");
    seen.add(id);
    const ref = item.checkpoint_ref;
    if (ref !== null && (typeof ref !== "string" || ref.length === 0
        || ref.length > 240 || /[\x00-\x1f\x7f]/.test(ref))) {
      throw new Error("invalid_checkpoint_reference");
    }
    if (paused && ref === null) throw new Error("missing_paused_checkpoint");
    return { id, hasCheckpoint: typeof ref === "string" };
  }
  const active = value.active === null ? null : readItem(value.active, false);
  const paused = value.paused.map(item => readItem(item, true));
  // Return IDs and checkpoint-presence ONLY; never expose the original refs.
  return { kind: "local_focus", active, paused, checkpointContentsRead: false };
}

export function localTaskEvidence(taskId, decision, focus) {
  const notes = [];
  const hold = decision?.held?.get(taskId);
  if (hold) notes.push("Imported local hold: " + hold.replaceAll("_", " "));
  else if (decision?.selected?.includes(taskId)) notes.push("Imported source-work proposal (not executed)");
  if (focus?.active?.id === taskId) {
    notes.push("Local focus: active" + (focus.active.hasCheckpoint ? " · checkpoint pointer saved" : " · no checkpoint pointer"));
  } else if (focus?.paused?.some(task => task.id === taskId)) {
    notes.push("Local focus: paused · checkpoint pointer saved");
  }
  return { notes, localHold: Boolean(hold) };
}

export function localFocusSummary(focus) {
  if (!focus) return "Not connected — no local focus file selected.";
  return (focus.active
    ? "Active " + focus.active.id + (focus.active.hasCheckpoint ? " (checkpoint pointer present)" : " (no checkpoint pointer)")
    : "No active task") + " · " + focus.paused.length + " paused task(s).";
}
