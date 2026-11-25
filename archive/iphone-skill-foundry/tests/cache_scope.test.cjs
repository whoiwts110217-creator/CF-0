"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const swSource = fs.readFileSync(path.join(__dirname, "..", "sw.js"), "utf8");

function serviceWorker() {
  const handlers = new Map();
  const stores = new Map();
  const deleted = [];
  const network = [];
  let claimed = false;

  function keyOf(request) { return typeof request === "string" ? request : request.url; }
  const caches = {
    async keys() { return [...stores.keys()]; },
    async delete(name) { deleted.push(name); return stores.delete(name); },
    async open(name) {
      if (!stores.has(name)) stores.set(name, new Map());
      const store = stores.get(name);
      return {
        async addAll(files) { for (const file of files) store.set(file, {url: file}); },
        async match(request) { return store.get(keyOf(request)); },
        async put(request, value) { store.set(keyOf(request), value); },
      };
    },
    async match() { throw Error("Origin-wide caches.match must not be used"); },
  };
  const self = {
    location: {origin: "https://example.invalid"},
    addEventListener(name, callback) { handlers.set(name, callback); },
    skipWaiting() {},
    clients: {async claim() { claimed = true; }},
  };
  function fetch(request) {
    network.push(keyOf(request));
    return Promise.resolve({
      ok: true, body: "fresh-network-response",
      clone() { return {ok: true, body: "fresh-network-response"}; },
    });
  }
  vm.runInNewContext(swSource, {self, caches, fetch, URL, Promise, console}, {filename: "sw.js"});
  return {
    caches, stores, deleted, network, handlers,
    get claimed() {return claimed;},
    async dispatch(name, request) {
      const callback = handlers.get(name);
      assert.equal(typeof callback, "function", "Missing " + name + " listener");
      const waiting = [];
      let response;
      const event = {
        request,
        waitUntil(p) { waiting.push(Promise.resolve(p)); },
        respondWith(p) { response = Promise.resolve(p); },
      };
      callback(event);
      const body = response ? await response : undefined;
      await Promise.all(waiting);
      return {body, handled: !!response};
    },
  };
}

test("activation deletes ONLY old Foundry caches, preserves unrelated app caches", async () => {
  const sw = serviceWorker();
  sw.stores.set("mission-control-v12", new Map([["dashboard", "preserved"]]));
  sw.stores.set("cf0-habit-automator-v3", new Map([["routine", "preserved"]]));
  sw.stores.set("cf-skill-foundry-v0.2.4", new Map([["old", "old"]]));
  sw.stores.set("cf-skill-foundry-v0.2.5", new Map([["live", "current"]]));
  sw.stores.set("CF-skill-foundry-lookalike", new Map([["asset", "unowned"]]));
  await sw.dispatch("activate");
  assert.deepEqual(sw.deleted, ["cf-skill-foundry-v0.2.4"]);
  assert.equal(sw.stores.get("mission-control-v12").get("dashboard"), "preserved");
  assert.equal(sw.stores.get("cf0-habit-automator-v3").get("routine"), "preserved");
  assert.equal(sw.stores.get("cf-skill-foundry-v0.2.5").get("live"), "current");
  assert.equal(sw.stores.get("CF-skill-foundry-lookalike").get("asset"), "unowned");
  assert.equal(sw.claimed, true);
});

test("install precaches Foundry pages in the current scoped cache", async () => {
  const sw = serviceWorker();
  await sw.dispatch("install");
  const files = sw.stores.get("cf-skill-foundry-v0.2.5");
  assert.ok(files.has("./index.html"));
  assert.ok(files.has("./manifest.webmanifest"));
  assert.ok(files.has("./apple-touch-icon.png"));
});

test("fetch does not read a cached response from another application", async () => {
  const sw = serviceWorker();
  const request = {method: "GET", url: "https://example.invalid/skill-foundry/index.html"};
  sw.stores.set("mission-control-v12", new Map([[request.url, {body: "foreign-poisoned-response"}]]));
  const first = await sw.dispatch("fetch", request);
  assert.equal(first.handled, true);
  assert.equal(first.body.body, "fresh-network-response");
  assert.equal(sw.network.length, 1);
  const second = await sw.dispatch("fetch", request);
  assert.equal(second.body.body, "fresh-network-response");
  assert.equal(sw.network.length, 1, "second read should hit own cache");
  assert.equal(sw.stores.get("mission-control-v12").get(request.url).body, "foreign-poisoned-response");
});

test("does not intercept POSTs or cross-origin assets", async () => {
  const sw = serviceWorker();
  const post = await sw.dispatch("fetch", {method: "POST", url: "https://example.invalid/skill-foundry/"});
  const remote = await sw.dispatch("fetch", {method: "GET", url: "https://third-party.invalid/a.js"});
  assert.equal(post.handled, false);
  assert.equal(remote.handled, false);
  assert.deepEqual(sw.network, []);
});
