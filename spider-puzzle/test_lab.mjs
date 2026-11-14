import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('./full.html',import.meta.url),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
const extract=(name)=>{
 const row=script.split('\n').find(x=>x.startsWith('function '+name+'('));
 assert.ok(row,`${name} must exist`);return row;
};
const helpers=vm.runInNewContext(`(()=>{const byId=new Map([['pieceA',{}],['pieceB',{}]]);${['clampLab','normalizeLabEntry','parseLabImport'].map(extract).join('\n')}return {normalizeLabEntry,parseLabImport};})()`);
test('Full original source puzzle retained with 1,289 library and 500 starting pieces',()=>{
 assert.match(html,/cf0\.full-millennium-puzzle\.v1/);
 assert.match(html,/Show 500 pieces/);
 assert.match(html,/Show all 1,289/);
 assert.match(html,/fetch\('\.\/atlas\.html'/);
 assert.match(html,/cf0\.full-puzzle\.layout\.v1/);
});
test('New Test Lab has visible controls, no native input, and parses as a script',()=>{
 for(const id of ['labPanel','labTrigger','labExpected','labProcedure','labDevice','labObserved','labOutcome','saveLab','runLab','labProposal','proposeLab','labCount','labProposalCount'])assert.match(html,new RegExp('id="'+id+'"'));
 assert.doesNotThrow(()=>new vm.Script(script));
 assert.doesNotMatch(script,/\b(eval|Function|WebSocket|XMLHttpRequest)\s*\(/);
 assert.match(html,/not independently verified/i);
});
test('Owner-reported pass is not recorded without a procedure, environment, observation',()=>{
 const a=helpers.normalizeLabEntry({trigger:'on pointer move',expected:'within 12 pixels',outcome:'pass'});
 assert.equal(a.outcome,'not-run');
 const b=helpers.normalizeLabEntry({trigger:'on pointer move',expected:'within 12 pixels',procedure:'move cursor',device:'Windows HP',observed:'within 7 pixels',outcome:'pass'});
 assert.equal(b.outcome,'pass');
});
test('Lab restoration can load older layout exports without a lab',()=>{
 const r=helpers.parseLabImport(undefined);
 assert.equal(r.contracts.size,0);assert.equal(r.proposals.length,0);
});
test('Malformed or ungrounded imported lab records fail closed',()=>{
 assert.throws(()=>helpers.parseLabImport({contracts:{notInCatalog:{trigger:'hi'}},proposals:[]}),/Unknown source piece/);
 assert.throws(()=>helpers.parseLabImport({contracts:{pieceA:{}},proposals:[{id:'hyp-abc123',source:'nonexistent',label:'hi'}]}),/Invalid missing-piece proposal/);
 assert.throws(()=>helpers.parseLabImport({contracts:{},proposals:'not an array'}),/Invalid proposals/);
});
test('Text fields are bounded and status values are constrained',()=>{
 const p=helpers.normalizeLabEntry({trigger:'x'.repeat(3000),expected:'yes',procedure:'steps',outcome:'verified'});
 assert.equal(p.trigger.length,600);
 assert.equal(p.outcome,'not-run');
});
test('Missing skill proposals do not imply compiled or executable source',()=>{
 assert.match(html,/hypotheses only, no executable code/i);
 assert.match(html,/No source code was created, and Spider was not assembled/);
});
