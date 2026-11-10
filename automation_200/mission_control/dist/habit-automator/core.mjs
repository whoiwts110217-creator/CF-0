// CF-0 Habit Automator v0.1 — pure model, no network, no account authority.
export const SCHEMA = "cf0.habit_automator.v1";
export const STORAGE_KEY = "cf0.habit-automator.v1";
export const MAX_ROUTINES = 100;
export const STEP_TYPES = ["check", "link", "shortcut"];
const TIME = /^([01]\d|2[0-3]):([0-5]\d)$/;
const idPattern = /^[A-Za-z0-9_-]{1,80}$/;
const validId = value => typeof value === "string" && idPattern.test(value);
const stamp = value => typeof value === "string" && !Number.isNaN(Date.parse(value)) ? value : null;
const words = (value, limit) => typeof value === "string" ? value.trim().slice(0, limit) : "";

export function safeLink(input) {
  const text = words(input, 1800);
  try {
    const url = new URL(text);
    if (url.protocol !== "https:" || url.username || url.password) return null;
    return url.href;
  } catch { return null; }
}

export function shortcutLink(name) {
  const value = words(name, 80);
  return value ? "shortcuts://run-shortcut?name=" + encodeURIComponent(value) : null;
}

export function normalizeStep(step, index = 0) {
  if (!step || typeof step !== "object" || !STEP_TYPES.includes(step.type)) throw Error("Invalid step type");
  const label = words(step.label, 100);
  if (!label) throw Error("Each step needs a label");
  const target = words(step.target, 1800);
  if (step.type === "link" && !safeLink(target)) throw Error("Links must use valid HTTPS URLs");
  if (step.type === "shortcut" && (!target || target.length > 80)) throw Error("Enter an iPhone Shortcut name");
  return { id: validId(step.id) ? step.id : "step-" + index, type: step.type, label,
    target: step.type === "link" ? safeLink(target) : step.type === "shortcut" ? target : "" };
}

export function normalizeRoutine(r, index = 0) {
  if (!r || typeof r !== "object") throw Error("Invalid routine");
  const title = words(r.title, 90);
  if (!title) throw Error("Routine title required");
  const schedule = r.schedule || {};
  const type = ["daily", "weekly", "manual"].includes(schedule.type) ? schedule.type : "manual";
  const time = TIME.test(schedule.time) ? schedule.time : "09:00";
  const days = [...new Set(Array.isArray(schedule.days) ? schedule.days.filter(n => Number.isInteger(n) && n >= 0 && n <= 6) : [])].sort();
  if (type === "weekly" && !days.length) throw Error("Pick at least one weekday");
  if (!Array.isArray(r.steps) || !r.steps.length || r.steps.length > 12) throw Error("Routines need 1–12 steps");
  const steps = r.steps.map(normalizeStep);
  if (new Set(steps.map(s => s.id)).size !== steps.length) throw Error("Duplicate step identifiers");
  return {
    id: validId(r.id) ? r.id : "routine-" + index,
    title, description: words(r.description, 180), enabled: r.enabled !== false,
    schedule: {type, time, days}, steps,
    createdAt: stamp(r.createdAt), lastRunAt: stamp(r.lastRunAt)
  };
}

export function emptyState() { return {schema:SCHEMA, routines:[], history:[], active:null}; }

export function parseState(raw) {
  const x = typeof raw === "string" ? JSON.parse(raw) : raw;
  if (!x || x.schema !== SCHEMA || !Array.isArray(x.routines) || x.routines.length > MAX_ROUTINES) throw Error("Not a Habit Automator v1 backup");
  const routines = x.routines.map(normalizeRoutine);
  if (new Set(routines.map(r => r.id)).size !== routines.length) throw Error("Duplicate routine identifiers");
  const history = Array.isArray(x.history) ? x.history.slice(0, 500).filter(h =>
    h && validId(h.routineId) && stamp(h.finishedAt) &&
    ["owner_marked", "aborted"].includes(h.status)
  ).map(h => ({id:validId(h.id) ? h.id : "imported", routineId:h.routineId,
    title:words(h.title,90), startedAt:stamp(h.startedAt), finishedAt:h.finishedAt,
    status:h.status, steps:Number.isInteger(h.steps) ? Math.max(0,Math.min(12,h.steps)) : 0})) : [];
  const a = x.active;
  const active = a && validId(a.routineId) && routines.some(r=>r.id===a.routineId) &&
    Array.isArray(a.completedStepIds) && stamp(a.startedAt) ?
    {routineId:a.routineId, startedAt:a.startedAt,
      completedStepIds:[...new Set(a.completedStepIds.filter(id=>validId(id) && routines.find(r=>r.id===a.routineId).steps.some(s=>s.id===id)))].slice(0,12)} : null;
  return {schema:SCHEMA, routines, history, active};
}

export function dueInfo(routine, now = new Date()) {
  if (routine.schedule.type === "manual") return {due:false, next:null, latest:null, label:"Manual"};
  const [hour, minute] = routine.schedule.time.split(":").map(Number);
  const allowed = date => routine.schedule.type === "daily" || routine.schedule.days.includes(date.getDay());
  let latest = null, next = null;
  for (let offset = 0; offset <= 7; offset++) {
    const past = new Date(now.getFullYear(), now.getMonth(), now.getDate() - offset, hour, minute);
    if (!latest && past <= now && allowed(past)) latest = past;
    const future = new Date(now.getFullYear(), now.getMonth(), now.getDate() + offset, hour, minute);
    if (!next && future > now && allowed(future)) next = future;
  }
  const completed = routine.lastRunAt && Date.parse(routine.lastRunAt) >= (latest?.getTime() ?? Infinity);
  const due = Boolean(routine.enabled && latest && !completed);
  return {due, next, latest, label:due ? "Due now" : next ? "Next " + next.toLocaleString([], {weekday:"short",hour:"numeric",minute:"2-digit"}) : "No schedule"};
}

export function freshId(prefix="id") {
  if (globalThis.crypto?.randomUUID) return prefix+"-"+globalThis.crypto.randomUUID();
  return prefix+"-"+Date.now().toString(36)+"-"+Math.random().toString(36).slice(2,10);
}
