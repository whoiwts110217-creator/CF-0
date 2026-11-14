import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';
const here=path.dirname(fileURLToPath(import.meta.url));
const project=path.join(here,'..');
const viewer=fs.readFileSync(path.join(here,'full.html'),'utf8');
const atlas=fs.readFileSync(path.join(project,'docs/spider-puzzle/index.html'),'utf8');
const m=atlas.match(/<script\s+id="embedded-data"\s+type="application\/json">([\s\S]*?)<\/script>/i);
assert.ok(m,'atlas source-backed embedded data missing');
const data=JSON.parse(m[1]);
test('Full viewer has a 500-piece launch, 1,289-piece option and manual save',()=>{
  for(const expected of ['id="batch500"','id="batchAll"','id="exportLayout"','id="importLayout"','id="auditAll"','id="tiles"','id="inspector"']) assert.ok(viewer.includes(expected),expected);
  assert.match(viewer,/fetch\('\.\/atlas\.html'/);
  assert.doesNotMatch(viewer,/<script[^>]*\ssrc=/);
});
test('Viewer script parses and does not try to launch native Spider',()=>{
  const script=viewer.match(/<script>([\s\S]*?)<\/script>/)?.[1];
  assert.ok(script);
  assert.doesNotThrow(()=>new vm.Script(script));
  assert.doesNotMatch(script,/\b(eval|Function|WebSocket|XMLHttpRequest)\s*\(/);
});
test('Exactly 1,289 distinct source symbols and 632 mapped edges',()=>{
  assert.equal(data.pieces.length,1289);assert.equal(data.dep_edges.length,632);
  const ids=new Set(data.pieces.map(p=>p.id));assert.equal(ids.size,1289);
  for(const e of data.dep_edges){assert.ok(ids.has(e.from));assert.ok(ids.has(e.to));}
});
test('All 1,289 original source-line SHA-256 hashes match',()=>{
  const cache=new Map();
  for(const p of data.pieces){
    if(!cache.has(p.path)){assert.equal(typeof data.sources[p.path],'string');cache.set(p.path,data.sources[p.path].split(/(?<=\n)/));}
    const src=cache.get(p.path).slice(p.line-1,p.end).join('');
    const digest=createHash('sha256').update(src,'utf8').digest('hex');
    assert.equal(digest,p.sha256,p.id);
  }
});
