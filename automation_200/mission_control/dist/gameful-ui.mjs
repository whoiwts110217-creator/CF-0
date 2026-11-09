// Optional no-storage learning mini-game; never writes to the dashboard source model.
import { MISSIONS, gradeMission } from "./gameful.mjs";

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
let answered = false;

function show() {
  const mission = MISSIONS[index];
  answered = false;
  genre.textContent = mission.genre + " / " + (index + 1) + " OF " + MISSIONS.length;
  heading.textContent = mission.title;
  claim.textContent = mission.claim;
  result.textContent = "Choose TRUE or FALSE before revealing the explanation.";
  result.dataset.tone = "neutral";
  explanation.textContent = "";
  source.removeAttribute("href");
  source.hidden = true;
  next.hidden = true;
  answers.forEach(button => { button.disabled = false; });
}

toggle.addEventListener("click", () => {
  content.hidden = !content.hidden;
  toggle.setAttribute("aria-expanded", String(!content.hidden));
  toggle.textContent = content.hidden ? "Start brainpower quest" : "Close brainpower quest";
  if (!content.hidden) show();
});

for (const button of answers) {
  button.addEventListener("click", () => {
    if (answered) return;
    const mission = MISSIONS[index];
    const grade = gradeMission(mission.id, button.dataset.gamefulAnswer === "true");
    if (!grade) return;
    answered = true;
    result.textContent = grade.message;
    result.dataset.tone = grade.correct ? "pass" : "retry";
    explanation.textContent = grade.explanation + " Takeaway: " + grade.takeaway;
    source.href = grade.sourceUrl;
    source.textContent = grade.sourceText + " ↗";
    source.hidden = false;
    answers.forEach(choice => { choice.disabled = true; });
    if (index + 1 < MISSIONS.length) {
      next.hidden = false;
      next.textContent = "Next encounter";
    } else {
      next.hidden = true;
      result.textContent += " ALL ENCOUNTERS FINISHED. No account state or rewards were changed.";
    }
  });
}

next.addEventListener("click", () => {
  if (answered && index + 1 < MISSIONS.length) { index++; show(); }
});
