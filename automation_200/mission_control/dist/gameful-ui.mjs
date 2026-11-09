// CF-EXP-GAME-LEARN-001 v0.3: optional, no-storage presentation choice.
// Both modes use the same graded facts and source links; no experiment participants are tracked.
import { MISSIONS, gradeMission, gradeTransfer } from "./gameful.mjs";
import { normalizeMode, lessonView, feedbackView } from "./gameful-modes.mjs";

const get = id => document.getElementById(id);
const lab = get("learning-lab");
const toggle = get("gameful-toggle");
const modeSelect = get("gameful-mode");
const largeTextSelect = get("gameful-large-text");
const content = get("gameful-content");
const heading = get("gameful-title");
const genre = get("gameful-genre");
const claim = get("gameful-claim");
const result = get("gameful-result");
const explanation = get("gameful-explanation");
const source = get("gameful-source");
const next = get("gameful-next");
const fieldBrief = get("gameful-field-brief");
const fieldAction = get("gameful-field-action");
const fieldEvidence = get("gameful-field-evidence");
const fieldLink = get("gameful-field-link");
const answers = Array.from(document.querySelectorAll("[data-gameful-answer]"));
const moveFocus = element => { if (typeof element?.focus === "function") element.focus(); };
let index = 0;
let phase = "guess";
let mode = "playful";

function setSource(mission) {
  source.href = mission.sourceUrl;
  source.textContent = mission.sourceText + " ↗";
  source.hidden = false;
}

function showFieldBrief(mission) {
  // Public, static action plan only: no grant status, HP receipt, or bank data is read.
  fieldAction.textContent = mission.fieldAction;
  fieldEvidence.textContent = mission.fieldEvidence;
  fieldLink.href = mission.fieldUrl;
  fieldBrief.hidden = false;
}

function display(stage) {
  const mission = MISSIONS[index];
  const view = lessonView(mission, mode, index, stage);
  phase = stage;
  genre.textContent = view.eyebrow + " / " + (index + 1) + " OF " + MISSIONS.length;
  heading.textContent = view.heading;
  claim.textContent = view.claim;
  result.textContent = view.instruction;
  result.dataset.tone = "neutral";
  explanation.textContent = "";
  source.hidden = true;
  source.removeAttribute("href");
  next.hidden = true;
  fieldBrief.hidden = true;
  fieldAction.textContent = "";
  fieldEvidence.textContent = "";
  fieldLink.removeAttribute("href");
  answers.forEach(button => { button.disabled = false; });
  moveFocus(heading);
}

function displayGuess() { display("guess"); }
function displayTransfer() { display("transfer"); }

function updateMode() {
  mode = normalizeMode(modeSelect.value);
  lab.dataset.learningMode = mode;
  if (content.hidden) {
    toggle.textContent = mode === "plain" ? "Start evidence exercise" : "Start brainpower quest";
  }
}

// The style choice is locked during one exercise to avoid a moving comparison condition.
// Close the exercise to choose another mode; neither mode stores responses.
modeSelect.addEventListener("change", updateMode);
updateMode();

// Presentation-only accessibility preference: no storage, identity or grading changes.
function updateTextSize() {
  lab.dataset.largeText = String(largeTextSelect.checked);
}
largeTextSelect.addEventListener("change", updateTextSize);
updateTextSize();

toggle.addEventListener("click", () => {
  content.hidden = !content.hidden;
  toggle.setAttribute("aria-expanded", String(!content.hidden));
  modeSelect.disabled = !content.hidden;
  toggle.textContent = content.hidden
    ? (mode === "plain" ? "Start evidence exercise" : "Start brainpower quest")
    : (mode === "plain" ? "Close evidence exercise" : "Close brainpower quest");
  if (!content.hidden) {
    index = 0;
    displayGuess();
  }
});

for (const button of answers) {
  button.addEventListener("click", () => {
    const guess = button.dataset.gamefulAnswer === "true";
    const mission = MISSIONS[index];
    if (phase === "guess") {
      const graded = gradeMission(mission.id, guess);
      if (!graded) return;
      phase = "reveal";
      result.textContent = feedbackView(graded, mode, "guess");
      result.dataset.tone = graded.correct ? "pass" : "retry";
      explanation.textContent = graded.explanation + " Takeaway: " + graded.takeaway;
      setSource(mission);
      next.textContent = mode === "plain" ? "Apply to a second example" : "Try the remix (new example)";
      next.hidden = false;
    } else if (phase === "transfer") {
      const graded = gradeTransfer(mission.id, guess);
      if (!graded) return;
      phase = "transfer-reveal";
      const last = index + 1 >= MISSIONS.length;
      result.textContent = feedbackView(graded, mode, "transfer", last);
      result.dataset.tone = graded.correct ? "pass" : "retry";
      explanation.textContent = graded.explanation;
      setSource(mission);
      next.textContent = mode === "plain" ? "Next topic" : "Next encounter";
      next.hidden = last;
      showFieldBrief(mission);
    } else {
      return;
    }
    answers.forEach(choice => { choice.disabled = true; });
    moveFocus(explanation);
  });
}

next.addEventListener("click", () => {
  if (phase === "reveal") displayTransfer();
  else if (phase === "transfer-reveal" && index + 1 < MISSIONS.length) {
    index++;
    displayGuess();
  }
});
