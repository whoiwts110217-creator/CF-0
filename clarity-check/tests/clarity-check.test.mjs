import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
const page=readFileSync(new URL("../index.html",import.meta.url),"utf8");
const form=readFileSync(new URL("../../.github/ISSUE_TEMPLATE/clarity-check.yml",import.meta.url),"utf8");
const sample=readFileSync(new URL("../../docs/CLARITY_CHECK_EXAMPLE_2026-11-09.md",import.meta.url),"utf8");
test("offer is public, limited, not prepaid, and links free alternative",()=>{
  for(const p of [/\$5/,/one public URL/i,/no payment yet/i,/written acceptance/i,/manual pilot/i,/refund/i,/not a complete code audit/i,/\/CF-0\/issues\/new\?template=clarity-check\.yml/,/href="\.\.\/clarity-card\/"/])assert.match(page,p);
  assert.doesNotMatch(page,/(?:password field|<form[^>]+action=|localStorage|document\.cookie|fetch\()/i);
});
test("paid service checkout is separate from voluntary support",()=>{
  assert.match(page,/voluntary Cash App support link/i);
  assert.match(page,/not<\/strong> a service checkout or order confirmation/i);
  assert.match(page,/private payment method/i);
  assert.match(page,/cancellation\/refund terms/i);
  assert.match(page,/Never put payment details in the public issue/i);
  assert.doesNotMatch(page,/pay the stated \$5 through the project's existing Cash App route/i);
});
test("issue template has no forced payment and collects public URL only",()=>{
  for(const term of [/name:/,/public-url/,/required: true/,/do not pay/i,/secrets/i,/consent/i])assert.match(form,term);
  assert.doesNotMatch(form,/password|payment receipt upload|private repository access/i);
});
test("demonstration does not invent results or client transactions",()=>{
  assert.match(sample,/Demonstration only/);
  assert.match(sample,/No visitors, conversions, or outcomes were measured/);
  assert.match(sample,/not a paid client/i);
});
