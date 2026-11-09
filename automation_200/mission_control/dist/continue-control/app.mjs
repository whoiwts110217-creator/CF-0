import {importConversationIndex, makeCheckpoint, selectionSummary, CONTINUE_MESSAGE} from "./loop.mjs";

const el = (id) => document.getElementById(id);
let queue = [];
let events = [];
let activeManual = null;

const handoff = [
  "Continue AUTO-08, Caveman Focus Continuity Control, in the Work session with the separately authorized signed-in secondary ChatGPT account.",
  "FIRST read current public main automation_200/MASTER_OPERATOR_PROMPT.md, then MASTER_CONTINUITY_PROMPT.md, then WORK_COPY_PASTE_AUTOMATION_PROMPT.md.",
  "Owner's recovered requirements: https://github.com/whoiwts110217-creator/CF-0/blob/main/docs/AUTO_CONTINUATION_CONTROL_2026-11-09.md",
  "Find the recent secondary-account chat where the owner discussed building an auto-control interface, master switch, all-conversation 'continue' loop, and Fire Force-inspired dark jacket / pale blue glow. Recover the exact original owner corrections and save that transcript context only in an authorized PRIVATE output; do not publish private chat text to GitHub.",
  "Control semantics: enumerate eligible signed-in chats through supported access, send exactly one 'continue' to one chat, await model response completion, record result, move to next; repeat bounded passes only at owner's direction; provide kill switch, safe resume and rate-limit handling.",
  "Inspect and extend existing Mission Control, not replace it. No fake live switch. Report what the current session actually retrieved or ran. This request does not authorize bypass of account or platform protections."
].join("\n\n");

