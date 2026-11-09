// CF-EXP-GAME-LEARN-001 - pure, dependency-free reviewer agreement arithmetic.
// IMPORTANT: this file does NOT score written responses, collect participant data,
// estimate learning effects, or certify rater reliability. Two raters must independently
// supply explicit 0/1 facet decisions; missing/incomplete cases require separate review.
const isBit = v => v === 0 || v === 1;

function metrics(pairs) {
  const n = pairs.length;
  if (n === 0) return Object.freeze({ n, matches: 0, observed_agreement: null, chance_agreement: null, cohen_kappa: null });
  let matches = 0, aTrue = 0, bTrue = 0;
  for (const [a, b] of pairs) {
    matches += Number(a === b);
    aTrue += a;
    bTrue += b;
  }
  const pObserved = matches / n;
  const pA = aTrue / n, pB = bTrue / n;
  const pExpected = pA * pB + (1 - pA) * (1 - pB);
  // Undefined when both marginals are constant and all observations agree.
  const kappa = 1 - pExpected <= 1e-12 ? null : (pObserved - pExpected) / (1 - pExpected);
  return Object.freeze({
    n, matches,
    observed_agreement: pObserved,
    chance_agreement: pExpected,
    cohen_kappa: kappa
  });
}

export function summarizeIndependentFacetRatings(rows) {
  if (!Array.isArray(rows)) throw new TypeError("Expected array of paired independent ratings.");
  const seen = new Set();
  const conclusionPairs = [], evidencePairs = [], completePairs = [];
  const disagreement_ids = [];
  for (const row of rows) {
    if (typeof row?.id !== "string" || !row.id.trim() || seen.has(row.id)) {
      throw new TypeError("Every paired rating needs a unique nonblank item/response id.");
    }
    seen.add(row.id);
    const a = row.a, b = row.b;
    if (![a?.conclusion, a?.evidence, b?.conclusion, b?.evidence].every(isBit)) {
      throw new TypeError("Both human raters must supply separate 0/1 conclusion and evidence judgments; do not silently impute missing.");
    }
    conclusionPairs.push([a.conclusion, b.conclusion]);
    evidencePairs.push([a.evidence, b.evidence]);
    completePairs.push([a.conclusion + a.evidence, b.conclusion + b.evidence]);
    if (a.conclusion !== b.conclusion || a.evidence !== b.evidence) disagreement_ids.push(row.id);
  }
  const n = rows.length;
  const identical = completePairs.reduce((sum, [a,b]) => sum + Number(a===b), 0);
  const facetIdentical = n - disagreement_ids.length;
  return Object.freeze({
    schema: "cf0.rater_agreement_descriptive.v1",
    paired_responses: n,
    total_score_exact: Object.freeze({
      n, matches: identical, observed_agreement: n ? identical/n : null
    }),
    facet_pair_exact: Object.freeze({
      n, matches: facetIdentical, observed_agreement: n ? facetIdentical/n : null
    }),
    conclusion: metrics(conclusionPairs),
    evidence: metrics(evidencePairs),
    disagreement_ids: Object.freeze(disagreement_ids),
    warning: "Descriptive agreement only. Null kappa means undefined, not zero. No human assessment was performed by this function; items, raters, study design, form equivalence and validity need independent evaluation."
  });
}
