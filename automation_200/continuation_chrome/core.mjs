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
// A conversation URL plus composer is not proof the requested chat loaded.
// On an empty/error page (including another account's inaccessible chat),
// stop before issuing any keyboard input. This does not authenticate identity.
export function hasLoadedConversation(snapshot) {
  return Number.isSafeInteger(snapshot?.userCount) && snapshot.userCount >= 0 &&
    Number.isSafeInteger(snapshot?.assistantCount) && snapshot.assistantCount >= 0 &&
    snapshot.userCount + snapshot.assistantCount > 0;
}

// Only read already-rendered sidebar links: no private API, extra tab or
// network request. Returned IDs stay in extension-local Chrome storage.
export function capturedSidebarQueue(hrefs) {
  if (!Array.isArray(hrefs) || hrefs.length > 2000) throw Error('INVALID_VISIBLE_SIDEBAR');
  const ids = new Set();
  for (const value of hrefs) {
    if (typeof value !== 'string' || value.length > 1000) continue;
    try {
      const id=chatId(new URL(value,WORKSPACE).href);
      if(id)ids.add(id);
    } catch { /* Ignore invalid/untrusted anchors. */ }
  }
  return [...ids].slice(0,500).map(id=>({id,title:'Visible sidebar chat'}));
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
// Owner-local, no-send readiness verdict. Never equate a matching URL or
// rendered message history with verified account identity or owner consent.
// Return only constant reason codes, never private content or login details.
export function readinessVerdict(snapshot, expectedId) {
  if (!CHAT_ID.test(expectedId||'')) return 'OPEN_A_CONVERSATION_FIRST';
  if (chatId(snapshot?.url)!==expectedId) return 'PAGE_CONTENT_MISMATCH';
  const overlay=classifyOverlay(snapshot);
  if (overlay!=='CLEAR') return overlay==='DISMISS_WITH_ESCAPE'
    ? 'INFORMATION_DIALOG_PRESENT' : overlay;
  if (!hasLoadedConversation(snapshot)) return 'CONVERSATION_HISTORY_NOT_LOADED';
  if (!snapshot.composerVisible) return 'COMPOSER_NOT_READY';
  if (snapshot.stopVisible||snapshot.busy) return 'ALREADY_RESPONDING';
  if (snapshot.draft) return 'OWNER_DRAFT_PRESENT';
  return 'READY_ACCOUNT_UNVERIFIED';
}

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
// Account labels are owner-selected, not authenticated ChatGPT identities.
// Maintain independent local queues/completion receipts when the owner switches
// labels. Migrates the legacy single-active-account v1 state without dropping
// earlier checkpoints. No account information leaves Chrome extension storage.
export function accountSnapshot(state, nextAccount) {
  if (!['primary','secondary'].includes(nextAccount)) throw Error('SELECT_VALID_ACCOUNT');
  const src = state && typeof state === 'object' ? state : {};
  const profiles = {};
  for(const label of ['primary','secondary']){
    const saved=src.profiles?.[label];
    if(saved && Array.isArray(saved.queue) && Array.isArray(saved.completed)){
      profiles[label]={queue:[...saved.queue],completed:[...saved.completed],
        submitted:Array.isArray(saved.submitted)?[...saved.submitted]:[]};
    }
  }
  // Always snapshot the currently active legacy fields. They are authoritative
  // until the next account switch; a stored profile may be one step behind.
  if(['primary','secondary'].includes(src.account)){
    profiles[src.account]={queue:Array.isArray(src.queue)?[...src.queue]:[],
      completed:Array.isArray(src.completed)?[...src.completed]:[],
      submitted:Array.isArray(src.submitted)?[...src.submitted]:[]};
  }
  // Preserve an older pre-selection import rather than throwing it away.
  if(!src.account && !profiles[nextAccount]){
    profiles[nextAccount]={queue:Array.isArray(src.queue)?[...src.queue]:[],
      completed:Array.isArray(src.completed)?[...src.completed]:[],
      submitted:Array.isArray(src.submitted)?[...src.submitted]:[]};
  }
  const destination=profiles[nextAccount]||{queue:[],completed:[],submitted:[]};
  return {profiles,account:nextAccount,
    queue:[...destination.queue],completed:[...destination.completed],
    submitted:[...destination.submitted]};
}

export function initialState() {
  return {schema:'cf0.auto08.chrome.v1', account:null, selectedTabId:null,
    phase:'idle', reason:'NOT_CONNECTED', queue:[], completed:[], submitted:[], profiles:{}, currentChat:null,
    attempt:null, updatedAt:null, lastResult:null, maxChats:1};
}
