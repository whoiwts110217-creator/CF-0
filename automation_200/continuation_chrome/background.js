import {chatId,chatURL,pickSingleTab,importQueue,accountSnapshot,capturedSidebarQueue,hasLoadedConversation,classifyOverlay,readinessVerdict,acknowledgedContinue,stableResponse,initialState,CONTINUE_TEXT} from './core.mjs';

// No network listener, no remote command endpoint, no private ChatGPT API, no mouse input.
// All Chrome actions are attached to one explicitly selected existing ChatGPT tab ID.
const KEY='auto08_state_v1';
let statePromise;
// All writes share one serialized queue. STOP must never be overwritten by
// an older in-flight chrome.storage.local.set completion.
let stateWrites=Promise.resolve();
let live=null;
let launching=false;
let cancelRequested=false;
// STOP must invalidate launches that are already waiting on an async state read.
// A later, separately requested START captures the new generation and remains allowed.
let stopGeneration=0;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const stamp=()=>new Date().toISOString();
const getState=()=>statePromise ||= chrome.storage.local.get(KEY).then(async data=>{
  const s=data[KEY] && data[KEY].schema==='cf0.auto08.chrome.v1' ? data[KEY] : initialState();
  // Browser extension can restart between steps: never silently resend an uncertain request.
  if(s.phase==='running') {
    // Persist a pre-send marker before navigation, and a maybe-sent marker
    // BEFORE the first keyboard side effect. A restart in the former state
    // cannot have dispatched this runner's command; the latter is uncertain.
    const beforeSend=s.attempt?.status==='pre_send';
    if(beforeSend){s.attempt=null;s.currentChat=null;}
    s.phase='needs_review';
    s.reason=beforeSend?'SERVICE_WORKER_RESTART_BEFORE_SEND':'SERVICE_WORKER_RESTART';
    s.lastResult=beforeSend
      ? 'Worker restarted before keyboard send; check the tab, then clear the pre-send blocker.'
      : 'Worker restarted after an uncertain command boundary; inspect the conversation before retrying.';
    await chrome.storage.local.set({[KEY]:s});
  }
  return s;
});
function save(patch={}){
  const operation=stateWrites.then(async()=>{
    const s=await getState();
    // Functional patches inspect the latest state *when the write executes*.
    // This prevents STOP/catch from acting on an out-of-date attempt snapshot.
    const next=typeof patch==='function' ? patch(s) : patch;
    Object.assign(s,next,{updatedAt:stamp()});
    await chrome.storage.local.set({[KEY]:s});
    return s;
  });
  stateWrites=operation.then(()=>undefined,()=>undefined);
  return operation;
}
const debuggerTarget=tabId=>({tabId});
const ensureActive=()=>{if(cancelRequested||!live||live.stop)throw Error('STOP_REQUESTED');};
const cd=async(method,params={})=>{
  ensureActive();return chrome.debugger.sendCommand(debuggerTarget(live.tabId),method,params);
};
async function tabsSnapshot(){
  const all=await chrome.tabs.query({url:['https://chatgpt.com/*']});
  try{const tab=pickSingleTab(all);return {count:1,reason:'ONE_TAB_READY',tabId:tab.id,url:tab.url};}
  catch(e){return {count:all.length,reason:e.message,tabId:null,url:null};}
}
async function selectedTab(){
  const snap=await tabsSnapshot();if(snap.reason!=='ONE_TAB_READY')throw Error(snap.reason);
  const tab=await chrome.tabs.get(snap.tabId);
  const u=new URL(tab.url);
  if(u.origin!=='https://chatgpt.com')throw Error('WRONG_ORIGIN');
  return tab;
}
function evaluateDOM(){
  const visible=el=>{try{const c=getComputedStyle(el);return c.visibility!=='hidden'&&c.display!=='none'&&!!el.getClientRects().length;}catch{return false;}};
  const dialogs=[...document.querySelectorAll('[role="dialog"], [aria-modal="true"]')].filter(visible);
  const dialog=dialogs[0]||null;
  const notices=[...document.querySelectorAll('[role="alert"], [data-testid*="toast"]')].filter(visible);
  const noticeText=notices.slice(0,3).map(e=>(e.innerText||'').slice(0,160)).join(' ');
  const editor=[...document.querySelectorAll('#prompt-textarea,[data-testid="composer-input"],[contenteditable="true"][role="textbox"]')].find(visible);
  const users=document.querySelectorAll('[data-message-author-role="user"]');
  const lastUser=users[users.length-1];
  // Never return private user-message content to extension storage or logs.
  const lastUserExactContinue=(lastUser?.innerText||'').trim()==='continue';
  const assistants=document.querySelectorAll('[data-message-author-role="assistant"]');
  const last=assistants[assistants.length-1];
  const raw=(last?.innerText||'').trim();
  // Do not send/store message contents. Signature is used only for stability detection.
  let hash=2166136261;for(let i=0;i<raw.length;i++){hash^=raw.charCodeAt(i);hash=Math.imul(hash,16777619);}
  const dialogText=(dialog?.innerText||'').slice(0,350);
  const signedOut=!!document.querySelector('a[href*="/auth/login"],a[href*="/login"]')&&!editor;
  const stopVisible=[...document.querySelectorAll('[data-testid="stop-button"],button[aria-label*="Stop generating" i]')].some(visible);
  return {url:location.href,dialogVisible:!!dialog,dialogText,rateLimit:/too many requests|usage limit|rate limit|try again later/i.test(noticeText),
    signedOut,composerVisible:!!editor,draft:editor?(editor.innerText||editor.textContent||'').trim().slice(0,100):null,
    userCount:users.length,lastUserExactContinue,
    assistantCount:assistants.length,lastAssistantSignature:raw?`${raw.length}:${hash>>>0}`:'',
    stopVisible,busy:!!last?.querySelector('[aria-busy="true"]')};
}
async function scan(){
  ensureActive();const result=await chrome.scripting.executeScript({target:{tabId:live.tabId},func:evaluateDOM});
  return result?.[0]?.result||{};
}
async function focusComposer(){
  ensureActive();const result=await chrome.scripting.executeScript({target:{tabId:live.tabId},func:()=>{
    const visible=el=>{const c=getComputedStyle(el);return c.visibility!=='hidden'&&c.display!=='none'&&!!el.getClientRects().length;};
    // A modal can appear after the preceding scan but before we focus the editor.
    const modal=[...document.querySelectorAll('[role="dialog"],[aria-modal="true"]')].some(visible);
    if(modal)return 'BLOCKING_DIALOG';
    const editor=[...document.querySelectorAll('#prompt-textarea,[data-testid="composer-input"],[contenteditable="true"][role="textbox"]')].find(visible);
    if(!editor)return 'MISSING_COMPOSER';
    if((editor.innerText||editor.textContent||'').trim())return 'OWNER_DRAFT_PRESENT';
    editor.focus();return document.activeElement===editor || editor.contains(document.activeElement)?'FOCUSED':'FOCUS_FAILED';
  }});
  if(result?.[0]?.result!=='FOCUSED')throw Error(result?.[0]?.result||'FOCUS_UNKNOWN');
}
async function key(name){
  ensureActive();const code=name==='Escape'?27:13;
  await cd('Input.dispatchKeyEvent',{type:'rawKeyDown',key:name,code:name,windowsVirtualKeyCode:code,nativeVirtualKeyCode:code});
  await cd('Input.dispatchKeyEvent',{type:'keyUp',key:name,code:name,windowsVirtualKeyCode:code,nativeVirtualKeyCode:code});
}
async function handleOverlay(snapshot){
  const c=classifyOverlay(snapshot);
  if(c==='CLEAR')return false;
  if(c==='DISMISS_WITH_ESCAPE'){
    if(++live.escapes>2)throw Error('REPEATED_POPUP');
    await key('Escape');
    // Never proceed using the OLD snapshot: the dialog could still be visible.
    // The caller must rescan and prove the obstruction disappeared first.
    await sleep(500);
    return true;
  }
  throw Error(c);
}
async function waitUntil(check,timeoutMs,expectedId,{allowNavigation=false}={}){
  const deadline=Date.now()+timeoutMs;
  const navigationGrace=Date.now()+12000;
  let lastError;
  while(Date.now()<deadline){
    ensureActive();
    const tabs=await tabsSnapshot();
    if(tabs.reason!=='ONE_TAB_READY'||tabs.tabId!==live.tabId)
      throw Error('CHATGPT_TAB_COUNT_CHANGED');
    const tab=await chrome.tabs.get(live.tabId).catch(()=>null);
    if(!tab)throw Error('TAB_CLOSED');
    if(chatId(tab.url)!==expectedId) {
      if(!chatId(tab.url)&&/login|auth/.test(tab.url||''))throw Error('SIGN_IN_REQUIRED');
      if(allowNavigation&&Date.now()<navigationGrace){await sleep(400);continue;}
      throw Error('TAB_NAVIGATED_AWAY');
    }
    let snap;
    try{snap=await scan();}catch(e){lastError=e;await sleep(600);continue;}
    if(snap.url&&chatId(snap.url)!==expectedId){
      if(allowNavigation&&Date.now()<navigationGrace){await sleep(400);continue;}
      throw Error('PAGE_CONTENT_MISMATCH');
    }
    const dismissed=await handleOverlay(snap);
    if(dismissed)continue; // Check the FRESH DOM before typing or marking completion.
    const ok=await check(snap);
    if(ok)return snap;
    await sleep(800);
  }
  throw Error(lastError?.message||'WAIT_TIMEOUT');
}
async function attachOneTab(){
  const tab=await selectedTab();
  live={tabId:tab.id,stop:false,escapes:0,attached:false,dialogIssue:null,popupCount:0};
  if(cancelRequested)throw Error('STOP_REQUESTED');
  await chrome.debugger.attach(debuggerTarget(tab.id),'1.3');
  live.attached=true;
  ensureActive();
  await cd('Page.enable');
  await save({selectedTabId:tab.id,phase:'running',reason:null,lastResult:'Attached to one existing Chrome ChatGPT tab; no new tab created.'});
  return tab;
}
async function navigate(id){
  ensureActive();
  const tab=await chrome.tabs.get(live.tabId);
  if(chatId(tab.url)!==id)await cd('Page.navigate',{url:chatURL(id)});
  // A busy conversation may hide the editor. Detect it before waiting for a
  // composer that cannot appear until generation stops.
  await waitUntil(s=>s.composerVisible||s.stopVisible||s.busy,40000,id,{allowNavigation:true});
}
async function continueOne(id,{advanceAfterAck=false}={}){
  await save({currentChat:id,attempt:{chatId:id,status:'pre_send',startedAt:stamp()},lastResult:'Navigating in selected tab; no keyboard send yet…'});
  await navigate(id);
  // The navigation wait verified the absence of known blocking overlays.
  // Refresh that evidence immediately before any keyboard input.
  let before=await scan();
  if(before.url&&chatId(before.url)!==id)throw Error('PAGE_CONTENT_MISMATCH');
  if(await handleOverlay(before)){
    await waitUntil(s=>s.composerVisible,20000,id);
    before=await scan();
    if(await handleOverlay(before))throw Error('PERSISTENT_POPUP');
  }
  // Other-account/missing-history pages may still display a usable composer.
  // Do not turn the failed navigation into a fresh ChatGPT conversation.
  if(!hasLoadedConversation(before))throw Error('CONVERSATION_HISTORY_NOT_LOADED');
  if(before.stopVisible||before.busy)throw Error('ALREADY_RESPONDING');
  if(!before.composerVisible)throw Error('COMPOSER_NOT_READY');
  if(before.draft)throw Error('OWNER_DRAFT_PRESENT');
  await focusComposer();
  ensureActive();
  // Durable side-effect boundary, BEFORE any keyboard action. If Chrome stops
  // after this point, never auto-retry; the exact send outcome is unknown.
  await save({attempt:{chatId:id,status:'maybe_sent',startedAt:stamp()},
    lastResult:'Keyboard send boundary armed; outcome may require review.'});
  ensureActive();
  await cd('Input.insertText',{text:CONTINUE_TEXT});
  await key('Enter');
  await save({lastResult:'Sent continue; waiting for response to finish…'});
  await waitUntil(s=>acknowledgedContinue(s,before.userCount),20000,id);
  if(advanceAfterAck){
    // Explicit owner-selected FAST mode: this is only a verified user-turn
    // submission. Navigating immediately may interrupt reply generation.
    // Do not call it a completed assistant response or silently retry it.
    ensureActive();
    await save(s=>({attempt:null,currentChat:null,
      submitted:[...new Set([...(Array.isArray(s.submitted)?s.submitted:[]),id])],
      lastResult:'Acknowledged literal continue submission; reply NOT verified (fast mode).'}));
    ensureActive();
    return;
  }
  let stable=null;
  await waitUntil(s=>{
    if(!acknowledgedContinue(s,before.userCount))throw Error('CONTINUE_ACK_LOST');
    stable=stableResponse(stable,{...s, baselineUsers:before.userCount,
      baselineAssistants:before.assistantCount,lastAssistantText:s.lastAssistantSignature,
      blocker:!!live.dialogIssue},Date.now());
    return stable.ready;
  },240000,id);
  ensureActive();
  await save(s=>({attempt:null,currentChat:null,
    completed:[...new Set([...s.completed,id])],
    lastResult:'Completed one chat and verified stable response.'}));
  ensureActive();
}
async function execute({mode,maxChats=1,advanceAfterAck=false}){
  if(live)throw Error('ALREADY_RUNNING');
  const s=await getState();
  if(!['primary','secondary'].includes(s.account))throw Error('SELECT_ACCOUNT_FIRST');
  if(s.attempt||s.phase==='needs_review')throw Error('UNCERTAIN_ATTEMPT_REQUIRES_REVIEW');
  const tab=await selectedTab();
  const q=mode==='current'?[{id:chatId(tab.url)}]:s.queue;
  if(!q.length||q.some(x=>!x?.id))throw Error('NO_CONVERSATION_SELECTED');
  if(!Number.isSafeInteger(maxChats)||maxChats<1||maxChats>100)throw Error('INVALID_CHAT_LIMIT');
  if(advanceAfterAck && mode!=='queue')throw Error('FAST_MODE_QUEUE_ONLY');
  const alreadySubmitted=Array.isArray(s.submitted)?s.submitted:[];
  const toDo=(mode==='current'?q:q.filter(x=>!s.completed.includes(x.id)&&!alreadySubmitted.includes(x.id))).slice(0,maxChats);
  // A busy thread is only deferred for THIS sweep. Do not mark it submitted
  // or completed, so a future owner-initiated sweep can reconsider it.
  const skippedBusy=[];
  let outcome='completed';
  try{
    if(cancelRequested)throw Error('STOP_REQUESTED');
    // Attach can fail (permission revoked, tab closed, Chrome debugger conflict).
    // Cleanup MUST still run, or the dead "live" marker blocks every future run.
    await attachOneTab();
    for(const c of toDo){
      ensureActive();
      const count=(await tabsSnapshot());
      if(count.count!==1||count.tabId!==live.tabId)throw Error('CHATGPT_TAB_COUNT_CHANGED');
      live.escapes=0;
      try {
        await continueOne(c.id,{advanceAfterAck});
      } catch(error) {
        // The owner requested full-queue coverage: skip an already-generating
        // chat *only* when no keyboard command has begun. Never swallow
        // unknown sends, owner drafts, sign-in, tab changes or STOP.
        const attempt=(await getState()).attempt;
        if(mode==='queue' && error?.message==='ALREADY_RESPONDING' &&
           attempt?.chatId===c.id && attempt.status==='pre_send' &&
           !cancelRequested && !live?.stop){
          skippedBusy.push(c.id);
          await save({attempt:null,currentChat:null,
            lastResult:`Skipped busy chat ${skippedBusy.length}; no continue was sent. Moving to next chat.`});
          continue;
        }
        throw error;
      }
    }
    ensureActive();
    const worked=toDo.length-skippedBusy.length;
    await save({phase:'idle',reason:null,lastResult:advanceAfterAck
      ? `Acknowledged ${worked} continue submission(s); skipped ${skippedBusy.length} busy chat(s). Replies NOT verified.`
      : `Finished ${worked} conversation(s); skipped ${skippedBusy.length} busy chat(s) in the same Chrome tab.`});
    ensureActive();
  }catch(error){
    outcome='needs_review';
    const reason=live?.dialogIssue||error.message||'UNKNOWN_ERROR';
    const ownerStop=cancelRequested||live?.stopReason==='USER_STOP';
    await save(s=>{
      const beforeSend=s.attempt?.status==='pre_send';
      const uncertain=!!s.attempt&&!beforeSend;
      const paused=ownerStop&&!uncertain;
      return {phase:paused?'paused':'needs_review',
        reason:ownerStop?'USER_STOP':reason,
        attempt:beforeSend?null:s.attempt,
        currentChat:beforeSend?null:s.currentChat,
        lastResult:paused
          ? 'Stopped before the next keyboard send. No uncertain attempt is recorded; resume only when ready.'
          : beforeSend
            ? `Stopped before keyboard send: ${reason}. Check the tab and acknowledge the pre-send blocker.`
            : `Stopped after uncertain send boundary: ${reason}. Review the conversation; no automatic duplicate send.`};
    });
  }finally{
    if(live?.attached){try{await chrome.debugger.detach(debuggerTarget(live.tabId));}catch{}}
    live=null;
  }
  return {ok:outcome==='completed',message:(await getState()).lastResult};
}
chrome.debugger.onEvent.addListener(async(source,method,params)=>{
  if(!live||source.tabId!==live.tabId)return;
  if(method==='Page.javascriptDialogOpening'){
    if(params.type==='alert'){
      try{await chrome.debugger.sendCommand(debuggerTarget(live.tabId),'Page.handleJavaScriptDialog',{accept:false});}catch{
        live.dialogIssue='BROWSER_ALERT_UNRESOLVED';live.stop=true;
      }
    }else{
      live.dialogIssue='BROWSER_'+String(params.type).toUpperCase()+'_NEEDS_OWNER';live.stop=true;
    }
  }
});
chrome.debugger.onDetach.addListener(source=>{
  if(live&&source.tabId===live.tabId){live.dialogIssue='CHROME_DEBUGGER_DETACHED';live.stop=true;}
});
chrome.tabs.onRemoved.addListener(tabId=>{if(live?.tabId===tabId){live.stop=true;live.dialogIssue='CHATGPT_TAB_CLOSED';}});
chrome.tabs.onCreated.addListener(async(tab)=>{
  if(!live||tab.openerTabId!==live.tabId)return;
  live.popupCount++;
  try{await chrome.tabs.update(live.tabId,{active:true});}catch{}
  // We never close or control newly created tabs. Unknown sign-in popups need owner review.
  live.dialogIssue='NEW_POPUP_TAB_NEEDS_OWNER_REVIEW';live.stop=true;
});
chrome.runtime.onMessage.addListener((message,sender,sendResponse)=>{
  // Immediate cancellation intent: never wait on a slow Chrome storage read
  // before telling an already-starting worker to stop.
  if(message?.type==='STOP'){
    stopGeneration++;
    cancelRequested=true;
    if(live){live.stop=true;live.stopReason='USER_STOP';}
  }
  const launchGeneration=stopGeneration;
  (async()=>{
    const s=await getState();
    switch(message?.type){
      case 'STATUS':
        // During launch preflight, don't block STATUS behind the same slow
        // tab query the owner may be trying to cancel. STOP stays reachable.
        return {ok:true,state:s,launching,
          tabs:launching&&!live
            ? {count:null,reason:'STARTING_TAB_CHECK',tabId:null,url:null}
            : await tabsSnapshot()};
      case 'PREFLIGHT':{
        if(live||launching)throw Error('RUNNER_ALREADY_ACTIVE');
        if(!s.account)return {ok:true,ready:false,reason:'SELECT_ACCOUNT_FIRST',
          message:'Choose the manually verified account label; no message sent.'};
        if(s.phase==='needs_review'||s.attempt)return {ok:true,ready:false,
          reason:'UNRESOLVED_ATTEMPT_REQUIRES_REVIEW',
          message:'Review the uncertain attempt first. No message sent.'};
        const tab=await selectedTab();
        const expected=chatId(tab.url);
        if(!expected)return {ok:true,ready:false,reason:'OPEN_A_CONVERSATION_FIRST',
          message:'Open one existing conversation, not a new-chat page. No message sent.'};
        let scan;
        try{
          const result=await chrome.scripting.executeScript({target:{tabId:tab.id},func:evaluateDOM});
          scan=result?.[0]?.result;
        }catch{
          return {ok:true,ready:false,reason:'PAGE_INSPECTION_UNAVAILABLE',
            message:'Cannot inspect the current conversation. No message sent.'};
        }
        const reason=readinessVerdict(scan,expected);
        return {ok:true,ready:reason==='READY_ACCOUNT_UNVERIFIED',reason,
          message:reason==='READY_ACCOUNT_UNVERIFIED'
            ? 'Page checks pass. Account identity is NOT verified: inspect the signed-in ChatGPT account yourself before Continue current chat once. No message sent.'
            : `Readiness blocked: ${reason}. No message sent or tab changed.`};
      }
      case 'SET_ACCOUNT':{
        if(live||launching)throw Error('CANNOT_CHANGE_ACCOUNT_WHILE_RUNNING');
        if(!['primary','secondary'].includes(message.account))throw Error('SELECT_VALID_ACCOUNT');
        if(s.attempt)throw Error('UNRESOLVED_ATTEMPT_REQUIRES_REVIEW');
        if(s.phase==='needs_review')throw Error('CLEAR_BLOCKER_BEFORE_ACCOUNT_CHANGE');
        await save({...accountSnapshot(s,message.account),phase:'idle',reason:null});
        return {ok:true,message:'Account label selected. Verify the ChatGPT login in the tab; this is not an identity check.'};
      }
      case 'IMPORT_QUEUE':{
        if(live||launching)throw Error('RUNNING');
        // Reimport must NEVER erase an uncertain send and allow a duplicate.
        if(s.attempt||s.phase==='needs_review')throw Error('UNRESOLVED_ATTEMPT_REQUIRES_REVIEW');
        const queue=importQueue(message.raw);
        // Reimport replaces the queue but cannot erase the completed history;
        // otherwise a previously completed conversation could be sent again.
        await save({queue,phase:'idle',reason:null});
        return {ok:true,message:`Loaded ${queue.length} private conversation IDs; ${s.completed.length} prior completed checkpoints preserved. No messages sent.`};
      }
      case 'CAPTURE_VISIBLE':{
        if(live||launching)throw Error('CANNOT_CAPTURE_WHILE_RUNNING');
        if(!s.account)throw Error('SELECT_ACCOUNT_FIRST');
        if(s.attempt||s.phase==='needs_review')throw Error('UNRESOLVED_ATTEMPT_REQUIRES_REVIEW');
        const tab=await selectedTab();
        const result=await chrome.scripting.executeScript({target:{tabId:tab.id},func:()=>{
          const visible=e=>{try{const c=getComputedStyle(e);return c.visibility!=='hidden'&&c.display!=='none'&&!!e.getClientRects().length;}catch{return false;}};
          const links=[...document.querySelectorAll('nav a[href],aside a[href]')].filter(visible)
            .slice(0,2000).map(a=>a.getAttribute('href')).filter(x=>typeof x==='string');
          return {url:location.href,links};
        }});
        const scan=result?.[0]?.result;
        if(!scan || new URL(scan.url).origin!=='https://chatgpt.com')throw Error('WRONG_PAGE_ORIGIN');
        const found=capturedSidebarQueue(scan.links);
        const seen=new Set(s.queue.map(x=>x.id));
        const added=found.filter(x=>!seen.has(x.id));
        if(added.length){
          await save({queue:[...s.queue,...added],lastResult:`Captured ${added.length} additional visible sidebar chats; account identity remains owner-selected and unverified.`});
        }
        return {ok:true,message:`Captured ${found.length} visible chats (${added.length} new; ${s.queue.length+added.length} queued). This is not a full account discovery. No message sent.`};
      }
      case 'CONTINUE_CURRENT': {
        if(stopGeneration!==launchGeneration)throw Error('STOP_REQUESTED');
        if(live||launching)throw Error('ALREADY_RUNNING');
        if(!s.account)throw Error('SELECT_ACCOUNT_FIRST');
        launching=true;
        cancelRequested=false;
        try{
          const tab=await selectedTab();
          if(!chatId(tab.url))throw Error('OPEN_A_CONVERSATION_FIRST');
          if(cancelRequested)throw Error('STOP_REQUESTED');
          void execute({mode:'current',maxChats:1}).catch(async e=>{
            await save({phase:'needs_review',reason:e.message,lastResult:'Start failed: '+e.message});
          }).finally(()=>{launching=false;});
          return {ok:true,message:'Requested one-chat test using existing tab.'};
        }catch(e){
          launching=false;
          throw e;
        }
      }
      case 'START': {
        if(stopGeneration!==launchGeneration)throw Error('STOP_REQUESTED');
        if(live||launching)throw Error('ALREADY_RUNNING');
        if(!s.account)throw Error('SELECT_ACCOUNT_FIRST');
        if(!s.queue.length)throw Error('IMPORT_QUEUE_FIRST');
        launching=true;
        cancelRequested=false;
        try{
          await selectedTab();
          if(cancelRequested)throw Error('STOP_REQUESTED');
          void execute({mode:'queue',maxChats:message.maxChats,
            advanceAfterAck:message.advanceAfterAck===true}).catch(async e=>{
            await save({phase:'needs_review',reason:e.message,lastResult:'Start failed: '+e.message});
          }).finally(()=>{launching=false;});
          return {ok:true,message:'Requested imported queue using existing tab.'};
        }catch(e){
          launching=false;
          throw e;
        }
      }
      case 'STOP':
        cancelRequested=true;
        if(live){
          // Set cancellation synchronously, BEFORE the first await.
          live.stop=true;live.stopReason='USER_STOP';
        }
        await save(current=>{
          const uncertain=!!current.attempt&&current.attempt.status!=='pre_send';
          return {phase:uncertain?'needs_review':'paused',reason:'USER_STOP',
            lastResult:uncertain
              ? 'STOP accepted. The current send outcome is uncertain; inspect the chat before retrying.'
              : 'STOP accepted. No uncertain send is recorded; future sends remain paused.'};
        });
        return {ok:true,message:'Stop accepted for AUTO-08. The Chrome tab remains open.'};
      case 'ACK_PRE_SEND': {
        if(live||launching)throw Error('CANNOT_CLEAR_WHILE_RUNNING');
        if(s.phase!=='needs_review'||s.attempt)throw Error('NO_SAFE_PRE_SEND_BLOCKER');
        const tabs=await tabsSnapshot();
        if(tabs.reason!=='ONE_TAB_READY')throw Error('ONE_CHATGPT_TAB_REQUIRED');
        await save({phase:'paused',reason:'PRE_SEND_BLOCKER_ACKNOWLEDGED',
          lastResult:'Owner acknowledged a blocker with no in-flight send. Runner remains paused until started again.'});
        return {ok:true,message:'Pre-send blocker acknowledged. Start again only after inspecting the tab.'};
      }
      case 'REVIEW_ATTEMPT': {
        if(live||launching)throw Error('CANNOT_REVIEW_WHILE_RUNNING');
        if(!s.attempt || s.phase!=='needs_review')throw Error('NO_UNCERTAIN_ATTEMPT');
        if(!['NOT_SENT','COMPLETED'].includes(message.decision))throw Error('INVALID_REVIEW_CHOICE');
        const completed=message.decision==='COMPLETED'
          ? [...new Set([...s.completed,s.attempt.chatId])] : s.completed;
        await save({attempt:null,currentChat:null,completed,phase:'paused',reason:'OWNER_REVIEWED',
          lastResult:'Owner reviewed chat and marked outcome '+message.decision+'. Resume is now permitted.'});
        return {ok:true,message:'Reviewed. You can resume after checking account and tab.'};
      }
      default:throw Error('UNKNOWN_COMMAND');
    }
  })().then(sendResponse).catch(e=>sendResponse({ok:false,error:e.message||'UNKNOWN'}));
  return true;
});
