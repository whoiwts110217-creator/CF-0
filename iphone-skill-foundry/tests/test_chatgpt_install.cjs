// Verify that the GitHub Pages generator prepares a real ChatGPT Plugin Creator handoff.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const { TextEncoder, Blob } = require('node:buffer');
const path = require('node:path');
const html=fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const engine=scripts.find(s=>s.includes('const api=factory()'));
assert.ok(engine, 'pure skill generation module must remain inline and usable offline');
const ctx={ module:{exports:{}}, TextEncoder, Blob };
vm.runInNewContext(engine,ctx);
const api=ctx.module.exports;
const input={
 name:'Caveman Focus Evidence to Action',
 philosophy:'Guess → hypothesis → evidence → proof',
 goal:'Check real-world claims',
 trigger:'When evidence is incomplete',
 principles:'Clarity | Separate facts from guesses | Cite observable facts\nProof | Test each claim | Report the test result',
 examples:'Situation: Chat completion status unknown\nAction: Check the response-finished signal\nOutcome: Not yet tested\nEvidence: unverified',
 source:'user-supplied study example',
 mode:'pack'
};
const bundle=api.build(input), root=api.slugify(input.name);
const key=root+'/INSTALL_IN_CHATGPT.md';
const request=bundle.files[key];
assert.ok(request, 'install request is exported as part of the downloadable skill pack');
assert.match(request, /@plugin-creator/);
assert.match(request,/PERSONAL, skill-only ChatGPT plugin/);
assert.match(request,/=== BEGIN .*\/SKILL\.md ===/);
assert.match(request,/No external apps, payment providers, API keys/);
assert.match(request,/Do not claim installed until ChatGPT confirms/);
assert.ok(Object.keys(bundle.files).some(k=>k.endsWith('/EVALS.json')));
assert.ok(Object.keys(bundle.files).some(k=>k.includes('/skills/')&&k.endsWith('/SKILL.md')));
assert.ok(html.includes('id="copyChatGPTInstall"'));
assert.ok(html.includes('https://chatgpt.com/plugins'));
const bytes=api.zip(bundle.files);
assert.ok(bytes.size>request.length,'ZIP includes more than request content');
console.log('ChatGPT install handoff checks passed. Files:',Object.keys(bundle.files).length);
