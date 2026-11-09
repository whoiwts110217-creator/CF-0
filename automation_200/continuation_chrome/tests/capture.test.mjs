import test from 'node:test';
import assert from 'node:assert/strict';
const id1='11111111-1111-4111-8111-111111111111';
const id2='22222222-2222-4222-8222-222222222222';

test('local visible sidebar capture merges only valid IDs and preserves prior queue and completion',async()=>{
  let state;
  let reads=0;
  let attached=0;
  const handlers={};
  const tab={id:31,url:'https://chatgpt.com/'};
  globalThis.chrome={
    storage:{local:{
      get:async()=>state?{auto08_state_v1:state}:{},
      set:async x=>{state=x.auto08_state_v1;}
    }},
    tabs:{
      query:async()=>[tab],get:async()=>tab,
      onRemoved:{addListener:()=>{}},onCreated:{addListener:()=>{}}
    },
    debugger:{
      attach:async()=>{attached++;},onEvent:{addListener:()=>{}},
      onDetach:{addListener:()=>{}}
    },
    scripting:{executeScript:async({target,func})=>{
      assert.equal(target.tabId,31);
      assert.match(func.toString(),/nav a\[href\]/);
      reads++;
      return [{result:{url:'https://chatgpt.com/',links:[
        '/c/'+id1, '/c/'+id2, '/c/'+id1,
        'https://evil.com/c/'+id2, '/c/not-a-chat-id'
      ]}}];
    }},
    runtime:{onMessage:{addListener:fn=>handlers.message=fn}}
  };
  await import('../background.js?capture='+Date.now());
  const call=msg=>new Promise(resolve=>handlers.message(msg,{},resolve));
  assert.equal((await call({type:'CAPTURE_VISIBLE'})).ok,false,'account selection is required');
  assert.equal((await call({type:'SET_ACCOUNT',account:'primary'})).ok,true);
  const first=await call({type:'CAPTURE_VISIBLE'});
  assert.equal(first.ok,true,first.error);
  assert.match(first.message,/2 new/);
  let current=(await call({type:'STATUS'})).state;
  assert.deepEqual(current.queue.map(x=>x.id),[id1,id2]);
  const second=await call({type:'CAPTURE_VISIBLE'});
  assert.equal(second.ok,true);
  assert.match(second.message,/0 new/);
  current=(await call({type:'STATUS'})).state;
  assert.equal(current.queue.length,2);
  assert.equal(current.completed.length,0);
  assert.equal(attached,0,'capture never attaches the debugger or sends a message');
  assert.equal(reads,2);
  assert.equal((await call({type:'SET_ACCOUNT',account:'secondary'})).ok,true);
  current=(await call({type:'STATUS'})).state;
  assert.equal(current.queue.length,0,'switching account label must drop prior queue');
});
