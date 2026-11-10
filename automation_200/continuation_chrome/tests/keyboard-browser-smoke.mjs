// AUTO-08 source integration probe: REAL headless Chromium keyboard dispatch.
// Runs in an inert about:blank contenteditable fixture, not chatgpt.com.
// Evidence class: browser keyboard integration, NOT signed-in account acceptance.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const profile = await mkdtemp(join(tmpdir(), "cf0-auto08-keyboard-"));
// Let Chrome choose a free ephemeral port. Chromium writes it to the
// private temporary profile's DevToolsActivePort file once it is ready.
const chrome = spawn(process.env.CF0_CHROME || "google-chrome", [
  "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage",
  "--no-first-run", "--no-default-browser-check", "--no-proxy-server",
  "--remote-debugging-port=0", "--user-data-dir=" + profile, "about:blank"
], { stdio: ["ignore","ignore","pipe"] });
let socket, nextId = 0, startupError = null, stderr = "";
chrome.on("error", error => { startupError = error; });
chrome.stderr.on("data", chunk => { stderr = (stderr + String(chunk)).slice(-2500); });
const pending = new Map();

async function awaitDebugger() {
  for (let i = 0; i < 450; i++) {
    if (startupError || chrome.exitCode !== null || chrome.signalCode !== null)
      throw Error("Chrome exited before debugger: "+(startupError?.message || chrome.exitCode || chrome.signalCode)+". "+stderr.slice(-900));
    try {
      const active = await readFile(join(profile, "DevToolsActivePort"), "utf8");
      const port = Number(active.split(/\r?\n/)[0]);
      if (!Number.isSafeInteger(port) || port < 1 || port > 65535) throw Error("Invalid Chrome port");
      const response = await fetch("http://127.0.0.1:" + port + "/json");
      if (response.ok) {
        const pages = await response.json();
        const page = pages.find(x => x.type === "page");
        if (page?.webSocketDebuggerUrl) return page.webSocketDebuggerUrl;
      }
    } catch {}
    await pause(100);
  }
  throw Error("Chrome debugger not available after 45 seconds. "+stderr.slice(-900));
}
function cd(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++nextId;
    const timer = setTimeout(() => { pending.delete(id); reject(Error("CDP timed out: " + method)); }, 12000);
    pending.set(id, { resolve, reject, timer });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
async function evaluate(expression) {
  const result = await cd("Runtime.evaluate", { expression, returnByValue:true });
  if (result.exceptionDetails) throw Error(JSON.stringify(result.exceptionDetails));
  return result.result?.value;
}
try {
  socket = new WebSocket(await awaitDebugger());
  await new Promise((resolve, reject) => {socket.onopen = resolve; socket.onerror = reject;});
  socket.onmessage = ev => {
    const msg = JSON.parse(ev.data);
    const waiting = pending.get(msg.id);
    if (!waiting) return;
    clearTimeout(waiting.timer);
    pending.delete(msg.id);
    msg.error ? waiting.reject(Error(JSON.stringify(msg.error))) : waiting.resolve(msg.result);
  };
  await cd("Runtime.enable");
  const setupDOM = () => {
    document.body.innerHTML = '<div id="composer" contenteditable="true" role="textbox"></div>';
    window.__cfProbe = {submissions:[],keyEvents:[]};
    const composer = document.getElementById("composer");
    composer.addEventListener("keydown", ev => {
      window.__cfProbe.keyEvents.push(ev.key);
      if (ev.key === "Enter") {
        window.__cfProbe.submissions.push(composer.innerText.trim());
        ev.preventDefault();
        composer.textContent = "";
      }
    });
    composer.focus();
    return document.activeElement === composer;
  };
  const ready = await evaluate("(" + setupDOM.toString() + ")()");
  assert.equal(ready, true, "Synthetic editor must have focus");
  const source = await readFile(new URL("../background.js", import.meta.url), "utf8");
  assert.match(source, /const text=bootstrap\?BOOTSTRAP_TEXT:CONTINUE_TEXT/);
  assert.match(source, /Input\.insertText',\{text\}/);
  assert.match(source, /type:'rawKeyDown'[\s\S]*type:'keyUp'/);
  // Exactly the three commands currently used by the owner-local extension:
  // insertText('continue') + physical Enter key-down and key-up.
  await cd("Input.insertText", {text:"continue"});
  await cd("Input.dispatchKeyEvent", {type:"rawKeyDown",key:"Enter",code:"Enter",windowsVirtualKeyCode:13,nativeVirtualKeyCode:13});
  await cd("Input.dispatchKeyEvent", {type:"keyUp",key:"Enter",code:"Enter",windowsVirtualKeyCode:13,nativeVirtualKeyCode:13});
  const result = await evaluate("({submissions:window.__cfProbe.submissions,keyEvents:window.__cfProbe.keyEvents,remainingDraft:document.getElementById('composer').innerText.trim()})");
  assert.deepEqual(result.submissions, ["continue"], "One Enter must submit literal continue ONCE");
  assert.deepEqual(result.keyEvents, ["Enter"], "Do not add another Enter or character event");
  assert.equal(result.remainingDraft, "", "No duplicate command or leftover draft");
  console.log("PASS: one real Chromium contenteditable Enter sends exactly one literal continue.");
} finally {
  for (const entry of pending.values()) { clearTimeout(entry.timer); entry.reject(Error("Probe stopped")); }
  pending.clear();
  if (socket) socket.close();
  chrome.kill("SIGTERM");
  await rm(profile, {recursive:true,force:true,maxRetries:3,retryDelay:100}).catch(()=>{});
}
