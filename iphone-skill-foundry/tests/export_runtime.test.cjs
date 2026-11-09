"use strict";
/* Browser-less source interaction tests: simulated Safari APIs, no network or accounts. */
const assert = require("node:assert/strict");
const test = require("node:test");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]);
assert.equal(scripts.length, 2, "Expected deterministic generator and inline UI script");

function harness(options = {}) {
  const events = new Map();
  const elements = new Map();
  const clicks = [];
  const revocations = [];
  const scheduled = [];
  const mode = {value: "pack", checked: true};
  const get = id => {
    if (!elements.has(id)) {
      elements.set(id, {
        id, value: "", textContent: "", innerHTML: "", disabled: false, hidden: false,
        addEventListener(name, callback) { events.set(id + ":" + name, callback); },
        appendChild(child) { if (id === "previewFile" && !this.value) this.value = child.value; },
        scrollIntoView() {},
        setAttribute() {},
        remove() {},
      });
    }
    return elements.get(id);
  };
  const document = {
    getElementById: get,
    querySelector() { return mode; },
    createElement(tag) {
      if (tag === "a") return {
        download: "", href: "", remove() {},
        click() {
          if (options.anchorThrows) throw Error("blocked anchor click");
          clicks.push({name: this.download, href: this.href});
        },
      };
      return {textContent: "", value: "", remove() {}};
    },
    body: {appendChild() {}},
    addEventListener() {},
  };
  const navigator = {
    canShare() { return options.canShare === true; },
    async share() {
      if (options.shareError) throw Object.assign(new Error("Share rejected"), {name: options.shareError});
    },
    clipboard: {async writeText() {}},
  };
  const url = {
    createObjectURL() {
      if (options.objectUrlThrows) throw Error("object URL blocked");
      return "blob:test";
    },
    revokeObjectURL(href) { revocations.push(href); },
  };
  class FakeFile extends Blob {
    constructor(chunks, name, opts) { super(chunks, opts); this.name = name; }
  }
  const context = vm.createContext({
    module: {exports: {}}, TextEncoder, TextDecoder, Uint8Array, Uint32Array, DataView,
    Blob, File: options.noFile ? undefined : FakeFile,
    URL: url, URLSearchParams, console, document, navigator, location: {search: "", protocol: "http:"},
    localStorage: {getItem() {return null;}, setItem() {}},
    window: {addEventListener() {}}, setTimeout(fn, ms) {scheduled.push({fn, ms});},
  });
  vm.runInContext(scripts[0], context, {filename: "generator.js"});
  vm.runInContext(scripts[1], context, {filename: "ui.js"});
  return {
    context, clicks, revocations, scheduled,
    status() {return get("feedback").textContent;},
    async fire(id, kind = "click") {
      const fn = events.get(id + ":" + kind);
      assert.equal(typeof fn, "function", id + " handler missing");
      await fn({preventDefault() {}, target: {files: []}});
    },
  };
}

test("ZIP is a non-empty actual ZIP archive", async () => {
  const h = harness();
  const b = h.context.SkillFoundry.zip({"test/SKILL.md": "Hello", "test/EVALS.json": "{}"});
  const a = new Uint8Array(await b.arrayBuffer());
  assert.equal(Buffer.from(a.subarray(0,4)).toString("hex"), "504b0304");
  assert.ok(a.length > 100);
});

test("ZIP download makes a request, not a saved-file claim", async () => {
  const h = harness();
  await h.fire("downloadZip");
  assert.equal(h.clicks.length, 1);
  assert.match(h.status(), /download requested/i);
  assert.doesNotMatch(h.status(), /download complete|saved successfully/i);
  assert.ok(h.scheduled.some(x => x.ms >= 60000));
});

test("blocked object URL fails visibly", async () => {
  const h = harness({objectUrlThrows: true});
  await h.fire("downloadZip");
  assert.equal(h.clicks.length, 0);
  assert.match(h.status(), /could not start/i);
});

test("failed anchor click revokes URL and leaves recovery instructions", async () => {
  const h = harness({anchorThrows: true});
  await h.fire("downloadZip");
  assert.equal(h.revocations.length, 1);
  assert.match(h.status(), /Try Share \/ Files/i);
});

test("iPhone share path returns cautious confirmation only", async () => {
  const h = harness({canShare: true});
  await h.fire("shareZip");
  assert.equal(h.clicks.length, 0);
  assert.match(h.status(), /Confirm the ZIP was saved/i);
});

test("cancelled iOS share does not download on its own", async () => {
  const h = harness({canShare: true, shareError: "AbortError"});
  await h.fire("shareZip");
  assert.equal(h.clicks.length, 0);
  assert.match(h.status(), /Share cancelled/i);
});

test("failed iOS share shows explicit fallback but does not surprise-download", async () => {
  const h = harness({canShare: true, shareError: "NotAllowedError"});
  await h.fire("shareZip");
  assert.equal(h.clicks.length, 0);
  assert.match(h.status(), /Share failed/i);
});

test("unsupported file share falls back to a visible download request", async () => {
  const h = harness({canShare: false});
  await h.fire("shareZip");
  assert.equal(h.clicks.length, 1);
  assert.match(h.status(), /download requested/i);
});

test("missing File API falls back without crashing", async () => {
  const h = harness({noFile: true, canShare: true});
  await h.fire("shareZip");
  assert.equal(h.clicks.length, 1);
  assert.match(h.status(), /download requested/i);
});

test("unsupported share and blocked download provide recovery guidance", async () => {
  const h = harness({noFile: true, objectUrlThrows: true});
  await h.fire("shareZip");
  assert.equal(h.clicks.length, 0);
  assert.match(h.status(), /Sharing and downloads are unavailable/i);
});

test("selected individual file download works in isolation", async () => {
  const h = harness();
  await h.fire("downloadSelected");
  assert.equal(h.clicks.length, 1);
  assert.match(h.status(), /Selected file download requested/i);
});

test("selected file export failure reports fallback", async () => {
  const h = harness({objectUrlThrows: true});
  await h.fire("downloadSelected");
  assert.match(h.status(), /Selected file download could not start/i);
});

test("editable JSON export failure reports fallback", async () => {
  const h = harness({objectUrlThrows: true});
  await h.fire("exportDraft");
  assert.match(h.status(), /Editable-project export could not start/i);
});

test("existing forge, preview and test controls remain wired", async () => {
  const h = harness();
  await h.fire("selfTest");
  assert.match(h.context.document.getElementById("testResults").textContent, /checks passed/);
  await h.fire("skillForm", "submit");
  assert.match(h.status(), /Forged \d+ files locally/);
});