function say(id, message) { el(id).textContent = message; }
function counts() {
  const summary = selectionSummary(queue);
  for (const key of ["total","eligible","excluded"]) say(key, summary[key]);
  say("queue-state", queue.length ? "INDEX LOADED" : "NO INDEX");
  el("queue-search").disabled = queue.length === 0;
  el("select-all").disabled = queue.length === 0;
  el("exclude-all").disabled = queue.length === 0;
  el("save-checkpoint").disabled = queue.length === 0 || !el("account").value;
  const canReview = !!queue.find(x => x.selected && x.status !== "reviewed_manual")
    && !!el("account").value && el("signed-in").checked;
  el("open-next").disabled = !canReview || !!activeManual;
  el("mark-reviewed").disabled = !activeManual;
}
function displayQueue() {
  counts();
  const search = el("queue-search").value.trim().toLocaleLowerCase();
  const matching = queue.filter(q => q.title.toLocaleLowerCase().includes(search));
  const list = el("queue-list");
  list.replaceChildren();
  for (const row of matching.slice(0, 70)) {
    const label = document.createElement("label");
    label.className = "queue-row";
    const select = document.createElement("input");
    select.type = "checkbox";
    select.checked = row.selected;
    select.addEventListener("change", () => {row.selected = select.checked; counts();});
    const text = document.createElement("span");
    text.textContent = row.title;
    text.title = row.title;
    const status = document.createElement("small");
    status.textContent = row.status === "reviewed_manual" ? "Manually reviewed"
      : row.status === "unknown" ? "Unknown result — review" : "Queued";
    label.append(select, text, status);
    list.append(label);
  }
  if (!matching.length) {
    const p = document.createElement("p"); p.className = "empty";
    p.textContent = queue.length ? "No chat titles match your search." : "Import an index to preview chats.";
    list.append(p);
  }
  if (matching.length > 70) {
    const p = document.createElement("p"); p.className = "small";
    p.textContent = "Showing first 70 of " + matching.length + " results. Narrow your search to select individual chats.";
    list.append(p);
  }
}
async function copy(text) {
  if (!navigator.clipboard?.writeText) throw new Error("Clipboard access unavailable.");
  await navigator.clipboard.writeText(text);
}
el("import-file").addEventListener("change", async event => {
  const file = event.target.files?.[0];
  if (!file) return;
  if (file.size > 40 * 1024 * 1024) {say("manual-status","File too large for browser review (40 MB maximum).");return;}
  try {
    const data = JSON.parse(await file.text());
    if (data?.schema === "cf0.auto08.private_checkpoint.v1" && Array.isArray(data.queue)) {
      queue = importConversationIndex(data.queue).map(item => {
        const old = data.queue.find(q => q.id === item.id);
        return {...item, selected:old.selected !== false,
          status:["queued","unknown","completed","reviewed_manual"].includes(old.status) ? old.status : "queued",
          completedPass:Number.isSafeInteger(old.completedPass) && old.completedPass >= 0 ? old.completedPass : 0};
      });
      if (["primary","secondary"].includes(data.account)) el("account").value = data.account;
      events = Array.isArray(data.events) ? data.events.slice(-1000) : [];
    } else {
      queue = importConversationIndex(data);
      events = [];
    }
    activeManual = null;
    say("manual-status",queue.length+" conversations indexed locally. No chat message was sent.");
    displayQueue();
  } catch (error) {
    say("manual-status","Cannot read index: " + (error instanceof Error ? error.message : "invalid JSON"));
  } finally {event.target.value = "";}
});
el("account").addEventListener("change", () => {
  el("signed-in").checked = false;
  activeManual = null;
  say("manual-status","Account selection changed. Reconfirm the ChatGPT sign-in before opening a chat.");
  counts();
});
el("signed-in").addEventListener("change",counts);
el("queue-search").addEventListener("input",displayQueue);
el("select-all").addEventListener("click",() => {queue.forEach(x=>x.selected=true);displayQueue();});
el("exclude-all").addEventListener("click",() => {queue.forEach(x=>x.selected=false);displayQueue();});
el("copy-work").addEventListener("click",async () => {
  try {await copy(handoff);say("copy-result","Recovery instructions copied. Paste into the authorized Work chat.");}
  catch {say("copy-result","Clipboard unavailable. Open the public requirements document and paste its Work handoff into Work.");}
});
el("save-checkpoint").addEventListener("click",() => {
  try {
    const content = JSON.stringify(makeCheckpoint({account:el("account").value, queue, events}),null,2);
    const blob = new Blob([content],{type:"application/json"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href=url; a.download="cf0-auto08-private-checkpoint.json";
    document.body.append(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),2000);
    say("manual-status","Private checkpoint downloaded on this device. Do not upload it to public GitHub.");
  } catch (error) {say("manual-status","Cannot save checkpoint: "+error.message);}
});
el("open-next").addEventListener("click",() => {
  if (!el("signed-in").checked || !el("account").value) return;
  const next = queue.find(x=>x.selected && x.status !== "reviewed_manual");
  if (!next) {say("manual-status","No eligible chats remain for manual review.");return;}
  // A new tab opens only after the owner clicks; this does NOT submit a message.
  const url="https://chatgpt.com/c/"+encodeURIComponent(next.id);
  const tab=window.open(url,"_blank","noopener,noreferrer");
  activeManual=next.id;
  events.push({kind:"manual_opened",chatId:next.id,at:new Date().toISOString()});
  say("manual-status",(tab ? "Opened" : "Popup may have been blocked for") +
    " “"+next.title+"”. Paste 'continue', wait for the answer, then mark manually reviewed. URL: "+url);
  copy(CONTINUE_MESSAGE).catch(()=>say("manual-status",
    "Chat link: "+url+" — clipboard blocked; type 'continue' yourself."));
  counts();
});
el("mark-reviewed").addEventListener("click",() => {
  const next=queue.find(x=>x.id===activeManual);
  if (!next) return;
  next.status="reviewed_manual";
  events.push({kind:"manual_reviewed_claim",chatId:next.id,at:new Date().toISOString()});
  activeManual=null;
  say("manual-status","Marked manually reviewed. This does not count as automatic execution or proof of model completion.");
  displayQueue();
});
// No synthetic executor is attached. The master switch is deliberately disabled.
// The serial engine exists as a tested adapter boundary, not as ChatGPT access.
counts();
