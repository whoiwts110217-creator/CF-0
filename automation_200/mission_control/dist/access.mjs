// Read-only classification for CF-0 public Mission Control.
// Never conflate a task type or source file with live execution authority.
export const OWNER_LOCAL_EVIDENCE = new Set([
  "CF-042", "CF-077", "CF-184", "CF-190", "CF-191", "CF-194",
]);
export const ACCESS_LABELS = Object.freeze({
  verified: "Verified / complete",
  source_candidate: "Source candidate only",
  physical_hp_required: "Physical HP evidence required",
  hp_install_needs_local_review: "Owner-local installation review",
  owner_local_evidence_required: "Owner-local evidence required",
  dependencies_unverified: "Waiting on prerequisites",
});

export function taskAccess(task, statuses) {
  const known = statuses instanceof Map ? statuses : new Map(statuses.map(x => [x.id, x.status]));
  let reason;
  if (task.status === "verified") reason = "verified";
  else if (task.physical_hp_required) reason = "physical_hp_required";
  else if (task.stream === "hp_install") reason = "hp_install_needs_local_review";
  else if (OWNER_LOCAL_EVIDENCE.has(task.id)) reason = "owner_local_evidence_required";
  else if (task.depends_on.some(id => known.get(id) !== "verified")) reason = "dependencies_unverified";
  else reason = "source_candidate";
  return {
    reason,
    label: ACCESS_LABELS[reason],
    restricted: reason !== "source_candidate" && reason !== "verified",
    // Suggested work category, NOT permission to execute that work.
    power: reason === "verified" ? "Completed" :
      (task.physical_hp_required || task.stream === "hp_install" ||
       OWNER_LOCAL_EVIDENCE.has(task.id)) ? "Device-local / evidence-gated" :
      task.stream === "public_finance" ? "Financial preparation only" :
      "Source review / test proposal",
  };
}

export function summarizeAccess(tasks) {
  const status = new Map(tasks.map(x => [x.id, x.status]));
  const totals = Object.fromEntries(Object.keys(ACCESS_LABELS).map(k => [k, 0]));
  for (const task of tasks) totals[taskAccess(task, status).reason] += 1;
  return totals;
}

export function contractTools(contract) {
  if (contract?.schema !== "cf0.owner_capability_contract.v1"
      || !Array.isArray(contract.capabilities)) return null;
  const known = new Map([
    ["public_relay_ping", ["ping", "L1 · allowlisted public relay"]],
    ["public_relay_status", ["hp_status", "L1 · allowlisted public relay"]],
    ["public_relay_sidecar_verify", ["sidecar_verify", "L1 · read-only, configured relay"]],
    ["hp_health_monitor", ["HP health monitor", "L0 · read public report"]],
    ["founder_decision_engine", ["Owner priority decision engine", "L0 · propose tasks, no execution"]],
    ["relay_unknown_attempt_recovery", ["Recovery guide", "L0 · source documentation"]],
    ["notepad_owner_launch", ["open_notepad (historical)", "L3 · requires owner-local restoration"]],
  ]);
  const rows = [];
  const seen = new Set();
  for (const cap of contract.capabilities) {
    if (typeof cap?.id !== "string" || seen.has(cap.id)
        || typeof cap.status !== "string") return null;
    seen.add(cap.id);
    const [name, power] = known.get(cap.id) ?? [cap.id, "Unclassified · review source"];
    rows.push({
      id: cap.id, name, power, status: cap.status,
      restricted: cap.status !== "active_source",
      note: cap.status === "regression_open"
        ? "Previously used; not available in current public relay."
        : "Source-present; device deployment and unattended operation not established.",
    });
  }
  return rows;
}
