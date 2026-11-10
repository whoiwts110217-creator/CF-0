import test from 'node:test';
import assert from 'node:assert/strict';
import {BOOTSTRAP_TEXT,CONTINUE_TEXT,initialState,accountSnapshot,acknowledgedExactCommand} from '../core.mjs';

const a='11111111-1111-4111-8111-111111111111';
const b='22222222-2222-4222-8222-222222222222';
const chatURL=id=>'https://chatgpt.com/c/'+id;

test('the bootstrap message links to the one canonical source and asks for real work',()=>{
  assert.equal(CONTINUE_TEXT,'continue','plain continue remains unchanged');
  assert.match(BOOTSTRAP_TEXT,/https:\/\/github\.com\/whoiwts110217-creator\/CF-0\/blob\/main\/docs\/CHATGPT_MEMORY_BOOTSTRAP\.md/);
  assert.match(BOOTSTRAP_TEXT,/three linked master prompts in order/);
  assert.match(BOOTSTRAP_TEXT,/substantial authorized work session/);
  assert.match(BOOTSTRAP_TEXT,/Do not publish private material/);
  assert.equal(BOOTSTRAP_TEXT.includes('\n'),false,'exact visible-text ack stays on one line');
  assert.equal(acknowledgedExactCommand({userCount:3,lastUserExactCommand:true},2),true);
  assert.equal(acknowledgedExactCommand({userCount:3,lastUserExactCommand:false},2),false);
  assert.equal(acknowledgedExactCommand({userCount:4,lastUserExactCommand:true},2),false);
});

test('bootstrap-sent and bootstrap-completed receipts survive account switches separately from continue',()=>{
  let s={...initialState(),account:'primary',queue:[{id:a}],completed:[a],submitted:[b],
    bootstrapSent:[a],bootstrapCompleted:[]};
  s={...s,...accountSnapshot(s,'secondary')};
  assert.deepEqual(s.bootstrapSent,[]);
  assert.deepEqual(s.completed,[]);
  s={...s,queue:[{id:b}],bootstrapSent:[b],bootstrapCompleted:[b]};
  s={...s,...accountSnapshot(s,'primary')};
  assert.deepEqual(s.bootstrapSent,[a]);
  assert.deepEqual(s.bootstrapCompleted,[]);
  assert.deepEqual(s.completed,[a]);
  assert.deepEqual(s.submitted,[b]);
  const legacy=accountSnapshot({account:'primary',queue:[{id:a}],completed:[a]},'secondary');
  assert.deepEqual(legacy.profiles.primary.bootstrapSent,[]);
  assert.deepEqual(legacy.profiles.primary.bootstrapCompleted,[]);
});

test('two prior continue chats each receive one exact bootstrap instruction; no replies are claimed in fast mode', {timeout:20000},async()=>{
  const calls=[];const events={};let state={...initialState(),account:'primary',completed:[a],submitted:[b]};
  const tab={id:37,url:chatURL(a)};
  const pages={
    [a]:{userCount:1,assistantCount:1,acked:false},
    [b]:{userCount:1,assistantCount:1,acked:false}
  };
  let current=a;
  globalThis.chrome={
    storage:{local:{
      get:async()=>({auto08_state_v1:state}),
      set:async x=>{state=x.auto08_state_v1;}
    }},
    tabs:{
      query:async()=>[tab],get:async()=>tab,update:async()=>{},
      onRemoved:{addListener:fn=>events.closed=fn},
      onCreated:{addListener:fn=>events.created=fn}
    },
    debugger:{
      attach:async t=>{assert.equal(t.tabId,37);calls.push('attach');},
      detach:async()=>{calls.push('detach');},
      sendCommand:async(t,method,params)=>{
        assert.equal(t.tabId,37);calls.push(method);
        if(method==='Page.navigate'){
          current=params.url.split('/').at(-1);tab.url=params.url;
        }
        if(method==='Input.insertText'){
          assert.equal(params.text,BOOTSTRAP_TEXT);
          calls.push('bootstrap_payload');
        }
        if(method==='Input.dispatchKeyEvent'&&params.type==='rawKeyDown'&&params.key==='Enter'){
          pages[current].userCount++;
          pages[current].acked=true;
        }
      },
      onEvent:{addListener:fn=>events.dialog=fn},
      onDetach:{addListener:fn=>events.detach=fn}
    },
    scripting:{executeScript:async({target,func,args})=>{
      assert.equal(target.tabId,37);
      if(func.toString().includes('editor.focus()'))return [{result:'FOCUSED'}];
      const p=pages[current];
      if(args)assert.equal(args[0],BOOTSTRAP_TEXT);
      return [{result:{
        url:tab.url,dialogVisible:false,dialogText:'',rateLimit:false,signedOut:false,
        composerVisible:true,draft:'',userCount:p.userCount,assistantCount:p.assistantCount,
        lastUserExactContinue:false,lastUserExactCommand:p.acked,
        lastAssistantSignature:'old-reply',stopVisible:false,busy:false
      }}];
    }},
    runtime:{onMessage:{addListener:fn=>events.message=fn}}
  };
  await import('../background.js?bootstrapMode='+Math.random());
  const message=m=>new Promise(resolve=>events.message(m,{},resolve));
  assert.equal((await message({type:'IMPORT_QUEUE',raw:[{id:a,title:'A'},{id:b,title:'B'}]})).ok,true);
  assert.equal((await message({type:'START',bootstrap:true,advanceAfterAck:true,maxChats:2})).ok,true);
  const deadline=Date.now()+15000;
  while(Date.now()<deadline){
    await new Promise(r=>setTimeout(r,100));
    const status=await message({type:'STATUS'});
    if(status.state.phase==='idle'&&status.state.bootstrapSent?.length===2)break;
  }
  let last=(await message({type:'STATUS'})).state;
  assert.equal(last.phase,'idle',last.lastResult);
  assert.deepEqual(last.bootstrapSent,[a,b]);
  assert.deepEqual(last.bootstrapCompleted,[],'fast send did not verify assistant replies');
  assert.deepEqual(last.completed,[a],'plain completed list not overwritten');
  assert.deepEqual(last.submitted,[b],'plain continue submitted list not overwritten');
  assert.equal(calls.filter(x=>x==='bootstrap_payload').length,2);
  assert.equal(calls.filter(x=>x==='Page.navigate').length,1);
  assert.equal(calls.filter(x=>x==='attach').length,1);
  assert.equal(calls.filter(x=>x==='detach').length,1);

  // A repeated fast sweep must not submit to the same two chat IDs again.
  assert.equal((await message({type:'START',bootstrap:true,advanceAfterAck:true,maxChats:2})).ok,true);
  const secondDeadline=Date.now()+5000;
  while(Date.now()<secondDeadline){
    await new Promise(r=>setTimeout(r,50));
    last=(await message({type:'STATUS'})).state;
    if(last.phase==='idle')break;
  }
  assert.equal(calls.filter(x=>x==='bootstrap_payload').length,2);
});
