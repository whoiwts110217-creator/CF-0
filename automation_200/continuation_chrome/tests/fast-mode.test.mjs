import test from 'node:test';
import assert from 'node:assert/strict';
import {accountSnapshot, initialState} from '../core.mjs';

const first='11111111-1111-4111-8111-111111111111';
const second='22222222-2222-4222-8222-222222222222';
const chatURL=id=>'https://chatgpt.com/c/'+id;

test('fast submission receipts are separated by account and migrated safely',()=>{
  let s={...initialState(),account:'primary',queue:[{id:first}],completed:[],submitted:[first]};
  s={...s,...accountSnapshot(s,'secondary')};
  assert.deepEqual(s.submitted,[]);
  s={...s,queue:[{id:second}],submitted:[second]};
  s={...s,...accountSnapshot(s,'primary')};
  assert.deepEqual(s.submitted,[first]);
  s={...s,...accountSnapshot(s,'secondary')};
  assert.deepEqual(s.submitted,[second]);
  const legacy=accountSnapshot({account:'primary',queue:[{id:first}],completed:[first]},'secondary');
  assert.deepEqual(legacy.profiles.primary.submitted,[]);
});

test('fast queue uses same tab, requires exact acknowledged sends, and does NOT claim assistant completion', {timeout:20000},async()=>{
  const calls=[];const events={};let state;
  const tab={id:37,url:chatURL(first)};
  const pages={
    [first]:{userCount:1,assistantCount:1,acked:false},
    [second]:{userCount:1,assistantCount:1,acked:false}
  };
  let current=first;
  globalThis.chrome={
    storage:{local:{
      get:async()=>state?{auto08_state_v1:state}:{},
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
          assert.equal(new URL(params.url).host,'chatgpt.com');
          current=params.url.split('/').at(-1);tab.url=params.url;
        }
        if(method==='Input.insertText')assert.equal(params.text,'continue');
        if(method==='Input.dispatchKeyEvent'&&params.type==='rawKeyDown'&&params.key==='Enter'){
          pages[current].userCount++;
          pages[current].acked=true;
        }
      },
      onEvent:{addListener:fn=>events.dialog=fn},
      onDetach:{addListener:fn=>events.detach=fn}
    },
    scripting:{executeScript:async({target,func})=>{
      assert.equal(target.tabId,37);
      if(func.toString().includes('editor.focus()'))return [{result:'FOCUSED'}];
      const p=pages[current];
      return [{result:{
        url:tab.url,dialogVisible:false,dialogText:'',rateLimit:false,signedOut:false,
        composerVisible:true,draft:'',userCount:p.userCount,assistantCount:p.assistantCount,
        lastUserExactContinue:p.acked,
        lastAssistantSignature:'old-reply',stopVisible:false,busy:false
      }}];
    }},
    runtime:{onMessage:{addListener:fn=>events.message=fn}}
  };
  await import('../background.js?fastMode='+Math.random());
  const message=m=>new Promise(resolve=>events.message(m,{},resolve));
  assert.equal((await message({type:'SET_ACCOUNT',account:'primary'})).ok,true);
  assert.equal((await message({type:'IMPORT_QUEUE',raw:[{id:first,title:'First'},{id:second,title:'Second'}]})).ok,true);
  assert.equal((await message({type:'START',maxChats:2,advanceAfterAck:true})).ok,true);
  const deadline=Date.now()+15000;
  while(Date.now()<deadline){
    await new Promise(r=>setTimeout(r,100));
    const status=await message({type:'STATUS'});
    if(status.state.phase==='idle'&&status.state.submitted?.length===2)break;
  }
  const final=(await message({type:'STATUS'})).state;
  assert.equal(final.phase,'idle',final.lastResult);
  assert.deepEqual(final.submitted,[first,second]);
  assert.deepEqual(final.completed,[],'no assistant replies were generated or waited for');
  assert.match(final.lastResult,/Replies NOT verified/);
  assert.equal(calls.filter(x=>x==='Input.insertText').length,2);
  assert.equal(calls.filter(x=>x==='Page.navigate').length,1);
  assert.equal(calls.filter(x=>x==='attach').length,1);
  assert.equal(calls.filter(x=>x==='detach').length,1);
  assert.equal(tab.url,chatURL(second));

  // Re-running the same queue cannot accidentally submit duplicates.
  assert.equal((await message({type:'START',maxChats:2,advanceAfterAck:true})).ok,true);
  const lastDeadline=Date.now()+5000;
  while(Date.now()<lastDeadline){
    await new Promise(r=>setTimeout(r,50));
    if((await message({type:'STATUS'})).state.phase==='idle')break;
  }
  assert.equal(calls.filter(x=>x==='Input.insertText').length,2);
});
