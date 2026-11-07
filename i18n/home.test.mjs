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
    "EN", "English", "Español", "Français", "Português", ".", "→"
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
