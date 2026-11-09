import test from 'node:test';
import assert from 'node:assert/strict';
import {importQueue,conversationURL,newCheckpoint,runSweep,keyboardDriver,MESSAGE} from '../core.mjs';
const a='11111111-1111-4111-8111-111111111111',b='22222222-2222-4222-8222-222222222222';
const queue=()=>importQueue([{id:a,title:'One'}, {conversation_id:b,title:'Two'}, {id:a,title:'Duplicate'}]);
test('validates private queue and rejects arbitrary URL',()=>{assert.equal(queue().length,2);assert.throws(()=>conversationURL('https://evil.test'));});
test('one awaited send at a time; exact text; checkpoint avoids duplicates',async()=>{
  let active=0,maxActive=0;const sent=[], q=queue(),s=newCheckpoint('primary',q);
  const driver={sendAndWait:async args=>{assert.equal(args.text,MESSAGE);sent.push(args.url);active++;maxActive=Math.max(maxActive,active);await Promise.resolve();active--;return {status:'completed'};}};
  const save=async x=>{assert.equal(x.account,'primary');};
  assert.equal((await runSweep({account:'primary',queue:q,checkpoint:s,driver,save,limit:2})).status,'completed');
  assert.equal(sent.length,2);assert.equal(maxActive,1);
  assert.equal((await runSweep({account:'primary',queue:q,checkpoint:s,driver,save,limit:2})).attempted,0);
});
test('uncertain send stops sweep, never retries automatically',async()=>{
  const q=queue(),s=newCheckpoint('secondary',q);let calls=0;
  const driver={sendAndWait:async()=>{calls++;throw Error('timeout');}},save=async()=>{};
  assert.equal((await runSweep({account:'secondary',queue:q,checkpoint:s,driver,save,limit:2})).status,'needs_review');
  assert.equal((await runSweep({account:'secondary',queue:q,checkpoint:s,driver,save,limit:2})).status,'needs_review');
  assert.equal(calls,1);
});
test('pre-send stop prevents any navigation',async()=>{
  const q=queue(),s=newCheckpoint('primary',q),ac=new AbortController();ac.abort();
  const r=await runSweep({account:'primary',queue:q,checkpoint:s,driver:{sendAndWait:async()=>{throw Error('unexpected');}},save:async()=>{},signal:ac.signal});
  assert.equal(r.status,'stopped');
});
test('single Page uses goto, focus and keyboard, no mouse or newPage',async()=>{
  const calls=[];let poll=0;
  const editor={waitFor:async()=>{},focus:async()=>calls.push('focus'),evaluate:async()=>''};
  const page={goto:async u=>{calls.push('goto');page.current=u;},url:()=>page.current,
    locator:()=>({first:()=>editor}),evaluate:async()=>({users:1,assistants:1}),
    keyboard:{insertText:async s=>calls.push('type:'+s),press:async s=>calls.push('key:'+s)},
    waitForFunction:async()=>{poll++;}};
  const out=await keyboardDriver(page).sendAndWait({url:conversationURL(a),text:MESSAGE});
  assert.equal(out.status,'completed');assert.deepEqual(calls,['goto','focus','type:continue','key:Enter']);
  assert.equal(poll,3);
});
