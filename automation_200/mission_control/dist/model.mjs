export const REPO = "whoiwts110217-creator/CF-0";
export const GITHUB = "https://github.com/" + REPO;
export const REGISTRY = "automation_200/registry.json";
export const STATE = "docs/PUBLIC_CONTINUITY_STATE.json";
export const HEALTH = "relay/health/latest.json";

const commitPattern = /^[a-f0-9]{40}$/;
const pingPattern = /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/;

export function pingPaths(state) {
  const id = state?.hp?.public_ping_request_id;
  if (typeof id !== "string" || !pingPattern.test(id)) return null;
  return { id, inbox: "command_queue/inbox/" + id + ".json", receipt: "command_queue/receipts/" + id + ".json" };
}

export function registryModel(registry) {
  if (registry?.schema !== "CF200.1" || registry.target !== 200
      || !Array.isArray(registry.tasks) || registry.tasks.length !== registry.target) {
    throw new Error("Invalid work order registry");
  }
  const ids = new Set(registry.tasks.map(task => task?.id));
  for (let number = 1; number <= registry.target; number++) {
    if (!ids.has("CF-" + String(number).padStart(3, "0"))) throw new Error("Invalid work order ID");
  }
  for (const task of registry.tasks) {
    if (typeof task.title !== "string" || typeof task.stream !== "string"
        || !["planned", "verified"].includes(task.status) || !Array.isArray(task.depends_on)
        || !task.depends_on.every(id => ids.has(id)) || typeof task.physical_hp_required !== "boolean"
        || (task.status === "verified" && (typeof task.evidence !== "string" || !task.evidence.trim()))) {
      throw new Error("Invalid work order record");
    }
  }
  const verified = registry.tasks.filter(task => task.status === "verified").length;
  if (verified !== registry.completed) throw new Error("Conflicting work order counts");
  return {
    target: registry.target,
    verified,
    tasks: [...registry.tasks].sort((a, b) => a.id.localeCompare(b.id)),
  };
}

export function filterTasks(tasks, status, query) {
  const terms = query.toLowerCase().trim().split(/\s+/);
  return tasks.filter(task => {
    if (status !== "all" && task.status !== status) return false;
    const value = [task.id, task.title, task.stream.replaceAll("_", " ")].join(" ").toLowerCase();
    return terms.every(term => value.includes(term));
  });
}

async function canonicalDigest(value) {
  const canonical = JSON.stringify(Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b))));
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(canonical));
  return Array.from(new Uint8Array(bytes), byte => byte.toString(16).padStart(2, "0")).join("");
}

async function matchedPing(paths, ping) {
  const { request, receipt } = ping ?? {};
  if (!paths || !request || !receipt || !globalThis.crypto?.subtle) return false;
  if (request.v !== 1 || request.id !== paths.id || request.action !== "ping"
      || !Number.isSafeInteger(request.issued) || !Number.isSafeInteger(request.expires)
      || request.expires <= request.issued || request.expires - request.issued > 86400
      || !request.args || typeof request.args !== "object" || Array.isArray(request.args)
      || Object.keys(request.args).length !== 0 || Object.keys(request).length !== 6
      || ![1, 2].includes(receipt.v) || receipt.id !== paths.id || receipt.status !== "completed"
      || receipt.result?.pong !== true || receipt.result?.protocol !== 1
      || Object.keys(receipt).length !== (receipt.v === 2 ? 6 : 5)) return false;

  if (receipt.request_sha256 !== await canonicalDigest(request)) return false;
  if (receipt.v === 1) return !Object.hasOwn(receipt, "response_sha256");
  // The allowlisted ping result has exactly two fields with scalar JSON values.
  return Object.keys(receipt.result).length === 2
    && receipt.response_sha256 === await canonicalDigest(receipt.result);
}

export async function dashboardModel(data) {
  if (typeof data?.commit !== "string" || !commitPattern.test(data.commit)) throw new Error("Invalid source commit");
  const model = registryModel(data.registry);
  const state = data.state?.schema === "cf0.public_continuity.v1" ? data.state : null;
  const info = state?.cf200;
  const checkpoint = info?.verified === model.verified && info?.target === model.target
    && Number.isInteger(info.last_numbered_checkpoint)
    && info.last_numbered_checkpoint > 0 && info.last_numbered_checkpoint <= model.verified
    ? info.last_numbered_checkpoint : null;
  const paths = pingPaths(state);
  const matched = await matchedPing(paths, data.ping);
  return {
    ...model,
    commit: data.commit,
    checkpoint,
    ping: matched ? "matched" : data.ping ? "unconfirmed" : "unavailable",
    receiptPath: matched ? paths.receipt : null,
    health: ["not_published", "available", "invalid"].includes(data.health) ? data.health : "unavailable",
  };
}

async function get(fetcher, url, signal) {
  return fetcher(url, { cache: "no-store", credentials: "omit", redirect: "error", signal });
}

async function getJson(fetcher, url, signal) {
  const response = await get(fetcher, url, signal);
  if (!response.ok) throw new Error("GitHub evidence unavailable");
  return response.json();
}

async function healthAvailability(fetcher, url, signal) {
  try {
    const response = await get(fetcher, url, signal);
    if (response.status === 404) return "not_published";
    if (!response.ok) return "unavailable";
    const content = await response.text();
    if (content.length > 1024) return "invalid";
    return JSON.parse(content)?.schema === "cf0.hp_health.v1" ? "available" : "invalid";
  } catch (error) {
    return error instanceof SyntaxError ? "invalid" : "unavailable";
  }
}

export async function loadLive(fetcher = fetch, signal = AbortSignal.timeout(8500)) {
  const ref = await getJson(fetcher, "https://api.github.com/repos/" + REPO + "/git/ref/heads/main", signal);
  const commit = ref?.object?.sha;
  if (ref?.ref !== "refs/heads/main" || ref.object?.type !== "commit"
      || typeof commit !== "string" || !commitPattern.test(commit)) throw new Error("Invalid GitHub ref");

  const raw = "https://raw.githubusercontent.com/" + REPO + "/" + commit + "/";
  const [registry, state, health] = await Promise.all([
    getJson(fetcher, raw + REGISTRY, signal),
    getJson(fetcher, raw + STATE, signal).catch(() => null),
    healthAvailability(fetcher, raw + HEALTH, signal),
  ]);
  const paths = pingPaths(state);
  const ping = paths && await Promise.all([
    getJson(fetcher, raw + paths.inbox, signal),
    getJson(fetcher, raw + paths.receipt, signal),
  ]).then(([request, receipt]) => ({ request, receipt })).catch(() => null);
  return dashboardModel({ commit, registry, state, ping, health });
}
