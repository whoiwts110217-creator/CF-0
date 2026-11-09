// Pure functions, safe for browser and Node tests. No Chrome API calls here.
export const CHATGPT_HOST = 'chatgpt.com';
export const CONTINUE_TEXT = 'continue';
export const CHAT_ID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
export const WORKSPACE = 'https://chatgpt.com';

export function chatId(url) {
  try {
    const u = new URL(url);
    if (u.protocol !== 'https:' || u.hostname !== CHATGPT_HOST) return null;
    const m = /^\/c\/([0-9a-f-]{36})\/?$/i.exec(u.pathname);
    return m && CHAT_ID.test(m[1]) ? m[1] : null;
  } catch { return null; }
}
export function chatURL(id) {
  if (!CHAT_ID.test(id)) throw new Error('Invalid conversation ID');
  return WORKSPACE + '/c/' + id;
}
export function eligibleTabs(tabs) {
  return (tabs || []).filter(t => {
    try { const u = new URL(t.url); return u.protocol === 'https:' && u.hostname === CHATGPT_HOST; }
    catch { return false; }
  });
}
export function pickSingleTab(tabs) {
  const found = eligibleTabs(tabs);
  if (found.length !== 1) throw new Error(found.length === 0 ? 'NO_CHATGPT_TAB' : 'MULTIPLE_CHATGPT_TABS');
  if (!Number.isInteger(found[0].id)) throw new Error('INVALID_TAB_ID');
  return found[0];
}
export function importQueue(raw) {
  const list = Array.isArray(raw) ? raw : raw?.conversations;
  if (!Array.isArray(list) || list.length > 50000) throw new Error('EXPECTED_CONVERSATIONS_JSON');
  const seen = new Set();
  return list.flatMap(x => {
    const id = x?.id ?? x?.conversation_id;
    if (typeof id !== 'string' || !CHAT_ID.test(id) || seen.has(id)) return [];
    seen.add(id);
    return [{id, title:String(x.title || 'Untitled').slice(0,100)}];
  });
}
export function classifyOverlay(snapshot) {
  const text = String(snapshot?.dialogText || '').trim().toLowerCase();
  const url = String(snapshot?.url || '');
  if (snapshot?.signedOut || /(?:login|auth)\.openai\.com/i.test(url)) return 'SIGN_IN_REQUIRED';
  if (snapshot?.rateLimit || /too many requests|usage limit|try again later|rate limit/i.test(text)) return 'RATE_LIMIT';
  if (!snapshot?.dialogVisible) return 'CLEAR';
  // Close only clearly harmless informational dialogs, by keyboard Escape.
  if (/^(what.s new|keyboard shortcuts|new in chatgpt|welcome to chatgpt|release notes)\b/.test(text)) return 'DISMISS_WITH_ESCAPE';
  return 'NEEDS_OWNER_REVIEW';
}
// A visible acknowledgement is not merely an extra user message: it must be
// the sole new user turn, containing exactly the command the owner authorized.
// Only a boolean is returned from the private ChatGPT DOM; no message text is saved.
export function acknowledgedContinue(snapshot, baselineUsers) {
  return Number.isSafeInteger(baselineUsers) && baselineUsers >= 0 &&
    snapshot?.userCount === baselineUsers + 1 &&
    snapshot.lastUserExactContinue === true;
}

export function stableResponse(prev, current, now, settleMs=8000) {
  if (!current || current.blocker || current.stopVisible || current.busy || !current.lastAssistantText ||
      current.assistantCount <= current.baselineAssistants ||
      !acknowledgedContinue(current, current.baselineUsers))
    return {ready:false, text:'', since:now};
  const text = current.lastAssistantText;
  if (prev?.text !== text || !Number.isFinite(prev?.since)) return {ready:false,text,since:now};
  return {ready:now-prev.since>=settleMs, text, since:prev.since};
}
export function initialState() {
  return {schema:'cf0.auto08.chrome.v1', account:null, selectedTabId:null,
    phase:'idle', reason:'NOT_CONNECTED', queue:[], completed:[], currentChat:null,
    attempt:null, updatedAt:null, lastResult:null, maxChats:1};
}
