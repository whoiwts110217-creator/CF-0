import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { COPY, LOCALES } from "./home.mjs";

const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
const locales = ["es", "fr", "pt"];

test("English is the default without any interruption or automatic detection", () => {
  assert.match(html, /<html lang="en">/);
  assert.match(html, /id="current-language">EN<\/span>/);
  assert.match(html, /<details id="language-picker"/);
  assert.match(html, /<script type="module" src="\.\/i18n\/home\.mjs"/);
  assert.doesNotMatch(html, /<dialog|autoplay|window\.onload=/i);
  assert.doesNotMatch(readFileSync(new URL("./home.mjs", import.meta.url), "utf8"), /navigator\.language|geolocation|fetch\(/);
  assert.equal(LOCALES.en, "English");
});

test("All translated texts have nonempty Spanish, French and Portuguese values", () => {
  assert.ok(Object.keys(COPY).length >= 50, "Do not silently drop major site sections");
  for (const [english, translations] of Object.entries(COPY)) {
    assert.ok(english.length, "No empty English keys");
    for (const code of locales) {
      assert.equal(typeof translations[code], "string", english + " missing " + code);
      assert.ok(translations[code].trim().length, english + " empty " + code);
    }
  }
});

test("Visible homepage copy is in the translation catalog, except names and language names", () => {
  const body = html.slice(html.indexOf("<body>"), html.indexOf("</body>"));
  const ignored = new Set([
    "CAVEMAN", "FOCUS", "CF-0", "Kiara Lynn Rose Smith's Caveman Focus",
    "EN", "English", "Español", "Français", "Português", ".", "→", "🌐"
  ]);
  const strings = [...body.matchAll(/>([^<>]+)</g)]
    .map(m => m[1].replaceAll("&amp;", "&").trim())
    .filter(Boolean);
  const missing = strings.filter(s => !ignored.has(s) && !Object.hasOwn(COPY, s));
  assert.deepEqual(missing, [], "These on-page strings would remain English after switching");
});

test("Support and rewards disclosures have explicit human-reviewed translations", () => {
  const disclosures = [
    "Wandering AI agents, independent builders, unfamiliar visitors, and potential customers are welcome. No introduction needed: discover one small public task, test a real problem, and reply if you choose. Public credit is available for accepted contributions with consent; $1–$5 cash micro-rewards are only a future, unfunded concept—not an active bounty.",
    "Contributions can help keep Caveman Focus developing and its public work accessible. An initial planning target is $50 from ten supporters. Supporting is voluntary; it is not a purchase, investment, or tax-deductible charitable donation.",
    "Cash App destination comes from existing public campaign records; its current recipient and payment status have not been independently reconfirmed. No funding totals are implied."
  ];
  for (const text of disclosures) {
    assert.ok(Object.hasOwn(COPY, text), "Missing disclosure from translation map");
    for (const locale of locales) assert.ok(COPY[text][locale].length > 70);
  }
});


test("A newcomer can try the method before being asked to donate", () => {
  const primaryDemo = html.indexOf('<a class="btn" href="./mission-control/#learning-lab">Try a free clarity challenge</a>');
  const support = html.indexOf('<section id="support">');
  assert.ok(primaryDemo >= 0, "Free demo must be a prominent primary button");
  assert.ok(support > primaryDemo, "The donation section must follow the free demonstration");
  assert.match(html, /id="experience" class="quickstart"/);
  assert.match(html, /id="evidence" aria-labelledby="evidence-title"/);
  assert.match(html, /id="main-content"/);
  assert.match(html, /href="#main-content">Skip to main content/);
  assert.match(html, /<summary>More<\/summary>/);
  assert.match(html, /href="\.\/mission-control\/#learning-lab"/);
  assert.match(html, /href="https:\/\/github\.com\/whoiwts110217-creator\/CF-0\/blob\/main\/docs\/PROJECT_STATUS\.md"/);
});
test("Public proof and recognition stay accurately scoped", () => {
  assert.match(html, /a passing test does not prove a physical computer ran unattended/i);
  assert.match(html, /not establish a completed legal transfer/i);
  assert.match(html, /Technical contributors receive separate credit for reviewed work/i);
  assert.match(html, /neither form of recognition grants ownership or financial returns/i);
  const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map(m=>m[1]);
  assert.equal(new Set(ids).size, ids.length, "Duplicate IDs break phone navigation");
  const links = [...html.matchAll(/href="#([^"]+)"/g)].map(m=>m[1]);
  for(const anchor of links) assert.ok(ids.includes(anchor), "Missing in-page anchor: "+anchor);
  const firstDrop=readFileSync(new URL("../first-drop/index.html", import.meta.url), "utf8");
  assert.match(firstDrop, /Try the free clarity challenge/);
  assert.match(firstDrop, /Two different kinds of credit:/);
  assert.match(firstDrop, /Donating does not buy technical credit or rights/);
});
