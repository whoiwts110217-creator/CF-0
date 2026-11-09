// Source-only public homepage 390px smoke. Real iPhone Safari remains separately unverified.
// Uses the existing Chromium CDP approach; no external services or project/account data.
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { spawn } from "node:child_process";
import { readFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const pageFiles = new Map([
  ["/", ["index.html", "text/html; charset=utf-8"]],
  ["/index.html", ["index.html", "text/html; charset=utf-8"]],
  ["/i18n/home.mjs", ["i18n/home.mjs", "text/javascript; charset=utf-8"]]
]);
const server = createServer(async (request, response) => {
  const url = new URL(request.url || "/", "http://127.0.0.1");
  const item = pageFiles.get(url.pathname);
  if (!item) { response.writeHead(404); response.end("Not found"); return; }
  try {
    const data = await readFile(new URL("../" + item[0], import.meta.url));
    response.writeHead(200, { "Content-Type": item[1], "Cache-Control": "no-store" });
    response.end(data);
  } catch (error) {
    response.writeHead(500); response.end("Read failure: " + error.message);
  }
});
await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
const origin = "http://127.0.0.1:" + server.address().port;
const port = 9400 + (process.pid % 800);
const browser = spawn(process.env.CF0_CHROME || "google-chrome", [
  "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
  "--no-first-run", "--remote-debugging-port=" + port,
  "--user-data-dir=" + join(tmpdir(), "cf0-home-mobile-" + process.pid),
  "about:blank"
], { stdio: "ignore" });
let socket = null, seq = 0;
const waiting = new Map();

async function target() {
  for (let i = 0; i < 120; i++) {
    try {
      const response = await fetch("http://127.0.0.1:" + port + "/json");
      if (response.ok) {
        const pages = await response.json();
        const page = pages.find(x => x.type === "page" && x.webSocketDebuggerUrl);
        if (page) return page.webSocketDebuggerUrl;
      }
    } catch {}
    await sleep(100);
  }
  throw Error("Cannot connect to headless Chromium CDP");
}
async function send(method, params={}) {
  return await new Promise((resolve, reject) => {
    const id = ++seq;
    const timeout = setTimeout(() => { waiting.delete(id); reject(Error("CDP timeout: "+method)); }, 12000);
    waiting.set(id, { resolve, reject, timeout });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
async function evaluate(expression) {
  const response = await send("Runtime.evaluate", { expression, returnByValue:true, awaitPromise:true });
  if (response.result?.exceptionDetails) throw Error("Browser exception: "+JSON.stringify(response.result.exceptionDetails));
  return response.result?.result?.value;
}
async function waitFor(expression, label) {
  for (let i = 0; i < 90; i++) {
    if (await evaluate(expression)) return;
    await sleep(100);
  }
  throw Error("Timed out: " + label);
}
try {
  socket = new WebSocket(await target());
  await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
  socket.onmessage = event => {
    const msg=JSON.parse(event.data);
    const w=waiting.get(msg.id);
    if (!w) return;
    clearTimeout(w.timeout); waiting.delete(msg.id);
    if (msg.error) w.reject(Error(JSON.stringify(msg.error)));
    else w.resolve(msg);
  };
  await send("Page.enable");
  await send("Runtime.enable");
  await send("Emulation.setDeviceMetricsOverride", {
    width:390,height:844,deviceScaleFactor:3,mobile:true
  });
  await send("Page.navigate", { url:origin+"/?lang=es" });
  await waitFor(
    "document.readyState === 'complete' && document.documentElement.lang === 'es' && document.querySelector('h1')?.textContent.includes('Haz comprensible')",
    "Spanish homepage"
  );
  const state = await evaluate(`(() => {
    const viewport=innerWidth, doc=document.documentElement;
    const rect=id=>{const r=document.querySelector(id).getBoundingClientRect();return {left:r.left,right:r.right,width:r.width,height:r.height};};
    return {viewport,scrollWidth:doc.scrollWidth,bodyWidth:document.body.scrollWidth,
      hero:document.querySelector('h1').textContent.trim(),
      evidence:document.querySelector('#evidence h2')?.textContent.trim(),
      demo:rect('.hero .btn'),menu:rect('.more-nav > summary'),lang:rect('.language-picker > summary'),
      demoHref:document.querySelector('.hero .btn')?.getAttribute('href')};
  })()`);
  console.log("390px Spanish page:", JSON.stringify(state));
  assert.equal(state.viewport, 390, "Mobile viewport meta must respect 390 CSS px");
  assert.ok(state.scrollWidth <= 392 && state.bodyWidth <= 392, "Initial homepage must not scroll horizontally");
  assert.ok(state.demo.left >= -2 && state.demo.right <= 392 && state.demo.height >= 40, "Free demo button must fit and be tappable");
  assert.ok(state.menu.left >= -2 && state.menu.right <= 392, "More menu must be inside viewport");
  assert.ok(state.lang.left >= -2 && state.lang.right <= 392, "Language picker must fit viewport");
  assert.ok(state.evidence.includes("Todavía en pruebas"), "New evidence heading must translate");
  assert.equal(state.demoHref,"./mission-control/#learning-lab");

  const menu = await evaluate(`(() => {
    const d=document.querySelector('.more-nav');d.open=true;
    const r=d.querySelector('.nav-extra').getBoundingClientRect();
    return {viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,
      left:r.left,right:r.right,width:r.width,visible:r.width>0,
      legacyLinks:[...d.querySelectorAll('a')].map(x=>x.getAttribute('href'))};
  })()`);
  console.log("390px expanded More menu:",JSON.stringify(menu));
  assert.ok(menu.scrollWidth <= 392, "Opening More menu must not cause horizontal scrolling");
  assert.ok(menu.left >= -2 && menu.right <= 392, "Open More menu must fit mobile screen");
  assert.ok(menu.legacyLinks.includes("./mission-control/") && menu.legacyLinks.some(x=>x?.includes("/ai_tracker")), "Historic links remain reachable");

  await evaluate(`(() => {
    document.querySelector('[data-set-language="en"]').click();
    return true;
  })()`);
  await waitFor("document.documentElement.lang === 'en' && document.querySelector('h1')?.textContent.includes('Make the complicated')","English language switch");
  const englishLayout = await evaluate(`(() => {
    const viewport=innerWidth;
    const outliers=[...document.querySelectorAll('body *')].map(e=>({e,r:e.getBoundingClientRect()}))
      .filter(({e,r})=>r.width>0 && (r.right>viewport+2 || r.left < -2))
      .slice(0,15).map(({e,r})=>({tag:e.tagName,id:e.id,cls:e.className?.toString().slice(0,80),left:r.left,right:r.right,width:r.width}));
    return {viewport,scrollWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth,
      menuOpen:document.querySelector('.more-nav').open,lang:document.documentElement.lang,outliers};
  })()`);
  console.log("390px English layout after switch:", JSON.stringify(englishLayout));
  assert.ok(englishLayout.viewport<=392 && englishLayout.scrollWidth<=392,"Language switching must not expand the 390px layout viewport");
  console.log("PASS: 390px Chromium first visit, Spanish evidence, no overflow, More menu, free demo and English switch.");
} finally {
  try { socket?.close(); } catch {}
  for (const [id,w] of waiting) { clearTimeout(w.timeout); w.reject(Error("Browser shutdown")); waiting.delete(id); }
  browser.kill("SIGTERM");
  await new Promise(resolve => server.close(resolve));
}
