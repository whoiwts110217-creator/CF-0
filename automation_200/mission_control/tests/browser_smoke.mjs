// CF-EXP-GAME-LEARN-001: dependency-free headless Chromium responsive and keyboard smoke.
// Uses the actual local dashboard HTML/CSS/JS; does NOT assert iPhone Safari compatibility.
// No external account authentication or browser automation permissions are used.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";

const root = fileURLToPath(new URL("../dist/", import.meta.url));
const MIME = { ".html": "text/html; charset=utf-8", ".mjs": "text/javascript", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml", ".json": "application/json" };
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const server = createServer(async (request, response) => {
  const relative = normalize(decodeURIComponent((request.url || "/").split("?")[0])).replace(/^\/+/, "");
  if (relative.startsWith("..") || relative.includes("\\") || relative.startsWith("/")) {
    response.writeHead(403); response.end("Forbidden"); return;
  }
  try {
    const filename = join(root, relative || "index.html");
    const buffer = await readFile(filename);
    response.writeHead(200, { "content-type": MIME[extname(filename)] || "text/plain", "cache-control": "no-store" });
    response.end(buffer);
  } catch {
    response.writeHead(404); response.end("Not found");
  }
});
await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
const origin = "http://127.0.0.1:" + server.address().port + "/";
const browserPort = 9300 + (process.pid % 500);
const chrome = spawn(process.env.CF0_CHROME || "google-chrome", [
  "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
  "--no-first-run", "--remote-debugging-port=" + browserPort,
  "--user-data-dir=" + join(tmpdir(), "cf0-learning-chrome-" + process.pid),
  "about:blank"
], { stdio: "ignore" });
let socket, pending = new Map(), id = 0;

async function debugTarget() {
  for (let i = 0; i < 100; i++) {
    try {
      const resp = await fetch("http://127.0.0.1:" + browserPort + "/json");
      if (resp.ok) {
        const targets = await resp.json();
        const target = targets.find(x => x.type === "page");
        if (target?.webSocketDebuggerUrl) return target.webSocketDebuggerUrl;
      }
    } catch {}
    await pause(100);
  }
  throw Error("Chrome CDP endpoint unavailable");
}
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const n = ++id;
    const timer = setTimeout(() => { pending.delete(n); reject(Error("CDP timeout " + method)); }, 12000);
    pending.set(n, { resolve, reject, timer });
    socket.send(JSON.stringify({ id: n, method, params }));
  });
}
async function evaluate(expression) {
  const response = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  if (response.error || response.result?.exceptionDetails) {
    throw Error("Browser execution error: " + JSON.stringify(response.error || response.result.exceptionDetails));
  }
  return response.result?.result?.value;
}
async function key(keyName) {
  const keyCode = keyName === "Tab" ? 9 : 13;
  const code = keyName === "Tab" ? "Tab" : "Enter";
  await send("Input.dispatchKeyEvent", { type: "keyDown", key: keyName, code, windowsVirtualKeyCode: keyCode, nativeVirtualKeyCode: keyCode });
  await send("Input.dispatchKeyEvent", { type: "keyUp", key: keyName, code, windowsVirtualKeyCode: keyCode, nativeVirtualKeyCode: keyCode });
}
async function waitFor(test, label) {
  for (let i = 0; i < 80; i++) {
    if (await evaluate(test)) return;
    await pause(100);
  }
  throw Error("Timed out waiting for " + label);
}
try {
  socket = new WebSocket(await debugTarget());
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    if (!message.id) return;
    const waiting = pending.get(message.id);
    if (!waiting) return;
    clearTimeout(waiting.timer); pending.delete(message.id);
    message.error ? waiting.reject(Error(JSON.stringify(message.error))) : waiting.resolve(message);
  };
  await send("Runtime.enable");
  await send("Page.enable");
  // 390 CSS-pixel viewport: iPhone-width Chromium emulation, NOT an iPhone device.
  await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 3, mobile: true });
  await send("Page.navigate", { url: origin + "#learning-lab" });
  await waitFor("document.readyState === 'complete' && !!document.querySelector('#gameful-mode') && !!document.querySelector('#learning-lab [data-gameful-answer]')", "learning lab DOM");
  const initial = await evaluate(`(() => {
    const lab=document.getElementById('learning-lab'),box=lab.getBoundingClientRect();
    return {viewport:innerWidth,labLeft:box.left,labRight:box.right,labWidth:box.width,
      pageWidth:document.documentElement.scrollWidth,select:!!document.getElementById('gameful-mode'),
      controls:!!document.getElementById('automation-controls'),
      masterDisabled:!!document.querySelector('#automation-controls input[role="switch"][disabled]'),
      aria:document.getElementById('gameful-explanation').getAttribute('aria-live')};
  })()`);
  console.log("Phone-width viewport:", JSON.stringify(initial));
  assert.ok(initial.viewport >= 350 && initial.viewport <= 400, "Viewport meta should respect 390px emulation");
  assert.ok(initial.labLeft >= -2 && initial.labRight <= initial.viewport + 2, "Lab container must fit viewport");
  assert.ok(initial.labWidth > 250, "Lab content should remain readable at phone width");
  assert.ok(initial.controls && initial.masterDisabled, "Existing disconnected master control must remain intact");
  assert.equal(initial.aria, "polite");

  await evaluate(`(()=>{const m=document.getElementById('gameful-mode');m.value='plain';m.dispatchEvent(new Event('change',{bubbles:true}));document.getElementById('gameful-toggle').click()})()`);
  const open = await evaluate(`({header:document.getElementById('gameful-title').textContent,
    focus:document.activeElement?.id,
    locked:document.getElementById('gameful-mode').disabled,
    claim:document.getElementById('gameful-claim').textContent})`);
  assert.equal(open.header, "Checking execution evidence");
  assert.equal(open.focus, "gameful-title");
  assert.equal(open.locked, true);

  // Keyboard-only path: heading -> True -> False -> Enter -> explanation.
  await key("Tab"); await key("Tab");
  const falseFocused = await evaluate("document.activeElement?.dataset?.gamefulAnswer");
  assert.equal(falseFocused, "false", "Tab from heading should reach false answer");
  await key("Enter");
  const grade = await evaluate(`({feedback:document.getElementById('gameful-result').textContent,
    focus:document.activeElement?.id,explanation:document.getElementById('gameful-explanation').textContent,
    source:document.getElementById('gameful-source').href,nextHidden:document.getElementById('gameful-next').hidden})`);
  assert.match(grade.feedback, /Correct/);
  assert.equal(grade.focus, "gameful-explanation");
  assert.match(grade.explanation, /public command round-trip/);
  assert.ok(grade.source.endsWith("/docs/PROJECT_STATUS.md"));
  assert.equal(grade.nextHidden, false);

  // Keyboard follows explanation -> source -> next; Enter opens second example.
  await key("Tab"); await key("Tab");
  assert.equal(await evaluate("document.activeElement?.id"), "gameful-next");
  await key("Enter");
  const remix = await evaluate(`({focus:document.activeElement?.id,
    heading:document.getElementById('gameful-title').textContent,
    claim:document.getElementById('gameful-claim').textContent})`);
  assert.equal(remix.focus, "gameful-title");
  assert.match(remix.heading, /second example/);
  assert.match(remix.claim, /stronger evidence/);

  // The same question/explanation survives the voluntary mode switch.
  await evaluate(`(()=>{document.getElementById('gameful-toggle').click();
    const mode=document.getElementById('gameful-mode');
    mode.value='playful';mode.dispatchEvent(new Event('change',{bubbles:true}));
    document.getElementById('gameful-toggle').click();
    document.querySelector('[data-gameful-answer="false"]').click()})()`);
  const playful = await evaluate(`({heading:document.getElementById('gameful-title').textContent,
    explanation:document.getElementById('gameful-explanation').textContent,
    focus:document.activeElement?.id,claim:document.getElementById('gameful-claim').textContent})`);
  assert.equal(playful.heading, "THE RECEIPT IMPOSTOR");
  assert.equal(playful.claim, open.claim);
  assert.equal(playful.explanation, grade.explanation);
  assert.equal(playful.focus, "gameful-explanation");
  console.log("PASS: phone-width Chromium keyboard/focus smoke; factual parity and master control preserved.");
} finally {
  for (const p of pending.values()) { clearTimeout(p.timer); p.reject(Error("Browser test shutting down")); }
  pending.clear();
  if (socket) socket.close();
  chrome.kill("SIGTERM");
  await new Promise(resolve => server.close(resolve));
}
