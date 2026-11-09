import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { MISSIONS, gradeMission } from "../dist/gameful.mjs";

test("gameful lessons teach evidence boundaries without invented results", () => {
  assert.equal(MISSIONS.length, 4);
  assert.deepEqual(MISSIONS.map(x => x.id), ["receipt", "funding", "hypothesis", "continuity"]);
  assert.equal(new Set(MISSIONS.map(x => x.id)).size, MISSIONS.length);
  for (const mission of MISSIONS) {
    assert.ok(mission.sourceUrl.startsWith("https://github.com/whoiwts110217-creator/CF-0/blob/main/"));
    assert.match(mission.explanation, /\S/);
    assert.equal(gradeMission(mission.id, mission.correct)?.correct, true);
    assert.equal(gradeMission(mission.id, !mission.correct)?.correct, false);
    assert.match(gradeMission(mission.id, mission.correct)?.message, /quiz question, not the real-world project/);
  }
  assert.equal(gradeMission("missing", true), null);
  assert.equal(gradeMission("receipt", "false"), null);
});
test("learning lab is opt-in and has no background authority or storage", () => {
  const html = readFileSync(new URL("../dist/index.html", import.meta.url), "utf8");
  const ui = readFileSync(new URL("../dist/gameful-ui.mjs", import.meta.url), "utf8");
  assert.ok(html.includes('id="learning-lab"'));
  assert.ok(html.includes('id="gameful-content" hidden'));
  assert.ok(html.includes('src="./gameful-ui.mjs"'));
  assert.ok(html.includes('id="automation-controls"'));
  assert.ok(html.includes('id="work-orders"'));
  assert.ok(html.includes('id="tool-power"'));
  assert.ok(html.includes('id="show-restricted"'));
  assert.doesNotMatch(ui, /fetch\(|localStorage|sessionStorage|sendMessage|window\.open|postMessage|exec\(/);
  assert.match(ui, /textContent/);
});
