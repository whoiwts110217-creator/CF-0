import test from 'node:test';
import assert from 'node:assert/strict';

// Owner acceptance requirement: one selected existing tab, 17 unique chats,
// no retry of an in-progress thread, and no busy chat blocking the remaining 14.
const ids=Array.from({length:17},(_,i)=>
  String(i+1).padStart(8,'0')+'-1111-4111-8111-111111111111');
const url=id=>'https://chatgpt.com/c/'+id;

test('fast 17-chat sweep skips three busy pre-send threads, reaches the other 14, and revisits only eligible chats later',
  {timeout:20000},async()=>{
  const events={},calls=[];
  let state,current=ids[0];
  const tab={id:37,url:url(current)};
  const busy=new Set(ids.slice(0,3));
  const pages=Object.fromEntries(ids.map(id=>[id,{users:1,assistants:1,acked:false}]));
  globalThis.chrome={
    storage:{local:{
      get:async()=>state?{auto08_state_v1:state}:{},
      set:async data=>{state=data.auto08_state_v1;}
    }},
    tabs:{
      query:async()=>[tab],get:async()=>tab,
      onRemoved:{addListener:fn=>events.closed=fn},
      onCreated:{addListener:fn=>events.created=fn}
    },
    debugger:{
      attach:async target=>{assert.equal(target.tabId,37);calls.push('attach');},
      detach:async target=>{assert.equal(target.tabId,37);calls.push('detach');},
      sendCommand:async(target,method,params)=>{
        assert.equal(target.tabId,37);
        if(method==='Page.navigate'){
          assert.equal(new URL(params.url).origin,'https://chatgpt.com');
          current=params.url.split('/').at(-1);
          tab.url=params.url;
        }
        if(method==='Input.insertText'){
          assert.equal(params.text,'continue');
          assert.equal(busy.has(current),false,'busy thread must never be typed into');
          calls.push('insert:'+current);
        }
        if(method==='Input.dispatchKeyEvent'&&params.type==='rawKeyDown'&&params.key==='Enter'){
          pages[current].users++;
          pages[current].acked=true;
        }
      },
      onEvent:{addListener:fn=>events.dialog=fn},
      onDetach:{addListener:fn=>events.detached=fn}
    },
    scripting:{executeScript:async({target,func})=>{
      assert.equal(target.tabId,37);
      if(func.toString().includes('editor.focus()'))return [{result:'FOCUSED'}];
      const p=pages[current];
      return [{result:{
        url:tab.url,dialogVisible:false,dialogText:'',rateLimit:false,signedOut:false,
        composerVisible:!busy.has(current),draft:'',userCount:p.users,assistantCount:p.assistants,
        lastUserExactContinue:p.acked,lastAssistantSignature:'old',
        stopVisible:busy.has(current),busy:busy.has(current)
      }}];
    }},
    runtime:{onMessage:{addListener:fn=>events.message=fn}}
  };
  await import('../background.js?skipBusy='+Math.random());
  const message=m=>new Promise(resolve=>events.message(m,{},resolve));
  async function waitForSubmitted(n){
    const deadline=Date.now()+14000;
    while(Date.now()<deadline){
      const s=(await message({type:'STATUS'})).state;
      if(s.phase==='idle' && s.submitted?.length===n)return s;
      if(s.phase==='needs_review')throw Error('Unexpected global stop: '+s.reason);
      await new Promise(r=>setTimeout(r,40));
    }
    throw Error('Timed out waiting for '+n+' submissions');
  }

  assert.equal((await message({type:'SET_ACCOUNT',account:'primary'})).ok,true);
  assert.equal((await message({type:'IMPORT_QUEUE',raw:ids.map(id=>({id}))})).ok,true);
  assert.equal((await message({type:'START',maxChats:17,advanceAfterAck:true})).ok,true);
  let s=await waitForSubmitted(14);
  assert.equal(s.attempt,null,'pre-send skip may not leave an uncertain attempt');
  assert.equal(s.currentChat,null);
  assert.equal(s.completed.length,0,'fast submitted is not answer completed');
  assert.match(s.lastResult,/skipped 3 busy chat\(s\)/);
  assert.deepEqual(s.submitted,ids.slice(3));
  assert.equal(calls.filter(x=>x.startsWith('insert:')).length,14);
  assert.equal(calls.filter(x=>x==='attach').length,1);
  assert.equal(calls.filter(x=>x==='detach').length,1);

  // Once those three genuinely become idle, a later run sends ONLY to them;
  // the previously submitted 14 remain checkpointed and are not duplicated.
  busy.clear();
  assert.equal((await message({type:'START',maxChats:17,advanceAfterAck:true})).ok,true);
  s=await waitForSubmitted(17);
  assert.equal(new Set(s.submitted).size,17);
  assert.equal(calls.filter(x=>x.startsWith('insert:')).length,17);
  assert.equal(calls.filter(x=>x==='attach').length,2);
  assert.equal(calls.filter(x=>x==='detach').length,2);
  assert.equal(s.completed.length,0);
});
