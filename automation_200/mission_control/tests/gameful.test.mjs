import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { MISSIONS, gradeMission, gradeTransfer } from "../dist/gameful.mjs";

test("gameful lessons teach source boundaries without invented real-world results", () => {
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

test("remix questions test another situation, with both true and false answers", () => {
  assert.ok(MISSIONS.some(x => x.transferCorrect === true));
  assert.ok(MISSIONS.some(x => x.transferCorrect === false));
  for (const mission of MISSIONS) {
    assert.notEqual(mission.claim, mission.transferClaim);
    assert.match(mission.transferExplanation, /\S/);
    assert.equal(gradeTransfer(mission.id, mission.transferCorrect)?.correct, true);
    assert.equal(gradeTransfer(mission.id, !mission.transferCorrect)?.correct, false);
    assert.equal(gradeTransfer(mission.id, mission.transferCorrect)?.sourceUrl, mission.sourceUrl);
    assert.match(gradeTransfer(mission.id, mission.transferCorrect)?.message, /REMIX CLEARED/);
  }
  assert.equal(gradeTransfer("unregistered", true), null);
  assert.equal(gradeTransfer("continuity", "true"), null);
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
  assert.match(ui, /phase === "reveal"/);
  assert.match(ui, /phase === "transfer-reveal"/);
  assert.match(ui, /textContent/);
});

test("pilot has explicit continuity links in every canonical prompt", () => {
  const root = new URL("../../../", import.meta.url);
  const relative = path => readFileSync(new URL(path, root), "utf8");
  const operator = relative("automation_200/MASTER_OPERATOR_PROMPT.md");
  const continuity = relative("automation_200/MASTER_CONTINUITY_PROMPT.md");
  const worker = relative("automation_200/WORK_COPY_PASTE_AUTOMATION_PROMPT.md");
  const contract = relative("docs/UNIVERSAL_CONTINUITY_CONTRACT.md");
  const pilot = relative("docs/BRAINROT_TO_BRAINPOWER_2026-11-09.md");
  for (const prompt of [operator, continuity, worker]) {
    assert.ok(prompt.includes("UNIVERSAL_CONTINUITY_CONTRACT.md"));
    assert.ok(prompt.includes("BRAINROT_TO_BRAINPOWER_2026-11-09.md"));
  }
  assert.ok(contract.includes("CF-EXP-GAME-LEARN-001"));
  assert.ok(pilot.includes("CF-EXP-GAME-LEARN-001"));
  assert.ok(pilot.includes("FIN-09"));
  assert.ok(pilot.includes("CF-CORE"));
  assert.ok(pilot.includes("RES-04"));
  assert.ok(pilot.includes("learning efficacy unverified"));
});
