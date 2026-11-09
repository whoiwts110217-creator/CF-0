// CF-EXP-GAME-LEARN-001 v0.2: opt-in, no-storage micro-learning.
// Purely local DOM interaction: never modifies Mission Control's real source model.
import { MISSIONS, gradeMission, gradeTransfer } from "./gameful.mjs";

const get = id => document.getElementById(id);
const toggle = get("gameful-toggle");
const content = get("gameful-content");
const heading = get("gameful-title");
const genre = get("gameful-genre");
const claim = get("gameful-claim");
const result = get("gameful-result");
const explanation = get("gameful-explanation");
const source = get("gameful-source");
const next = get("gameful-next");
const answers = Array.from(document.querySelectorAll("[data-gameful-answer]"));
let index = 0;
let phase = "guess";

function setSource(mission) {
  source.href = mission.sourceUrl;
  source.textContent = mission.sourceText + " ↗";
  source.hidden = false;
}

function displayGuess() {
  const mission = MISSIONS[index];
  phase = "guess";
  genre.textContent = mission.genre + " / MISSION " + (index + 1) + " OF " + MISSIONS.length;
  heading.textContent = mission.title;
  claim.textContent = mission.claim;
  result.textContent = "Predict TRUE or FALSE, then see the evidence.";
  result.dataset.tone = "neutral";
  explanation.textContent = "";
  source.hidden = true;
  source.removeAttribute("href");
  next.hidden = true;
  answers.forEach(button => { button.disabled = false; });
}

function displayTransfer() {
  const mission = MISSIONS[index];
  phase = "transfer";
  genre.textContent = mission.genre + " / REMIX CHALLENGE";
  heading.textContent = mission.title + " — REMIX";
  claim.textContent = mission.transferClaim;
  result.textContent = "New situation. Apply the rule without looking at the first answer.";
  result.dataset.tone = "neutral";
  explanation.textContent = "";
  source.hidden = true;
  source.removeAttribute("href");
  next.hidden = true;
  answers.forEach(button => { button.disabled = false; });
}

toggle.addEventListener("click", () => {
  content.hidden = !content.hidden;
  toggle.setAttribute("aria-expanded", String(!content.hidden));
  toggle.textContent = content.hidden ? "Start brainpower quest" : "Close brainpower quest";
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
      result.textContent = graded.message;
      result.dataset.tone = graded.correct ? "pass" : "retry";
      explanation.textContent = graded.explanation + " Takeaway: " + graded.takeaway;
      setSource(mission);
      next.textContent = "Try the remix (new example)";
      next.hidden = false;
    } else if (phase === "transfer") {
      const graded = gradeTransfer(mission.id, guess);
      if (!graded) return;
      phase = "transfer-reveal";
      result.textContent = graded.message;
      result.dataset.tone = graded.correct ? "pass" : "retry";
      explanation.textContent = graded.explanation;
      setSource(mission);
      next.textContent = "Next encounter";
      next.hidden = index + 1 >= MISSIONS.length;
      if (next.hidden) result.textContent += " QUEST ENDED — no account or real-world results changed.";
    } else {
      return;
    }
    answers.forEach(choice => { choice.disabled = true; });
  });
}

next.addEventListener("click", () => {
  if (phase === "reveal") displayTransfer();
  else if (phase === "transfer-reveal" && index + 1 < MISSIONS.length) {
    index++;
    displayGuess();
  }
});
