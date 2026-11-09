// Injected only into the owner's published CF-0 Mission Control origin.
// Site code cannot call chrome.debugger; only user-trusted clicks can send commands.
const prefix='CF0 AUTO-08 Chrome · ';
const send=msg=>chrome.runtime.sendMessage(msg);
let working=false;
async function refresh(){
  if(working)return;
  working=true;
  try{
    const row=document.querySelector('#control-continuation .control-row');
    if(!row)return;
    const res=await send({type:'STATUS'});
    if(!res?.ok)return;
    const {tabs,state}=res;
    let note=row.querySelector('#cf0-chrome-adapter-status');
    if(!note){
      note=document.createElement('small');note.id='cf0-chrome-adapter-status';note.className='control-detail';
      note.style.color='#99d6ff';row.querySelector('.control-description')?.append(note);
    }
    note.textContent=prefix+`${tabs.reason} (${tabs.count} ChatGPT tab${tabs.count===1?'':'s'}) · ${state.phase}`+
      (state.reason?' · '+state.reason:'');
    const btns=[...row.querySelectorAll('.control-row-actions button')];
    const start=btns.find(b=>b.textContent.trim()==='Start');
    const resume=btns.find(b=>b.textContent.trim()==='Resume');
    const runnable=tabs.count===1&&state.account&&state.phase!=='running'&&!state.attempt&&state.phase!=='needs_review';
    if(start){start.disabled=!runnable;start.title=runnable?'Continue current chat once (Chrome extension; owner action)':'Select an account in the CF-0 extension popup and have exactly one ChatGPT tab open.';
      if(!start.dataset.cf0Wired){start.dataset.cf0Wired='1';start.addEventListener('click',async e=>{
        if(!e.isTrusted)return;
        const result=await send({type:'CONTINUE_CURRENT'});
        if(!result?.ok)alert('AUTO-08: '+(result?.error||'Cannot start'));
        refresh();
      });}}
    if(resume){resume.disabled=!(runnable&&state.phase==='paused');resume.title='Resume only after any uncertain attempt has been reviewed';
      if(!resume.dataset.cf0Wired){resume.dataset.cf0Wired='1';resume.addEventListener('click',async e=>{
        if(!e.isTrusted)return;
        const result=await send({type:'CONTINUE_CURRENT'});
        if(!result?.ok)alert('AUTO-08: '+(result?.error||'Cannot resume'));
        refresh();
      });}}
    let stop=row.querySelector('#cf0-chrome-stop');
    if(!stop){stop=document.createElement('button');stop.type='button';stop.id='cf0-chrome-stop';stop.className='control-action';stop.textContent='Stop AUTO-08';
      stop.addEventListener('click',async e=>{if(!e.isTrusted)return;await send({type:'STOP'});refresh();});
      row.querySelector('.control-row-actions')?.append(stop);
    }
    stop.disabled=state.phase!=='running';
  }catch(e){/* Extension disabled or user closed dashboard. Never claim connection. */}
  finally{working=false;}
}
refresh();setInterval(refresh,2500);
