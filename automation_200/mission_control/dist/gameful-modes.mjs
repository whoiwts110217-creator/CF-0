// CF-EXP-GAME-LEARN-001 v0.3: display modes over one unchanged evidence set.
// No fetch, random allocation, account permissions, telemetry or persistence.
// A voluntary mode choice is a demo, NOT a randomized study.
const NEUTRAL_TITLES = Object.freeze({
  receipt: "Checking execution evidence",
  funding: "Checking funding claims",
  hypothesis: "Testing a general claim",
  continuity: "Preserving a revision history"
});

export const MODES = Object.freeze(["playful", "plain"]);

export function normalizeMode(mode) {
  return mode === "plain" ? "plain" : "playful";
}

export function lessonView(mission, mode, index, stage) {
  if (!mission || !Number.isInteger(index) || index < 0 || !["guess", "transfer"].includes(stage)) return null;
  const plain = normalizeMode(mode) === "plain";
  const transfer = stage === "transfer";
  return Object.freeze({
    // These fields are always verbatim: no educational change between arms.
    claim: transfer ? mission.transferClaim : mission.claim,
    answer: transfer ? mission.transferCorrect : mission.correct,
    explanation: transfer ? mission.transferExplanation : mission.explanation,
    sourceUrl: mission.sourceUrl,
    takeaway: mission.takeaway,
    heading: plain
      ? (NEUTRAL_TITLES[mission.id] || "Evidence check") + (transfer ? " — second example" : "")
      : mission.title + (transfer ? " — REMIX" : ""),
    eyebrow: plain
      ? "EVIDENCE EXERCISE / " + (transfer ? "SECOND EXAMPLE" : "TOPIC " + (index + 1))
      : mission.genre + (transfer ? " / REMIX CHALLENGE" : " / MISSION " + (index + 1)),
    instruction: transfer
      ? (plain ? "Apply the same rule to this different situation." : "New situation. Apply the rule without looking at the first answer.")
      : (plain ? "Choose true or false, then review the source and explanation." : "Predict TRUE or FALSE, then see the evidence.")
  });
}

export function feedbackView(grade, mode, stage, finished = false) {
  if (!grade || typeof grade.correct !== "boolean" || !["guess", "transfer"].includes(stage)) return null;
  const plain = normalizeMode(mode) === "plain";
  const phrase = plain
    ? (grade.correct ? "Correct. " : "Incorrect. ") + (stage === "transfer" ? "Review the second example." : "Review the explanation.")
    : grade.message;
  return phrase + (finished
    ? (plain ? " Exercise complete. No account or external project state changed." : " QUEST ENDED — no account or real-world results changed.")
    : "");
}
