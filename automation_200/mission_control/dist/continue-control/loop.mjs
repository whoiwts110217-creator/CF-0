// AUTO-08: pure, connector-agnostic continuation queue.
// This module NEVER uses ChatGPT private APIs, browser automation, or credentials.
const safeId = /^[A-Za-z0-9_-]{6,80}$/;
const privateId = /^[0-9a-f-]{20,80}$/i;
export const CONTINUE_MESSAGE = "continue";

export function importConversationIndex(raw) {
  // Only metadata is retained. The original export's messages are not copied.
  const data = typeof raw === "string" ? JSON.parse(raw) : raw;
  const rows = Array.isArray(data) ? data
    : Array.isArray(data?.conversations) ? data.conversations : null;
  if (!rows) throw new Error("Expected a ChatGPT conversations.json array or a conversations index.");
  if (rows.length > 50000) throw new Error("Conversation index exceeds the local safety limit.");
  const seen = new Set();
  const result = [];
  for (const item of rows) {
    const id = typeof item?.id === "string" ? item.id
      : typeof item?.conversation_id === "string" ? item.conversation_id : "";
    if (!(safeId.test(id) || privateId.test(id)) || seen.has(id)) continue;
    seen.add(id);
    result.push({
      id,
      title: typeof item.title === "string" && item.title.trim()
        ? item.title.trim().slice(0, 160) : "Untitled conversation",
      selected: true,
      status: "queued", completedPass: 0
    });
  }
  return result;
}

export function selectionSummary(queue) {
  return {total: queue.length, eligible: queue.filter(x => x.selected).length,
    excluded: queue.filter(x => !x.selected).length};
}

export function makeCheckpoint({account, queue, pass = 0, events = []}) {
  if (!["primary","secondary"].includes(account)) throw new Error("Choose the signed-in account.");
  if (!Array.isArray(queue) || !Array.isArray(events)) throw new Error("Invalid checkpoint.");
  return {
    schema: "cf0.auto08.private_checkpoint.v1",
    // The human user downloads this locally; never publish it to public GitHub.
    account, pass, queue: queue.map(x => ({id:x.id, title:x.title, selected:!!x.selected, status:x.status,
      completedPass:Number.isSafeInteger(x.completedPass) && x.completedPass >= 0 ? x.completedPass : 0})),
    events: events.slice(-1000)
  };
}

export async function runSerial({queue, driver, onEvent = () => {},
  signal, repeat = false, maxPasses = 1, initialPass = 1}) {
  if (!Array.isArray(queue) || !driver || typeof driver.sendAndWait !== "function")
    throw new Error("A supported, owner-authorized executor is required.");
  if (!Number.isSafeInteger(initialPass) || initialPass < 1
      || !Number.isSafeInteger(maxPasses) || maxPasses < 1 || maxPasses > 100)
    throw new Error("Invalid pass limits.");
  let sent = 0;
  let finished = 0;
  const eligible = queue.filter(x => x && x.selected && typeof x.id === "string");
  for (let pass = initialPass; pass <= maxPasses; pass++) {
    for (const chat of eligible) {
      if (signal?.aborted) return {status:"stopped", pass, sent, finished};
      // Skip only provably completed work in the current pass on checkpoint resumption.
      if (Number.isSafeInteger(chat.completedPass) && chat.completedPass >= pass) {
        onEvent({type:"checkpoint_skip", pass, chatId:chat.id});
        continue;
      }
      // Never resume chat if a previous attempt's outcome is unknown.
      if (chat.status === "unknown") return {status:"needs_review", pass, chatId:chat.id, sent, finished};
      onEvent({type:"starting", pass, chatId:chat.id});
      let result;
      try {
        // This promise MUST resolve only after the model finished replying.
        result = await driver.sendAndWait({
          chatId:chat.id, text:CONTINUE_MESSAGE, signal, pass
        });
        sent++;
      } catch (error) {
        chat.status = "unknown";
        onEvent({type:"blocked", pass, chatId:chat.id, reason:"executor_failed"});
        return {status:"needs_review", pass, chatId:chat.id, sent, finished};
      }
      if (result?.status !== "completed") {
        chat.status = "unknown";
        onEvent({type:"blocked", pass, chatId:chat.id,
          reason:typeof result?.status === "string" ? result.status : "unknown"});
        return {status:"needs_review", pass, chatId:chat.id, sent, finished};
      }
      chat.status = "completed";
      chat.completedPass = pass;
      finished++;
      onEvent({type:"completed", pass, chatId:chat.id});
      if (signal?.aborted) return {status:"stopped", pass, sent, finished};
    }
    onEvent({type:"pass_completed", pass});
    if (!repeat) return {status:"completed", pass, sent, finished};
    // A real executor must implement rate limiting, quotas and backoff.
    // No unbounded loop: even explicit repeat is capped by maxPasses.
  }
  return {status:"completed", pass:maxPasses, sent, finished};
}
