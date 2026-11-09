import test from "node:test";
import assert from "node:assert/strict";
import { MISSIONS } from "../dist/gameful.mjs";

class FakeElement {
  constructor(id) {
    this.id = id;
    this.hidden = false;
    this.disabled = false;
    this.value = "";
    this.dataset = {};
    this.attributes = {};
    this.textContent = "";
    this.listeners = new Map();
    this.href = "";
    this.focusedCount = 0;
  }
  addEventListener(type, callback) { this.listeners.set(type, callback); }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  removeAttribute(name) { delete this.attributes[name]; }
  click() { this.listeners.get("click")?.(); }
  change() { this.listeners.get("change")?.(); }
  focus() { this.focusedCount += 1; }
}

test("mode switch preserves identical facts across a full guess/remix and reset", async () => {
  const ids = [
    "learning-lab", "gameful-toggle", "gameful-mode", "gameful-large-text", "gameful-content",
    "gameful-title", "gameful-genre", "gameful-claim", "gameful-result",
    "gameful-explanation", "gameful-source", "gameful-next",
    "gameful-field-brief", "gameful-field-action", "gameful-field-evidence", "gameful-field-link"
  ];
  const elements = new Map(ids.map(id => [id, new FakeElement(id)]));
  const trueAnswer = new FakeElement("true-answer");
  const falseAnswer = new FakeElement("false-answer");
  trueAnswer.dataset.gamefulAnswer = "true";
  falseAnswer.dataset.gamefulAnswer = "false";
  elements.get("gameful-content").hidden = true;
  elements.get("gameful-field-brief").hidden = true;
  elements.get("gameful-mode").value = "playful";
  const oldDocument = globalThis.document;
  globalThis.document = {
    getElementById: id => elements.get(id),
    querySelectorAll: selector => selector === "[data-gameful-answer]" ? [trueAnswer, falseAnswer] : []
  };

  try {
    await import("../dist/gameful-ui.mjs");
    const mode = elements.get("gameful-mode");
    const toggle = elements.get("gameful-toggle");
    const content = elements.get("gameful-content");
    const heading = elements.get("gameful-title");
    const claim = elements.get("gameful-claim");
    const result = elements.get("gameful-result");
    const explanation = elements.get("gameful-explanation");
    const source = elements.get("gameful-source");
    const next = elements.get("gameful-next");
    const field = elements.get("gameful-field-brief");
    const fieldAction = elements.get("gameful-field-action");
    const fieldEvidence = elements.get("gameful-field-evidence");
    const fieldLink = elements.get("gameful-field-link");

    mode.value = "plain";
    mode.change();
    assert.equal(elements.get("learning-lab").dataset.learningMode, "plain");
    toggle.click();
    assert.equal(mode.disabled, true);
    assert.equal(content.hidden, false);
    assert.equal(heading.textContent, "Checking execution evidence");
    assert.equal(heading.focusedCount, 1, "Heading receives focus when lesson opens");
    assert.equal(claim.textContent, MISSIONS[0].claim);
    const largeText = elements.get("gameful-large-text");
    const originalQuestion = claim.textContent;
    largeText.checked = true;
    largeText.change();
    assert.equal(elements.get("learning-lab").dataset.largeText, "true");
    assert.equal(claim.textContent, originalQuestion, "Large text does not reset the exercise");
    falseAnswer.click();
    assert.match(result.textContent, /Correct/);
    assert.equal(source.href, MISSIONS[0].sourceUrl);
    const plainExplanation = explanation.textContent;
    assert.match(plainExplanation, /public command round-trip/);
    assert.equal(explanation.focusedCount, 1, "Explanation receives focus after grading");
    assert.equal(next.hidden, false);
    assert.equal(field.hidden, true, "No real-work task before second scenario");
    next.click();
    assert.equal(claim.textContent, MISSIONS[0].transferClaim);
    assert.equal(heading.focusedCount, 2, "Focus moves to the second question");
    trueAnswer.click();
    assert.match(result.textContent, /Correct/);
    assert.equal(source.href, MISSIONS[0].sourceUrl);
    assert.equal(explanation.focusedCount, 2, "Remix feedback is reachable");
    assert.equal(field.hidden, false, "Show a real-world action only after the remix");
    assert.equal(fieldAction.textContent, MISSIONS[0].fieldAction);
    assert.equal(fieldEvidence.textContent, MISSIONS[0].fieldEvidence);
    assert.equal(fieldLink.href, MISSIONS[0].fieldUrl);
    assert.notEqual(fieldAction.textContent, result.textContent, "Real task isn't a pretend quiz award");

    toggle.click();
    assert.equal(content.hidden, true);
    assert.equal(mode.disabled, false);
    mode.value = "playful";
    mode.change();
    assert.equal(elements.get("learning-lab").dataset.learningMode, "playful");
    toggle.click();
    assert.equal(mode.disabled, true);
    assert.equal(heading.textContent, MISSIONS[0].title);
    assert.equal(field.hidden, true, "Restart closes the earlier field brief");
    assert.equal(fieldAction.textContent, "");
    assert.equal(heading.focusedCount, 3, "New mode returns focus to the first question");
    assert.equal(claim.textContent, MISSIONS[0].claim);
    falseAnswer.click();
    assert.match(result.textContent, /MISSION PASSED/);
    assert.equal(explanation.textContent, plainExplanation);
    assert.equal(source.href, MISSIONS[0].sourceUrl);
    toggle.click();
    assert.equal(mode.disabled, false);
    assert.equal(content.hidden, true);
    largeText.checked = false;
    largeText.change();
    assert.equal(elements.get("learning-lab").dataset.largeText, "false");
  } finally {
    globalThis.document = oldDocument;
  }
});
