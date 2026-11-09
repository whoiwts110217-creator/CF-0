import test from 'node:test';
import assert from 'node:assert/strict';

const id='11111111-1111-4111-8111-111111111111';
const url='https://chatgpt.com/c/'+id;

test('background attaches only existing Chrome ChatGPT tab and completes one keyboard continuation', {timeout:20000}, async()=>{
  const calls=[];let userCount=2, assistantCount=2;let afterSend=false;let state;
  const events={};
  const tab={id:37,url};
  globalThis.chrome={
    storage:{local:{get:async()=>state?{auto08_state_v1:state}:{},set:async x=>{state=x.auto08_state_v1;}}},
    tabs:{query:async()=>[tab],get:async()=>tab,update:async()=>{} ,onRemoved:{addListener:fn=>events.closed=fn},onCreated:{addListener:fn=>events.created=fn}},
    debugger:{
      attach:async t=>{assert.equal(t.tabId,37);calls.push('attach');},
      detach:async()=>{calls.push('detach');},
      sendCommand:async(t,method,params)=>{
        assert.equal(t.tabId,37);calls.push(method);
        if(method==='Input.insertText')assert.equal(params.text,'continue');
        if(method==='Input.dispatchKeyEvent'&&params.type==='rawKeyDown'&&params.key==='Enter'){
          userCount++;assistantCount++;afterSend=true;
        }
      },
      onEvent:{addListener:fn=>events.dialog=fn},onDetach:{addListener:fn=>events.detach=fn}
    },
    scripting:{executeScript:async({target,func})=>{
      assert.equal(target.tabId,37);
      if(func.toString().includes('editor.focus()'))return [{result:'FOCUSED'}];
      return [{result:{url,dialogVisible:false,dialogText:'',rateLimit:false,signedOut:false,
        composerVisible:true,draft:'',userCount,assistantCount,
        lastAssistantSignature:afterSend?'32:16001':'20:20002',stopVisible:false,busy:false}}];
    }},
    runtime:{onMessage:{addListener:fn=>events.message=fn}}
  };
  await import('../background.js?test='+Math.random());
  const msg=m=>new Promise(resolve=>events.message(m,{},resolve));
  const status=await msg({type:'STATUS'});
  assert.equal(status.tabs.reason,'ONE_TAB_READY');
  assert.equal((await msg({type:'SET_ACCOUNT',account:'primary'})).ok,true);
  assert.equal((await msg({type:'CONTINUE_CURRENT'})).ok,true);
  const deadline=Date.now()+15000;
  while(Date.now()<deadline){
    await new Promise(r=>setTimeout(r,250));
    const s=await msg({type:'STATUS'});
    if(s.state.phase==='idle'&&s.state.completed.length)break;
  }
  const s=await msg({type:'STATUS'});
  assert.equal(s.state.phase,'idle',s.state.lastResult);
  assert.deepEqual(s.state.completed,[id]);
  assert.equal(calls.filter(x=>x==='Input.insertText').length,1);
  assert.ok(calls.includes('attach'));
  assert.ok(calls.includes('detach'));
  assert.equal(calls.filter(x=>x==='Page.navigate').length,0,'current tab should not navigate');
});
