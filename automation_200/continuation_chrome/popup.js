const $=id=>document.getElementById(id);
const call=async(data)=>chrome.runtime.sendMessage(data);
let lastState=null;
async function refresh(){
  const r=await call({type:'STATUS'});
  if(!r?.ok){$('status').textContent='Status unavailable';return;}
  const {state,tabs}=r;
  lastState=state;
  $('status').textContent=`ChatGPT tabs: ${tabs.count} | ${tabs.reason}\nRunner: ${state.phase}${state.reason?' · '+state.reason:''}\nCompleted: ${state.completed?.length||0}`;
  $('account').value=state.account||'';
  $('detail').textContent=state.lastResult||'Use Check tab, then Continue current chat once for the first live test.';
  const blocked=state.phase==='running'||state.phase==='needs_review'||!!state.attempt||!state.account;
  $('start').disabled=!state.queue?.length || tabs.count!==1 || blocked;
  $('current').disabled=tabs.count!==1||blocked;
  $('pause').disabled=!['running','paused','needs_review'].includes(state.phase);
  $('review').disabled=state.phase!=='needs_review';
  $('review').textContent=state.attempt?'Review uncertain send':'Clear pre-send blocker';
}
const withFeedback=fn=>async()=>{
  try{
    const r=await fn();
    await refresh();
    $('detail').textContent=(r?.ok===false?'Error: '+r.error:r?.message)||'Request received';
  }catch(e){await refresh();$('detail').textContent=e.message;}
};
$('check').addEventListener('click',withFeedback(()=>call({type:'STATUS'})));
$('account').addEventListener('change',withFeedback(()=>call({type:'SET_ACCOUNT',account:$('account').value})));
$('queue').addEventListener('change',withFeedback(async()=>{
  const f=$('queue').files?.[0];if(!f)return {message:'No file selected'};
  if(f.size>4*1024*1024)throw new Error('Private index too large (4 MB maximum)');
  return call({type:'IMPORT_QUEUE',raw:JSON.parse(await f.text())});
}));
$('current').addEventListener('click',withFeedback(()=>call({type:'CONTINUE_CURRENT'})));
$('start').addEventListener('click',withFeedback(()=>call({type:'START',maxChats:Math.min(100,Math.max(1,Number(prompt('Maximum conversations for this sweep (1–100):','1'))||1))})));
$('pause').addEventListener('click',withFeedback(()=>call({type:'STOP'})));
refresh();

$('review').addEventListener('click',withFeedback(async()=>{
  if(!lastState?.attempt){
    if(lastState?.phase!=='needs_review')return {message:'No blocker to clear.'};
    const ok=confirm('No send is recorded as in flight. Have you inspected the single ChatGPT tab and resolved the blocker?');
    return ok ? call({type:'ACK_PRE_SEND'}) : {message:'Cancelled. No checkpoint changed.'};
  }
  const decision=prompt('AFTER checking the conversation, type NOT_SENT if the message was not sent, or COMPLETED if it finished. Any other answer cancels:','');
  if(!['NOT_SENT','COMPLETED'].includes(decision))return {message:'Review cancelled; no checkpoint changed.'};
  return call({type:'REVIEW_ATTEMPT',decision});
}));
