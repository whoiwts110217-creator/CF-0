import test from 'node:test';
import assert from 'node:assert/strict';

const id='11111111-1111-4111-8111-111111111111';
const chatUrl='https://chatgpt.com/c/'+id;

function harness({stickyDialog=false,addSecondAfterSend=false,attachFailure=false}={}){
  let state,hasSent=false,escapes=0,sends=0,attached=0,detached=0;
  const handlers={};
  const tab={id:23,url:chatUrl};
  const chrome={
    storage:{local:{
      get:async()=>state?{auto08_state_v1:state}:{},
      set:async x=>{state=x.auto08_state_v1;}
    }},
    tabs:{
      query:async()=>addSecondAfterSend&&hasSent?[tab,{id:24,url:'https://chatgpt.com/'}]:[tab],
      get:async()=>tab,update:async()=>{},
      onRemoved:{addListener:fn=>handlers.removed=fn},
      onCreated:{addListener:fn=>handlers.created=fn}
    },
    debugger:{
      attach:async t=>{assert.equal(t.tabId,23);attached++;if(attachFailure)throw Error('DEBUGGER_PERMISSION_DENIED');},
      detach:async()=>{detached++;},
      sendCommand:async(t,method,params)=>{
        assert.equal(t.tabId,23);
        if(method==='Input.insertText'){assert.equal(params.text,'continue');sends++;}
        if(method==='Input.dispatchKeyEvent'&&params.type==='rawKeyDown'){
          if(params.key==='Escape')escapes++;
          if(params.key==='Enter')hasSent=true;
        }
      },
      onEvent:{addListener:fn=>handlers.dialog=fn},
      onDetach:{addListener:fn=>handlers.detach=fn}
    },
    scripting:{
      executeScript:async({target,func})=>{
        assert.equal(target.tabId,23);
        if(func.toString().includes('editor.focus()'))return [{result:'FOCUSED'}];
        const dialogVisible=stickyDialog;
        return [{result:{url:chatUrl,dialogVisible,dialogText:dialogVisible?"What's new in ChatGPT":'',
          signedOut:false,rateLimit:false,composerVisible:true,draft:'',
          userCount:hasSent?2:1,assistantCount:hasSent?2:1,
          lastAssistantSignature:hasSent?'50:33001':'20:10001',
          busy:false,stopVisible:false}}];
      }
    },
    runtime:{onMessage:{addListener:fn=>handlers.message=fn}}
  };
  return {chrome,handlers,status:()=>state,metrics:()=>({sends,escapes,attached,detached,hasSent})};
}
async function send(h,msg){return new Promise(resolve=>h.handlers.message(msg,{},resolve));}
async function until(h,check,timeout=8000){
  const until=Date.now()+timeout;
  while(Date.now()<until){
    const s=(await send(h,{type:'STATUS'})).state;
    if(check(s))return s;
    await new Promise(resolve=>setTimeout(resolve,80));
  }
  throw Error('timed out waiting for status');
}
test('persistent information overlay cannot be mistaken for cleared; never sends', {timeout:12000},async()=>{
  const h=harness({stickyDialog:true});globalThis.chrome=h.chrome;
  await import('../background.js?sticky=' + Date.now());
  assert.equal((await send(h,{type:'SET_ACCOUNT',account:'primary'})).ok,true);
  assert.equal((await send(h,{type:'CONTINUE_CURRENT'})).ok,true);
  const s=await until(h,x=>x.phase==='needs_review',10000);
  assert.equal(s.reason,'REPEATED_POPUP');
  assert.equal(h.metrics().sends,0);
  assert.equal(h.metrics().escapes,2);
  assert.equal(h.metrics().detached,1);
});
test('another ChatGPT tab appearing during generation halts without retry', {timeout:12000},async()=>{
  const h=harness({addSecondAfterSend:true});globalThis.chrome=h.chrome;
  await import('../background.js?second=' + Date.now());
  assert.equal((await send(h,{type:'SET_ACCOUNT',account:'primary'})).ok,true);
  assert.equal((await send(h,{type:'CONTINUE_CURRENT'})).ok,true);
  const s=await until(h,x=>x.phase==='needs_review',9000);
  assert.equal(s.reason,'CHATGPT_TAB_COUNT_CHANGED');
  assert.equal(h.metrics().sends,1);
  assert.equal(s.attempt.status,'in_flight'); // Unknown result must not be retried blindly.
  // A newly selected queue/account cannot discard a maybe-sent message.
  const reset=await send(h,{type:'IMPORT_QUEUE',raw:[{id,title:'Same chat'}]});
  assert.equal(reset.ok,false);
  assert.match(reset.error,/UNRESOLVED_ATTEMPT/);
  const relabel=await send(h,{type:'SET_ACCOUNT',account:'secondary'});
  assert.equal(relabel.ok,false);
  assert.match(relabel.error,/UNRESOLVED_ATTEMPT/);
  const clear=await send(h,{type:'ACK_PRE_SEND'});
  assert.equal(clear.ok,false);
  assert.equal(h.metrics().detached,1);
});

test('debugger attach refusal cleans up live marker and allows safe pre-send recovery',{timeout:8000},async()=>{
  const h=harness({attachFailure:true});globalThis.chrome=h.chrome;
  await import('../background.js?attachfailure=' + Date.now());
  assert.equal((await send(h,{type:'SET_ACCOUNT',account:'primary'})).ok,true);
  assert.equal((await send(h,{type:'CONTINUE_CURRENT'})).ok,true);
  const s=await until(h,x=>x.phase==='needs_review',6000);
  assert.equal(s.reason,'DEBUGGER_PERMISSION_DENIED');
  assert.equal(s.attempt,null);
  assert.equal(h.metrics().sends,0);
  // No debugger session is attached; no stale live flag may prevent acknowledgement.
  const ack=await send(h,{type:'ACK_PRE_SEND'});
  assert.equal(ack.ok,true);
  assert.equal((await send(h,{type:'STATUS'})).state.phase,'paused');
  assert.equal(h.metrics().attached,1);
  assert.equal(h.metrics().detached,0);
});
