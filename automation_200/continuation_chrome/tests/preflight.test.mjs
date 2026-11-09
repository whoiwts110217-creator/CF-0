import test from 'node:test';
import assert from 'node:assert/strict';
const id='11111111-1111-4111-8111-111111111111';
const url='https://chatgpt.com/c/'+id;

async function setup({selected=true,tabUrl=url,dom={}}={}){
  let state={schema:'cf0.auto08.chrome.v1',account:selected?'primary':null,
    phase:'idle',reason:null,queue:[],completed:[],profiles:{},attempt:null};
  let handler,inspections=0,debuggerCalls=0,writes=0,tabUpdates=0;
  const chrome={
    storage:{local:{get:async()=>({auto08_state_v1:state}),
      set:async obj=>{writes++;state=obj.auto08_state_v1;}}},
    tabs:{
      query:async()=>[{id:17,url:tabUrl}],
      get:async()=>({id:17,url:tabUrl}),
      update:async()=>{tabUpdates++;},
      onRemoved:{addListener:()=>{}},onCreated:{addListener:()=>{}}
    },
    scripting:{executeScript:async({target,func})=>{
      inspections++;
      assert.deepEqual(target,{tabId:17});
      assert.match(func.toString(),/composerVisible/);
      return [{result:{
        url:tabUrl,dialogVisible:false,dialogText:'',rateLimit:false,signedOut:false,
        composerVisible:true,draft:'',userCount:2,assistantCount:2,
        stopVisible:false,busy:false,...dom
      }}];
    }},
    debugger:{
      attach:async()=>{debuggerCalls++;},
      sendCommand:async()=>{debuggerCalls++;},
      onEvent:{addListener:()=>{}},onDetach:{addListener:()=>{}}
    },
    runtime:{onMessage:{addListener:fn=>handler=fn}}
  };
  globalThis.chrome=chrome;
  await import('../background.js?preflight='+Date.now()+'-'+Math.random());
  const send=msg=>new Promise(resolve=>handler(msg,{},resolve));
  return {send,metrics:()=>({inspections,debuggerCalls,writes,tabUpdates}),state:()=>state};
}

test('read-only preflight succeeds on an existing loaded conversation but does not authenticate the account',async()=>{
  const h=await setup();
  const r=await h.send({type:'PREFLIGHT'});
  assert.equal(r.ok,true);
  assert.equal(r.ready,true);
  assert.equal(r.reason,'READY_ACCOUNT_UNVERIFIED');
  assert.match(r.message,/NOT verified/);
  assert.deepEqual(h.metrics(),{inspections:1,debuggerCalls:0,writes:0,tabUpdates:0});
});
test('read-only preflight does not run without account label',async()=>{
  const h=await setup({selected:false});
  const r=await h.send({type:'PREFLIGHT'});
  assert.equal(r.ready,false);
  assert.equal(r.reason,'SELECT_ACCOUNT_FIRST');
  assert.equal(h.metrics().inspections,0);
});
test('preflight refuses unknown page and preserves private state',async()=>{
  const h=await setup({tabUrl:'https://chatgpt.com/'});
  const r=await h.send({type:'PREFLIGHT'});
  assert.equal(r.reason,'OPEN_A_CONVERSATION_FIRST');
  assert.equal(r.ready,false);
  assert.equal(h.metrics().inspections,0);
  assert.equal(h.metrics().writes,0);
});
test('preflight blocks unsafe page conditions without input, storage or debugger',async()=>{
  for(const [dom,reason] of [
    [{userCount:0,assistantCount:0},'CONVERSATION_HISTORY_NOT_LOADED'],
    [{draft:'unsent private draft'},'OWNER_DRAFT_PRESENT'],
    [{signedOut:true},'SIGN_IN_REQUIRED'],
    [{dialogVisible:true,dialogText:'Approve this purchase'},'NEEDS_OWNER_REVIEW'],
    [{dialogVisible:true,dialogText:"What's new in ChatGPT"},'INFORMATION_DIALOG_PRESENT'],
    [{stopVisible:true},'ALREADY_RESPONDING'],
    [{composerVisible:false},'COMPOSER_NOT_READY'],
    [{url:'https://chatgpt.com/'},'PAGE_CONTENT_MISMATCH']
  ]){
    const h=await setup({dom});
    const r=await h.send({type:'PREFLIGHT'});
    assert.equal(r.ready,false,reason);
    assert.equal(r.reason,reason);
    assert.deepEqual(h.metrics(),{inspections:1,debuggerCalls:0,writes:0,tabUpdates:0});
  }
});
