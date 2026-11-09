// CF-EXP-GAME-LEARN-001: optional, bounded evidence-learning overlay.
// Sources and continuity: docs/BRAINROT_TO_BRAINPOWER_2026-11-09.md
export const MISSIONS = Object.freeze([
  Object.freeze({
    id: "receipt",
    genre: "MYSTERY / BOSS FIGHT",
    title: "THE RECEIPT IMPOSTOR",
    claim: "A matching public HP ping and receipt prove the Windows task ran unattended.",
    correct: false,
    explanation: "A matched request and receipt supports a public command round-trip. It does not, by itself, identify the physical HP or prove an unattended Windows scheduler run.",
    sourceText: "Read the project evidence",
    sourceUrl: "https://github.com/whoiwts110217-creator/CF-0/blob/main/docs/PROJECT_STATUS.md",
    takeaway: "Matched evidence is not the same as independently verified execution."
  }),
  Object.freeze({
    id: "funding",
    genre: "STRATEGY / ECONOMY",
    title: "THE INVISIBLE PAYDAY",
    claim: "A submitted grant request counts as money earned before an award and payment arrive.",
    correct: false,
    explanation: "An application is a real completed action, but it is not an award or received money. The records must keep requested funds, approvals and settlements separate.",
    sourceText: "Read the business boundary",
    sourceUrl: "https://github.com/whoiwts110217-creator/CF-0/blob/main/docs/BUSINESS.md",
    takeaway: "Submitted is not funded; a proposal is not revenue."
  }),
  Object.freeze({
    id: "hypothesis",
    genre: "SCIENCE / PUZZLE",
    title: "THE FINITE FINAL BOSS",
    claim: "Checking many numerical examples alone proves a universal mathematical claim.",
    correct: false,
    explanation: "Finite numerical tests can disprove a universal claim with a valid counterexample, but passing finite cases alone does not establish a universal theorem.",
    sourceText: "Read the research status",
    sourceUrl: "https://github.com/whoiwts110217-creator/CF-0/blob/main/docs/RESEARCH.md",
    takeaway: "Tests inform proof; they do not replace a general argument."
  }),
  Object.freeze({
    id: "continuity",
    genre: "RPG / SAVE POINT",
    title: "THE SAVE THAT REMEMBERS",
    claim: "A failed test should remain in the continuity record even if the next version passes.",
    correct: true,
    explanation: "Preserving the original failure, fix, source version and new test result makes later claims auditable. Quietly erasing a failure destroys information.",
    sourceText: "Read the universal continuity contract",
    sourceUrl: "https://github.com/whoiwts110217-creator/CF-0/blob/main/docs/UNIVERSAL_CONTINUITY_CONTRACT.md",
    takeaway: "Keep originals, corrections and evidence linked."
  })
]);

export function gradeMission(id, guess) {
  const mission = MISSIONS.find(item => item.id === id);
  if (!mission || typeof guess !== "boolean") return null;
  return Object.freeze({
    correct: guess === mission.correct,
    message: guess === mission.correct
      ? "MISSION PASSED — you beat this quiz question, not the real-world project."
      : "CHECKPOINT RETRY — the explanation is the real upgrade.",
    explanation: mission.explanation,
    takeaway: mission.takeaway,
    sourceText: mission.sourceText,
    sourceUrl: mission.sourceUrl
  });
}
