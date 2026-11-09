import test from 'node:test';
import assert from 'node:assert/strict';

const a='11111111-1111-4111-8111-111111111111';
const b='22222222-2222-4222-8222-222222222222';

test('reimport and account switches cannot silently erase completed checkpoints',async()=>{
  // Simulate a legacy v1 installation. No browser tab, Chrome debugger, or
  // ChatGPT account is contacted; these are state-transition checks.
  let stored={schema:'cf0.auto08.chrome.v1',account:'primary',
    queue:[{id:a,title:'Original'}],completed:[a],
    phase:'idle',reason:null,attempt:null,currentChat:null};
  let handler;
  globalThis.chrome={
    storage:{local:{get:async()=>({auto08_state_v1:stored}),
      set:async fields=>{stored=fields.auto08_state_v1;}}},
    tabs:{query:async()=>[],onRemoved:{addListener:()=>{}},
      onCreated:{addListener:()=>{}}},
    debugger:{onEvent:{addListener:()=>{}},onDetach:{addListener:()=>{}}},
    runtime:{onMessage:{addListener:fn=>handler=fn}}
  };
  await import('../background.js?account-checkpoints='+Date.now());
  const send=msg=>new Promise(resolve=>handler(msg,{},resolve));

  assert.equal((await send({type:'IMPORT_QUEUE',raw:[{id:a,title:'Reimported'}]})).ok,true);
  assert.deepEqual(stored.completed,[a],'reimport must not reenable old sends');

  assert.equal((await send({type:'SET_ACCOUNT',account:'secondary'})).ok,true);
  assert.deepEqual(stored.completed,[]);
  assert.deepEqual(stored.queue,[]);
  assert.equal((await send({type:'IMPORT_QUEUE',raw:[{id:b,title:'Other'}]})).ok,true);
  assert.deepEqual(stored.queue.map(x=>x.id),[b]);

  assert.equal((await send({type:'SET_ACCOUNT',account:'primary'})).ok,true);
  assert.deepEqual(stored.queue.map(x=>x.id),[a]);
  assert.deepEqual(stored.completed,[a]);
  assert.equal((await send({type:'SET_ACCOUNT',account:'secondary'})).ok,true);
  assert.deepEqual(stored.queue.map(x=>x.id),[b]);
  assert.deepEqual(stored.completed,[]);
  assert.equal((await send({type:'IMPORT_QUEUE',raw:[{id:b,title:'Same again'}]})).ok,true);
  assert.deepEqual(stored.queue.map(x=>x.id),[b]);
  // A malformed imported list is rejected without disturbing checkpoints.
  const bad=await send({type:'IMPORT_QUEUE',raw:{}});
  assert.equal(bad.ok,false);
  assert.deepEqual(stored.queue.map(x=>x.id),[b]);
});
