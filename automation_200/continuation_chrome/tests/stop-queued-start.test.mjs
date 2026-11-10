import test from 'node:test';
import assert from 'node:assert/strict';

// Regression: STOP can arrive while an earlier START awaits the initial
// chrome.storage.local.get. STOP must win before tab inspection or attachment.
test('STOP invalidates a queued start while local state read is pending', {timeout:8000}, async()=>{
  const id='11111111-1111-4111-8111-111111111111';
  const chatUrl='https://chatgpt.com/c/'+id;
  let state={schema:'cf0.auto08.chrome.v1',account:'primary',
    selectedTabId:null,phase:'idle',reason:null,queue:[{id}],
    completed:[],submitted:[],profiles:{},attempt:null,currentChat:null,
    updatedAt:null,lastResult:null,maxChats:1};
  let enterRead,releaseRead;
  const readEntered=new Promise(resolve=>enterRead=resolve);
  const gate=new Promise(resolve=>releaseRead=resolve);
  const handlers={};
  let tabQueries=0,attachments=0,keyboardInputs=0;
  globalThis.chrome={
    storage:{local:{
      get:async()=>{
        enterRead();
        await gate;
        return {auto08_state_v1:structuredClone(state)};
      },
      set:async value=>{state=structuredClone(value.auto08_state_v1);}
    }},
    tabs:{
      query:async()=>{tabQueries++;return [{id:41,url:chatUrl}];},
      get:async()=>({id:41,url:chatUrl}),update:async()=>{},
      onRemoved:{addListener:fn=>handlers.removed=fn},
      onCreated:{addListener:fn=>handlers.created=fn}
    },
    debugger:{
      attach:async()=>{attachments++;},
      detach:async()=>{},
      sendCommand:async(_target,method)=>{if(method.startsWith('Input.'))keyboardInputs++;},
      onEvent:{addListener:fn=>handlers.event=fn},
      onDetach:{addListener:fn=>handlers.detached=fn}
    },
    scripting:{executeScript:async()=>{throw Error('Unexpected page inspection');}},
    runtime:{onMessage:{addListener:fn=>handlers.message=fn}}
  };
  await import('../background.js?queued-stop='+Date.now());
  const send=msg=>new Promise(resolve=>handlers.message(msg,{},resolve));
  const starting=send({type:'CONTINUE_CURRENT'});
  await readEntered;
  const stopping=send({type:'STOP'});
  releaseRead();
  const [started,stopped]=await Promise.all([starting,stopping]);
  assert.equal(started.ok,false);
  assert.match(started.error,/STOP_REQUESTED/);
  assert.equal(stopped.ok,true);
  assert.equal(tabQueries,0,'cancel before inspecting a signed-in tab');
  assert.equal(attachments,0,'cancel before debugger attachment');
  assert.equal(keyboardInputs,0,'never send a message');
  assert.equal(state.phase,'paused');
  assert.equal(state.reason,'USER_STOP');
  assert.equal(state.attempt,null);
});
