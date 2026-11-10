import test from 'node:test';
import assert from 'node:assert/strict';
import {initialState} from '../core.mjs';

// Regression: a chat ending in an unanswered user message can have a visible
// composer while the Stop/generating button is absent. It must not receive an
// additional 'continue', even if the owner asks for a one-chat run.
test('trailing unanswered user turn blocks AUTO-08 before keyboard send', {timeout:6000}, async()=>{
  const id='11111111-1111-4111-8111-111111111111';
  const url='https://chatgpt.com/c/'+id;
  let stored={...initialState(),account:'primary'};
  let keyboard=0;
  let attached=0;
  let detached=0;
  const callbacks={};
  const tab={id:77,url};
  globalThis.chrome={
    storage:{local:{
      get:async()=>({auto08_state_v1:structuredClone(stored)}),
      set:async value=>{stored=structuredClone(value.auto08_state_v1);}
    }},
    tabs:{
      query:async()=>[tab],get:async()=>tab,update:async()=>{},
      onRemoved:{addListener:fn=>callbacks.removed=fn},
      onCreated:{addListener:fn=>callbacks.created=fn}
    },
    debugger:{
      attach:async()=>{attached++;},
      detach:async()=>{detached++;},
      sendCommand:async(_target,method)=>{
        if(method.startsWith('Input.'))keyboard++;
      },
      onEvent:{addListener:fn=>callbacks.event=fn},
      onDetach:{addListener:fn=>callbacks.detached=fn}
    },
    scripting:{executeScript:async()=>[{result:{
      url,dialogVisible:false,signedOut:false,rateLimit:false,
      composerVisible:true,draft:'',userCount:2,assistantCount:1,
      lastTurnIsUser:true,lastUserExactContinue:true,
      lastAssistantSignature:'8:123',stopVisible:false,busy:false
    }}]},
    runtime:{onMessage:{addListener:fn=>callbacks.message=fn}}
  };
  await import('../background.js?unanswered-turn='+Date.now());
  const send=message=>new Promise(resolve=>callbacks.message(message,{},resolve));
  assert.equal((await send({type:'CONTINUE_CURRENT'})).ok,true);
  const deadline=Date.now()+3000;
  while(Date.now()<deadline){
    if(stored.phase==='needs_review')break;
    await new Promise(resolve=>setTimeout(resolve,25));
  }
  assert.equal(stored.phase,'needs_review');
  assert.equal(stored.reason,'UNANSWERED_USER_TURN');
  assert.equal(stored.attempt,null,'pre-send marker should not block later owner review');
  assert.equal(keyboard,0,'no duplicate text or Enter');
  assert.equal(attached,1);
  assert.equal(detached,1);
  assert.equal(stored.completed.length,0,'do not invent a completed reply');
});
