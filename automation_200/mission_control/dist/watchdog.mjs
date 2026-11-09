// Read-only metadata from GitHub Actions. Not HP identity or execution proof.
const REPO = "whoiwts110217-creator/CF-0";
const WORKFLOW = "cf0-channel-watchdog.yml";
export const WATCHDOG_URL =
  "https://api.github.com/repos/" + REPO + "/actions/workflows/" + WORKFLOW + "/runs?per_page=1";

export function watchdogModel(value) {
  const runs = value?.workflow_runs;
  if (!Array.isArray(runs) || runs.length !== 1) return null;
  const item = runs[0];
  if (!item || !Number.isSafeInteger(item.id) || item.id <= 0
      || item.path !== ".github/workflows/" + WORKFLOW
      || item.head_branch !== "main"
      || !/^[a-f0-9]{40}$/.test(item.head_sha ?? "")
      || !["schedule", "push", "workflow_dispatch"].includes(item.event)
      || !["queued", "in_progress", "completed"].includes(item.status)
      || (item.status === "completed" && !["success", "failure", "cancelled",
        "skipped", "timed_out", "action_required", "neutral"].includes(item.conclusion))
      || (item.status !== "completed" && item.conclusion !== null)
      || typeof item.created_at !== "string"
      || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(item.created_at)
      || !Number.isFinite(Date.parse(item.created_at))
      || (item.repository?.full_name && item.repository.full_name !== REPO)) return null;
  return {
    id: item.id, link: "https://github.com/" + REPO + "/actions/runs/" + item.id,
    event: item.event, commit: item.head_sha,
    status: item.status, conclusion: item.conclusion,
    createdAt: Date.parse(item.created_at),
    hpIdentityAttested: false, taskExecuted: false,
  };
}

export async function loadWatchdog(fetcher = fetch, signal = AbortSignal.timeout(7000)) {
  const response = await fetcher(WATCHDOG_URL, {
    cache: "no-store", credentials: "omit", redirect: "error", signal,
  });
  if (!response.ok) throw new Error("Public cloud watchdog metadata unavailable");
  const result = watchdogModel(await response.json());
  if (!result) throw new Error("Invalid public cloud watchdog metadata");
  return result;
}
