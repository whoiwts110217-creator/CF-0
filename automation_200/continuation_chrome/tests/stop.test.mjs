import test from 'node:test';
import assert from 'node:assert/strict';

const id='11111111-1111-4111-8111-111111111111';
const url='https://chatgpt.com/c/'+id;
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const until=async(fn,timeout=7000)=>{
  const deadline=Date.now()+timeout;
  while(Date.now()<deadline){if(fn())return;await sleep(20);}
  throw Error('Timed out waiting for STOP test condition');
};

function harness({holdTabs=false,holdFocus=false,stopAfterEnter=false,holdCompletion=false}={}){
  let state={schema:'cf0.auto08.chrome.v1',account:'primary',selectedTabId:null,
    phase:'idle',reason:null,queue:[{id}],completed:[],profiles:{},attempt:null,
    currentChat:null,updatedAt:null,lastResult:null,maxChats:1};
  const calls=[];
  let hasSent=false,tabRelease,focusRelease,completionRelease;
  let tabEntered,focusEntered,completionEntered;
  const onTabs=new Promise(resolve=>tabEntered=resolve);
  const onFocus=new Promise(resolve=>focusEntered=resolve);
  const onCompletion=new Promise(resolve=>completionEntered=resolve);
  const events={};
  const tab={id:23,url};
  let message;
  const chrome={
    storage:{local:{
      get:async()=>({auto08_state_v1:state}),
      set:async obj=>{
        const next=obj.auto08_state_v1;
        if(holdCompletion && next.completed?.includes(id) && !completionRelease){
          completionEntered();
          await new Promise(resolve=>completionRelease=resolve);
        }
        state=structuredClone(next);
      }
    }},
    tabs:{
      query:async()=>{
        if(holdTabs&&!tabRelease){
          tabEntered();
          await new Promise(resolve=>tabRelease=resolve);
        }
        return [tab];
      },
      get:async()=>tab,update:async()=>{},
      onRemoved:{addListener:fn=>events.removed=fn},
      onCreated:{addListener:fn=>events.created=fn}
    },
    debugger:{
      attach:async()=>{calls.push('attach');},
      detach:async()=>{calls.push('detach');},
      sendCommand:async(_target,method,params)=>{
        calls.push(method);
        if(method==='Input.insertText'){
          assert.equal(params.text,'continue');
        }
        if(method==='Input.dispatchKeyEvent'&&params.type==='rawKeyDown'&&params.key==='Enter'){
          hasSent=true;
          if(stopAfterEnter) queueMicrotask(()=>{void message({type:'STOP'});});
        }
      },
      onEvent:{addListener:fn=>events.debuggerEvent=fn},
      onDetach:{addListener:fn=>events.detached=fn}
    },
    scripting:{executeScript:async({func})=>{
      if(func.toString().includes('editor.focus()')){
        if(holdFocus){
          focusEntered();
          await new Promise(resolve=>focusRelease=resolve);
        }
        return [{result:'FOCUSED'}];
      }
      return [{result:{
        url,dialogVisible:false,dialogText:'',rateLimit:false,signedOut:false,
        composerVisible:true,draft:'',userCount:hasSent?2:1,
        assistantCount:hasSent?2:1,lastUserExactContinue:hasSent,
        lastAssistantSignature:hasSent?'32:16001':'20:20002',
        stopVisible:false,busy:false
      }}];
    }},
    runtime:{onMessage:{addListener:fn=>events.message=fn}}
  };
  const call=msg=>new Promise(resolve=>events.message(msg,{},resolve));
  message=call;
  return {chrome,call,calls,status:()=>state,onTabs,onFocus,onCompletion,
    releaseTabs:()=>tabRelease?.(),releaseFocus:()=>focusRelease?.(),
    releaseCompletion:()=>completionRelease?.()};
}

test('STOP during launch preflight cancels before attach and preserves pause', {timeout:12000},async()=>{
  const h=harness({holdTabs:true});globalThis.chrome=h.chrome;
  await import('../background.js?stop-preflight='+Date.now());
  const start=h.call({type:'START',maxChats:1});
  await h.onTabs;
  assert.equal((await h.call({type:'STOP'})).ok,true);
  h.releaseTabs();
  const started=await start;
  assert.equal(started.ok,false);
  assert.match(started.error,/STOP_REQUESTED/);
  assert.equal(h.calls.includes('attach'),false);
  assert.equal(h.calls.includes('Input.insertText'),false);
  assert.equal(h.status().phase,'paused');
});

test('STOP at editor focus prevents all keyboard actions', {timeout:12000},async()=>{
  const h=harness({holdFocus:true});globalThis.chrome=h.chrome;
  await import('../background.js?stop-focus='+Date.now());
  assert.equal((await h.call({type:'CONTINUE_CURRENT'})).ok,true);
  await h.onFocus;
  assert.equal((await h.call({type:'STOP'})).ok,true);
  h.releaseFocus();
  await until(()=>h.status().phase==='paused' && h.status().attempt===null);
  assert.equal(h.calls.includes('Input.insertText'),false);
  await until(()=>h.calls.includes('detach'));
});

test('STOP after an Enter boundary retains an uncertain attempt for owner review',{timeout:12000},async()=>{
  const h=harness({stopAfterEnter:true});globalThis.chrome=h.chrome;
  await import('../background.js?stop-after-enter='+Date.now());
  assert.equal((await h.call({type:'CONTINUE_CURRENT'})).ok,true);
  await until(()=>h.status().phase==='needs_review'&&h.status().reason==='USER_STOP');
  assert.equal(h.status().attempt?.status,'maybe_sent');
  assert.deepEqual(h.status().completed,[]);
  assert.equal(h.calls.filter(x=>x==='Input.insertText').length,1);
  await until(()=>h.calls.includes('detach'));
});

test('STOP wins after a delayed completion write; no false idle resume',{timeout:20000},async()=>{
  const h=harness({holdCompletion:true});globalThis.chrome=h.chrome;
  await import('../background.js?stop-finish='+Date.now());
  assert.equal((await h.call({type:'CONTINUE_CURRENT'})).ok,true);
  await h.onCompletion; // after the stable-answer gate, before completed is persisted
  const stopped=h.call({type:'STOP'});
  h.releaseCompletion();
  assert.equal((await stopped).ok,true);
  await until(()=>h.status().phase==='paused'&&h.calls.includes('detach'));
  assert.deepEqual(h.status().completed,[id],'verified answer checkpoint survives STOP');
  assert.equal(h.calls.filter(x=>x==='Input.insertText').length,1);
  assert.equal(h.status().reason,'USER_STOP');
});
