// CF-0 AUTO-08: private, keyboard-only, one-tab continuation sweep.
// No mouse/coordinate commands, ChatGPT private APIs, auth tokens or public transcript uploads.
export const MESSAGE = 'continue';
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const COMPOSER = '#prompt-textarea, [data-testid="composer-input"], [contenteditable="true"][role="textbox"]';

export function importQueue(raw) {
  const list = Array.isArray(raw) ? raw : raw?.conversations;
  if (!Array.isArray(list) || list.length > 50000) throw new Error('Expected private conversations.json (50,000 maximum).');
  const ids = new Set();
  return list.flatMap(entry => {
    const id = entry?.id ?? entry?.conversation_id;
    if (typeof id !== 'string' || !UUID.test(id) || ids.has(id)) return [];
    ids.add(id);
    return [{id, title: String(entry.title || 'Untitled').slice(0, 120), selected: true}];
  });
}

export function conversationURL(id) {
  if (!UUID.test(id)) throw new Error('Invalid conversation ID.');
  return 'https://chatgpt.com/c/' + id;
}

export function newCheckpoint(account, queue) {
  if (!['primary', 'secondary'].includes(account)) throw new Error('Select primary or secondary account.');
  return {schema:'cf0.auto08.keyboard_checkpoint.v1', account, pass:1,
    entries:Object.fromEntries(queue.map(c => [c.id,{status:'queued', completedPass:0}])),
    updatedAt:null};
}

export async function runSweep({account, queue, checkpoint, driver, save, limit=1, pass=1, signal}) {
  if (!['primary','secondary'].includes(account) || checkpoint?.account !== account || !Array.isArray(queue))
    throw new Error('Account or checkpoint mismatch.');
  if (!driver || typeof driver.sendAndWait !== 'function' || typeof save !== 'function')
    throw new Error('Real signed-in browser driver and private checkpoint save required.');
  if (!Number.isSafeInteger(pass) || pass < 1 || !Number.isSafeInteger(limit) || limit < 1)
    throw new Error('Invalid pass or limit.');
  let completed = 0;
  let attempted = 0;
  for (const chat of queue) {
    if (signal?.aborted) return {status:'stopped', completed, attempted};
    if (!chat.selected) continue;
    const entry = checkpoint.entries[chat.id];
    if (!entry) throw new Error('Checkpoint does not match the queue.');
    if (entry.completedPass >= pass) continue;
    if (entry.status === 'unknown' || entry.status === 'in_flight')
      return {status:'needs_review', chatId:chat.id, completed, attempted};
    if (attempted >= limit) return {status:'limit_reached', completed, attempted};
    entry.status = 'in_flight'; // Persist BEFORE send; unknown outcome never silently retried.
    checkpoint.updatedAt = new Date().toISOString();
    await save(checkpoint);
    attempted++;
    try {
      const result = await driver.sendAndWait({url:conversationURL(chat.id), text:MESSAGE, signal});
      if (result?.status !== 'completed') throw new Error(result?.status ?? 'unknown_result');
      entry.status = 'completed';
      entry.completedPass = pass;
      completed++;
    } catch (error) {
      entry.status = 'unknown';
      entry.reason = String(error?.message ?? error).slice(0, 120);
      checkpoint.updatedAt = new Date().toISOString();
      await save(checkpoint);
      return {status:'needs_review', chatId:chat.id, completed, attempted};
    }
    checkpoint.updatedAt = new Date().toISOString();
    await save(checkpoint);
  }
  return {status:'completed', completed, attempted};
}

export function keyboardDriver(page, {timeoutMs=240000, settleMs=6000}={}) {
  if (!page?.keyboard || !page?.goto || !page?.locator || !page?.waitForFunction) throw new Error('Playwright Page required.');
  return {async sendAndWait({url, text, signal}) {
    if (signal?.aborted) throw new Error('stopped');
    // Navigation reuses THIS Page. No new tab, new window, or mouse interaction.
    await page.goto(url,{waitUntil:'domcontentloaded',timeout:30000});
    if (new URL(page.url()).pathname !== new URL(url).pathname) throw new Error('wrong_chat_or_signed_out');
    const composer = page.locator(COMPOSER).first();
    await composer.waitFor({state:'visible',timeout:20000});
    const baseline = await page.evaluate(() => ({
      users:document.querySelectorAll('[data-message-author-role="user"]').length,
      assistants:document.querySelectorAll('[data-message-author-role="assistant"]').length
    }));
    if (signal?.aborted) throw new Error('stopped');
    await composer.focus(); // Keyboard focus; never click.
    // Refuse to append 'continue' to a draft the owner is composing.
    const draft = await composer.evaluate(el => (el.innerText || el.textContent || '').trim());
    if (draft) throw new Error('existing_draft_do_not_overwrite');
    await page.keyboard.insertText(text);
    await page.keyboard.press('Enter');
    // Only count a send when a NEW user turn really appears in the selected chat.
    await page.waitForFunction(before =>
      document.querySelectorAll('[data-message-author-role="user"]').length > before,
      baseline.users,{timeout:20000,polling:250});
    await page.waitForFunction(before =>
      document.querySelectorAll('[data-message-author-role="assistant"]').length > before,
      baseline.assistants,{timeout:timeoutMs,polling:500});
    // Conservative completion check: last assistant output stabilizes, Stop is gone,
    // and ChatGPT isn't exposing a busy reply. UI changes fail closed as unknown.
    await page.waitForFunction(ms => {
      const assistants = [...document.querySelectorAll('[data-message-author-role="assistant"]')];
      const last = assistants.at(-1);
      if (!last) return false;
      const responseText = (last.innerText || '').trim();
      const stop = document.querySelector('[data-testid="stop-button"], button[aria-label*="Stop generating" i]');
      const busy = last.querySelector('[aria-busy="true"]');
      if (!responseText || stop || busy) { window.__cf0Stable = null; return false; }
      const now = performance.now();
      if (!window.__cf0Stable || window.__cf0Stable.text !== responseText) {
        window.__cf0Stable = {text:responseText, since:now}; return false;
      }
      return now - window.__cf0Stable.since >= ms;
    },settleMs,{timeout:timeoutMs,polling:500});
    if (signal?.aborted) throw new Error('stopped');
    return {status:'completed'};
  }};
}
