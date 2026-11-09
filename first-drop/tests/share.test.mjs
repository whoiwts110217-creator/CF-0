import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";

const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
const script = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];

function setup({ nativeShare, clipboard, secure = true, prompt } = {}) {
  assert.ok(script, "First Drop inline sharing code is present");
  const handlers = new Map();
  const feedback = { textContent: "" };
  const buttons = {
    "share-clarity-card": { addEventListener: (event, fn) => { assert.equal(event, "click"); handlers.set("tool", fn); } },
    "copy-first-drop": { addEventListener: (event, fn) => { assert.equal(event, "click"); handlers.set("invite", fn); } },
    "share-feedback": feedback
  };
  const navigator = {};
  if (nativeShare) navigator.share = nativeShare;
  if (clipboard) navigator.clipboard = { writeText: clipboard };
  const promptCalls = [];
  const window = {
    isSecureContext: secure,
    prompt: (...args) => { promptCalls.push(args); if (prompt) prompt(...args); }
  };
  runInNewContext(script, { document: { getElementById: id => buttons[id] }, navigator, window }, { timeout: 1500 });
  return { feedback, promptCalls, click: async key => handlers.get(key)() };
}

test("keeps existing third-party composer links and clear no-auto-post disclosure", () => {
  for (const host of ["twitter.com/intent/tweet", "bsky.app/intent/compose", "reddit.com/submit", "facebook.com/sharer", "linkedin.com/sharing"]) {
    assert.ok(html.includes(host), `missing composer for ${host}`);
  }
  assert.match(html, /do not automatically post anything/i);
  assert.match(html, /id="share-feedback" role="status" aria-live="polite"/);
  assert.match(html, /https:\/\/cash\.app\/\$LAZYBLACKBEAN/);
});

test("shares free Clarity Card through a user-initiated native share sheet", async () => {
  const calls = [];
  const page = setup({ nativeShare: async value => { calls.push(value); } });
  await page.click("tool");
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "https://whoiwts110217-creator.github.io/CF-0/clarity-card/");
  assert.match(page.feedback.textContent, /dialog closed/i);
});

test("copies the free tool URL when native sharing is unavailable", async () => {
  const copied = [];
  const page = setup({ clipboard: async value => { copied.push(value); } });
  await page.click("tool");
  assert.deepEqual(copied, ["https://whoiwts110217-creator.github.io/CF-0/clarity-card/"]);
  assert.match(page.feedback.textContent, /link copied/i);
});

test("copy invitation uses actual First Drop URL", async () => {
  const copied = [];
  const page = setup({ clipboard: async value => { copied.push(value); } });
  await page.click("invite");
  assert.deepEqual(copied, ["https://whoiwts110217-creator.github.io/CF-0/first-drop/"]);
});

test("manual copy fallback survives clipboard failure and insecure contexts", async () => {
  const page = setup({ clipboard: async () => { throw new Error("permission blocked"); } });
  await page.click("invite");
  assert.equal(page.promptCalls[0][1], "https://whoiwts110217-creator.github.io/CF-0/first-drop/");
  assert.match(page.feedback.textContent, /copy the link/i);
});

test("canceling the native share sheet never triggers copy or claims to post", async () => {
  let copied = false;
  const page = setup({
    nativeShare: async () => { throw { name: "AbortError" }; },
    clipboard: async () => { copied = true; }
  });
  await page.click("tool");
  assert.equal(copied, false);
  assert.match(page.feedback.textContent, /nothing was posted/i);
});
