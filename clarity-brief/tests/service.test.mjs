import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page=readFileSync(new URL("../index.html",import.meta.url),"utf8");
const sample=readFileSync(new URL("../SAMPLE_BRIEF.md",import.meta.url),"utf8");
const inquiry=readFileSync(new URL("../../.github/ISSUE_TEMPLATE/clarity-brief-pilot.yml",import.meta.url),"utf8");
const home=readFileSync(new URL("../../index.html",import.meta.url),"utf8");
const first=readFileSync(new URL("../../first-drop/index.html",import.meta.url),"utf8");
const free=readFileSync(new URL("../../clarity-card/index.html",import.meta.url),"utf8");
const sitemap=readFileSync(new URL("../../sitemap.xml",import.meta.url),"utf8");

test("Paid pilot is a complete scoped public-safe inquiry, not a fake checkout",()=>{
  assert.match(page,/\$15/);
  assert.match(page,/one-page/i);
  assert.match(page,/human-reviewed, AI-assisted/i);
  assert.match(page,/Target turnaround:.*3 business days/s);
  assert.match(page,/One correction.*7 days/s);
  assert.match(page,/No paid clients or fulfillment outcomes have yet been verified/i);
  assert.match(page,/Do not send payment before/i);
  assert.match(page,/inquiries/,);
  assert.match(page,/GitHub requires an account/);
  assert.match(page,/Your inquiry will be <strong>public<\/strong>/);
  assert.match(page,/The donation link is|Cash App donation link/i);
  assert.match(page,/not legal, medical, tax, investment/i);
  assert.doesNotMatch(page,/(<form|localStorage|sessionStorage|fetch\(|document\.cookie|stripe\.com|shopify\.com\/checkout)/i);
  assert.doesNotMatch(page,/(guaranteed income|verified client|granted funding|orders received)/i);
});

test("Inquiry template gates privacy and distinguishes interest from an order",()=>{
  assert.match(inquiry,/name: "Clarity Brief — Public Pilot Inquiry"/);
  assert.match(inquiry,/type: checkboxes/);
  assert.match(inquiry,/required: true/g);
  assert.match(inquiry,/GitHub issue is public/i);
  assert.match(inquiry,/not an order or payment/i);
  assert.match(inquiry,/do not include|Do not include/i);
  assert.match(inquiry,/One public-safe question/);
  assert.match(inquiry,/Pilot scope acknowledgment/);
  assert.match(page,/issues\/new\?template=clarity-brief-pilot.yml/);
});

test("Actual free-first pathway, sample and checkout boundaries",()=>{
  assert.match(sample,/Not a completed client assignment/i);
  assert.match(sample,/Uncollected:/);
  assert.match(sample,/STATUS = UNTESTED/);
  assert.match(page,/SAMPLE_BRIEF.md/);
  assert.match(home,/href="\.\/clarity-brief\/"/);
  assert.match(first,/href="\.\.\/clarity-brief\/"/);
  assert.match(free,/href="\.\.\/clarity-brief\/"/);
  assert.match(page,/href="\.\.\/clarity-card\/"/);
  assert.match(sitemap,/\/CF-0\/clarity-brief\//);
  assert.ok(home.indexOf('Try a free clarity challenge')<home.indexOf('Explore the $15 Clarity Brief pilot'),"free first");
});
