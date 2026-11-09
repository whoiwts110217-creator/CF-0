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
  if (keyName === "Enter") {
    // CDP Enter needs a char event on some Chromium versions to activate buttons.
    await send("Input.dispatchKeyEvent", { type: "rawKeyDown", key: keyName, code, windowsVirtualKeyCode: keyCode, nativeVirtualKeyCode: keyCode });
    await send("Input.dispatchKeyEvent", { type: "char", key: keyName, code, text: "\r", unmodifiedText: "\r", windowsVirtualKeyCode: keyCode, nativeVirtualKeyCode: keyCode });
  } else {
    await send("Input.dispatchKeyEvent", { type: "keyDown", key: keyName, code, windowsVirtualKeyCode: keyCode, nativeVirtualKeyCode: keyCode });
  }
  await send("Input.dispatchKeyEvent", { type: "keyUp", key: keyName, code, windowsVirtualKeyCode: keyCode, nativeVirtualKeyCode: keyCode });
}
async function accessibilityNodes() {
  const response = await send("Accessibility.getFullAXTree");
  return (response.result?.nodes || []).filter(node => !node.ignored)
    .map(node => ({ role: node.role?.value || "", name: node.name?.value || "" }));
}
function assertAccessible(nodes, role, name) {
  assert.ok(nodes.some(node => node.role.toLowerCase() === role.toLowerCase() && node.name === name),
    "Expected accessibility tree "+role+" named "+JSON.stringify(name)+", found: "+
    JSON.stringify(nodes.filter(node => node.name.includes(name.slice(0,12))).slice(0,10)));
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
  await send("Accessibility.enable");
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
  // Browser accessibility tree, not a VoiceOver or Safari screen-reader run.
  const initialAx = await accessibilityNodes();
  assertAccessible(initialAx, "combobox", "Presentation mode");
  assertAccessible(initialAx, "checkbox", "Larger lesson text");
  assertAccessible(initialAx, "button", "Start brainpower quest");
  assert.ok(initialAx.some(node => node.role.toLowerCase() === "switch" &&
    node.name.includes("Master automation switch") && node.name.includes("unavailable")),
    "Disconnected owner master switch must be labelled and discoverable");
  console.log("PASS: initial quiz controls and disconnected master have accessible names.");

  await evaluate(`(()=>{const m=document.getElementById('gameful-mode');m.value='plain';m.dispatchEvent(new Event('change',{bubbles:true}));document.getElementById('gameful-toggle').click()})()`);
  const open = await evaluate(`({header:document.getElementById('gameful-title').textContent,
    focus:document.activeElement?.id,
    locked:document.getElementById('gameful-mode').disabled,
    claim:document.getElementById('gameful-claim').textContent})`);
  assert.equal(open.header, "Checking execution evidence");
  assert.equal(open.focus, "gameful-title");
  assert.equal(open.locked, true);
  const openedAx = await accessibilityNodes();
  assertAccessible(openedAx, "heading", "Checking execution evidence");
  assertAccessible(openedAx, "button", "TRUE");
  assertAccessible(openedAx, "button", "FALSE");
  assert.ok(openedAx.some(node => node.name.includes(open.claim)),
    "Current evidence claim should be exposed in the accessibility tree");

  // Keyboard-only path: heading -> True -> False -> Enter -> explanation.
  await key("Tab"); await key("Tab");
  const falseFocused = await evaluate("document.activeElement?.dataset?.gamefulAnswer");
  assert.equal(falseFocused, "false", "Tab from heading should reach false answer");
  await key("Enter");
  await waitFor("document.getElementById('gameful-result').textContent.includes('Correct')", "keyboard answer feedback");
  const grade = await evaluate(`({feedback:document.getElementById('gameful-result').textContent,
    focus:document.activeElement?.id,explanation:document.getElementById('gameful-explanation').textContent,
    source:document.getElementById('gameful-source').href,nextHidden:document.getElementById('gameful-next').hidden})`);
  assert.match(grade.feedback, /Correct/);
  assert.equal(grade.focus, "gameful-explanation");
  assert.match(grade.explanation, /public command round-trip/);
  assert.ok(grade.source.endsWith("/docs/PROJECT_STATUS.md"));
  assert.equal(grade.nextHidden, false);
  const gradedAx = await accessibilityNodes();
  assert.ok(gradedAx.some(node => node.name.includes("public command round-trip")),
    "Evidence explanation must remain in the accessibility tree after grading");
  assert.ok(gradedAx.some(node => node.role.toLowerCase() === "link" &&
    node.name.includes("Read the project evidence")),
    "Evidence-source link must have a navigable accessible name");

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

  // Large-text readability preference: changing size must preserve source facts.
  await evaluate("(()=>{const box=document.getElementById('gameful-large-text');box.checked=true;box.dispatchEvent(new Event('change',{bubbles:true}))})()");
  const sizeChange = await evaluate(String.raw`(()=>({
    enabled:document.getElementById('learning-lab').dataset.largeText,
    claim:document.getElementById('gameful-claim').textContent,
    explanation:document.getElementById('gameful-explanation').textContent,
    claimFont:parseFloat(getComputedStyle(document.getElementById('gameful-claim')).fontSize),
    explanationFont:parseFloat(getComputedStyle(document.getElementById('gameful-explanation')).fontSize)
  }))()`);
  assert.equal(sizeChange.enabled,"true","Large text must be an accessible, local display state");
  assert.equal(sizeChange.claim,open.claim,"Large text must not alter the question");
  assert.equal(sizeChange.explanation,grade.explanation,"Large text must not alter answer evidence");
  assert.ok(sizeChange.claimFont >= 21 && sizeChange.explanationFont >= 19,"Large text option must increase lesson fonts");
  console.log("Large-text readability:",JSON.stringify(sizeChange));

  // Responsive and touch-target acceptance across four iPhone-like CSS widths.
  // Browser engine remains Chromium; this is NOT physical iPhone Safari verification.
  for (const width of [320, 360, 390, 430]) {
    await send("Emulation.setDeviceMetricsOverride", { width, height: 844, deviceScaleFactor: 3, mobile: true });
    await pause(100);
    await evaluate("document.documentElement.dataset.cfTestWidth = "+width);
    const measures = await evaluate(String.raw`(() => {
      const root = document.getElementById("learning-lab");
      const bounds = root.getBoundingClientRect();
      const targetWidth = Number(document.documentElement.dataset.cfTestWidth);
      const outliers = Array.from(document.querySelectorAll("body *"))
        .filter(el => {
          const rect = el.getBoundingClientRect();
          return el.getClientRects().length && rect.right > targetWidth + 2 && rect.width > 0;
        }).slice(0, 20).map(el => {
          const rect = el.getBoundingClientRect();
          return {tag:el.tagName,id:el.id,classes:String(el.className).slice(0,80),left:Math.round(rect.left),right:Math.round(rect.right)};
        });

      const selectors = "#gameful-toggle,#gameful-mode,.gameful-choices button,#gameful-next,#gameful-source,.gameful-note a";
      const targets = Array.from(root.querySelectorAll(selectors))
        .filter(el => el.getClientRects().length && getComputedStyle(el).visibility !== "hidden")
        .map(el => {
          const r=el.getBoundingClientRect();
          return {tag:el.tagName,id:el.id||el.textContent.trim().slice(0,25),width:Math.round(r.width),height:Math.round(r.height),left:Math.round(r.left),right:Math.round(r.right)};
        });
      return {viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,
        labLeft:bounds.left,labRight:bounds.right,labClient:root.clientWidth,labScroll:root.scrollWidth,
        targets,outliers,modeFont:getComputedStyle(document.getElementById("gameful-mode")).fontSize};
    })()`);
    console.log("Phone-width touch targets:",JSON.stringify({width,...measures}));
    if (measures.viewport !== width || measures.scrollWidth > width) {
      console.warn("Existing full dashboard has overflow at configured width",JSON.stringify({width,innerWidth:measures.viewport,scrollWidth:measures.scrollWidth,outliers:measures.outliers}));
    }
    assert.equal(measures.viewport, width, "Full dashboard viewport should match phone width");
    assert.ok(measures.scrollWidth <= width + 1, "Full dashboard must not overflow horizontally at "+width);
    assert.ok(measures.labLeft >= -2 && measures.labRight <= width+2,"Lab must fit viewport at "+width);
    assert.ok(measures.labScroll <= measures.labClient+2,"Lab content must not overflow horizontally at "+width);
    assert.ok(measures.targets.length >= 6,"Required touch targets must be visible at "+width);
    for (const target of measures.targets) {
      assert.ok(target.width >= 44 && target.height >= 44,"Touch target must be at least 44x44 at "+width+": "+JSON.stringify(target));
      assert.ok(target.left >= -2 && target.right <= width+2,"Target must stay inside viewport at "+width+": "+JSON.stringify(target));
    }
    assert.ok(parseFloat(measures.modeFont) >= 16,"Select text must avoid iOS autofocus zoom at "+width);
    assert.equal(await evaluate("document.getElementById('learning-lab').dataset.largeText"),"true","Large text remains on throughout responsive check");

  }
  // System contrast is an OS/browser preference, not stored or inferred from user data.
  await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-contrast", value: "more" }] });
  const highContrast = await evaluate(String.raw`(()=>({
    enabled:matchMedia("(prefers-contrast: more)").matches,
    claimColor:getComputedStyle(document.getElementById("gameful-claim")).color,
    explainColor:getComputedStyle(document.getElementById("gameful-explanation")).color,
    pageWidth:document.documentElement.scrollWidth,viewport:innerWidth
  }))()`);
  console.log("High-contrast preference:",JSON.stringify(highContrast));
  assert.equal(highContrast.enabled,true,"Chromium should emulate increased contrast");
  assert.equal(highContrast.explainColor,"rgb(255, 255, 255)","Source explanation must receive high-contrast text color");
  assert.ok(highContrast.pageWidth<=highContrast.viewport+1,"High contrast must preserve responsive layout");
  await send("Emulation.setEmulatedMedia", { features: [] });

  // Optional owner-device instructions do not assert a completed physical iPhone test.
  const deviceGuide = await evaluate(`(()=>{const d=document.getElementById("gameful-device-check");return {
    exists:!!d,open:d?.open,steps:d?.querySelectorAll("li").length,
    text:d?.textContent||"",scrollWidth:document.documentElement.scrollWidth
  }})()`);
  assert.equal(deviceGuide.exists,true,"On-device acceptance help should exist");
  assert.equal(deviceGuide.open,false,"On-device acceptance help should be collapsed by default");
  assert.equal(deviceGuide.steps,4,"Guide should have short, reproducible checks");
  assert.match(deviceGuide.text,/VoiceOver/);
  assert.match(deviceGuide.text,/does not automatically verify or report/i);
  await evaluate("document.querySelector('#gameful-device-check summary').click()");
  const openGuide = await evaluate(`(()=>({open:document.getElementById("gameful-device-check").open,
    viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,
    summaryHeight:document.querySelector("#gameful-device-check summary").getBoundingClientRect().height}))()`);
  assert.equal(openGuide.open,true,"Guide opens without saving or submitting anything");
  assert.ok(openGuide.summaryHeight >= 44,"On-device guide summary has a usable touch target");
  assert.ok(openGuide.scrollWidth <= openGuide.viewport + 1,"Expanded guide must not cause sideways scrolling");
  await evaluate("document.querySelector('#gameful-device-check summary').click()");
  assert.equal(await evaluate("document.getElementById('gameful-device-check').open"),false);
  console.log("PASS: optional device guide is collapsed by default and responsive when expanded.");

  // Restore source smoke defaults before closing browser.
  await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 3, mobile: true });

  console.log("PASS: phone-width Chromium keyboard/focus smoke; factual parity and master control preserved.");
} finally {
  for (const p of pending.values()) { clearTimeout(p.timer); p.reject(Error("Browser test shutting down")); }
  pending.clear();
  if (socket) socket.close();
  chrome.kill("SIGTERM");
  await new Promise(resolve => server.close(resolve));
}
