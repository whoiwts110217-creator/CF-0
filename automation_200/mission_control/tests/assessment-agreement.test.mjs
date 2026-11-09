// Synthetic arithmetic checks ONLY. None of the numbers are study outcomes.
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { summarizeIndependentFacetRatings as summary } from "../../../research/gameful_learning/rater_agreement.mjs";

const syntheticRows=[
  {id:"FICTION-01",a:{conclusion:1,evidence:1},b:{conclusion:1,evidence:1}},
  {id:"FICTION-02",a:{conclusion:0,evidence:0},b:{conclusion:1,evidence:0}},
  {id:"FICTION-03",a:{conclusion:1,evidence:0},b:{conclusion:1,evidence:0}},
  {id:"FICTION-04",a:{conclusion:0,evidence:1},b:{conclusion:0,evidence:0}},
  {id:"FICTION-05",a:{conclusion:1,evidence:1},b:{conclusion:0,evidence:1}},
  {id:"FICTION-06",a:{conclusion:0,evidence:0},b:{conclusion:0,evidence:0}}
];
test("explicit human-decided facets produce transparent descriptive agreement",()=>{
  const r=summary(syntheticRows);
  assert.equal(r.schema,"cf0.rater_agreement_descriptive.v1");
  assert.equal(r.paired_responses,6);
  assert.deepEqual(r.disagreement_ids,["FICTION-02","FICTION-04","FICTION-05"]);
  assert.equal(r.facet_pair_exact.observed_agreement,0.5);
  assert.equal(r.total_score_exact.observed_agreement,0.5);
  assert.equal(r.conclusion.matches,4);
  assert.equal(r.evidence.matches,5);
  assert.equal(r.conclusion.observed_agreement,4/6);
  assert.equal(r.evidence.observed_agreement,5/6);
  assert.ok(Math.abs(r.conclusion.cohen_kappa - 1/3) < 1e-10);
  assert.ok(Math.abs(r.evidence.cohen_kappa - 2/3) < 1e-10);
  assert.match(r.warning,/Descriptive agreement only/);
});
test("zero rows and constant marginal categories are honest about undefined kappa",()=>{
  const empty=summary([]);
  assert.equal(empty.paired_responses,0);
  assert.equal(empty.conclusion.cohen_kappa,null);
  assert.equal(empty.conclusion.observed_agreement,null);
  const allZeros=summary([
    {id:"FICTION-07",a:{conclusion:0,evidence:0},b:{conclusion:0,evidence:0}},
    {id:"FICTION-08",a:{conclusion:0,evidence:0},b:{conclusion:0,evidence:0}}
  ]);
  assert.equal(allZeros.conclusion.observed_agreement,1);
  assert.equal(allZeros.conclusion.cohen_kappa,null);
  assert.equal(allZeros.evidence.cohen_kappa,null);
});
test("incomplete, ambiguous, duplicated or corrupted judgments are not treated as zeros",()=>{
  for(const input of [null,{}, "rows"])assert.throws(()=>summary(input),TypeError);
  const A={id:"x",a:{conclusion:0,evidence:1},b:{conclusion:0,evidence:1}};
  for(const rows of [
    [A,A],
    [{...A,id:""}],
    [{...A,a:{conclusion:0,evidence:null}}],
    [{...A,b:{conclusion:true,evidence:1}}],
    [{...A,b:{conclusion:2,evidence:1}}],
    [{...A,b:null}]
  ]) assert.throws(()=>summary(rows),TypeError);
});
test("agreement utility does not contain any response parser, persistent data or remote calls",()=>{
  const raw=readFileSync(new URL("../../../research/gameful_learning/rater_agreement.mjs",import.meta.url),"utf8");
  for(const banned of ["fetch(", "localStorage.", "sessionStorage.", "sendBeacon(", "new WebSocket", "readFile", "writeFile", "exec(", "openai", "scoreNaturalLanguage"]){
    assert.equal(raw.includes(banned),false,"Forbidden inference or I/O: "+banned);
  }
});
