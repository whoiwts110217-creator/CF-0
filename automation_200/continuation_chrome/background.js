import {chatId,chatURL,pickSingleTab,importQueue,classifyOverlay,stableResponse,initialState,CONTINUE_TEXT} from './core.mjs';

// No network listener, no remote command endpoint, no private ChatGPT API, no mouse input.
// All Chrome actions are attached to one explicitly selected existing ChatGPT tab ID.
const KEY='auto08_state_v1';
let statePromise;
let live=null;
let launching=false;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const stamp=()=>new Date().toISOString();
const getState=()=>statePromise ||= chrome.storage.local.get(KEY).then(async data=>{
  const s=data[KEY] && data[KEY].schema==='cf0.auto08.chrome.v1' ? data[KEY] : initialState();
  // Browser extension can restart between steps: never silently resend an uncertain request.
  if(s.phase==='running') {
    s.phase='needs_review';s.reason='SERVICE_WORKER_RESTART';
    s.lastResult='Worker restarted mid-run; review the selected chat before retrying.';
    await chrome.storage.local.set({[KEY]:s});
  }
  return s;
});
async function save(patch={}){
  const s=await getState();Object.assign(s,patch,{updatedAt:stamp()});
  await chrome.storage.local.set({[KEY]:s});return s;
}
const debuggerTarget=tabId=>({tabId});
const ensureActive=()=>{if(!live||live.stop)throw Error('STOP_REQUESTED');};
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
    userCount:document.querySelectorAll('[data-message-author-role="user"]').length,
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
  await chrome.debugger.attach(debuggerTarget(tab.id),'1.3');
  live.attached=true;
  await cd('Page.enable');
  await save({selectedTabId:tab.id,phase:'running',reason:null,lastResult:'Attached to one existing Chrome ChatGPT tab; no new tab created.'});
  return tab;
}
async function navigate(id){
  ensureActive();
  const tab=await chrome.tabs.get(live.tabId);
  if(chatId(tab.url)!==id)await cd('Page.navigate',{url:chatURL(id)});
  await waitUntil(s=>s.composerVisible,40000,id,{allowNavigation:true});
}
async function continueOne(id){
  await save({currentChat:id,attempt:{chatId:id,status:'in_flight',startedAt:stamp()},lastResult:'Navigating in selected tab…'});
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
  if(!before.composerVisible)throw Error('COMPOSER_NOT_READY');
  if(before.stopVisible||before.busy)throw Error('ALREADY_RESPONDING');
  if(before.draft)throw Error('OWNER_DRAFT_PRESENT');
  await focusComposer();
  await cd('Input.insertText',{text:CONTINUE_TEXT});
  await key('Enter');
  await save({lastResult:'Sent continue; waiting for response to finish…'});
  await waitUntil(s=>s.userCount>before.userCount,20000,id);
  let stable=null;
  await waitUntil(s=>{
    stable=stableResponse(stable,{...s, baselineUsers:before.userCount,
      baselineAssistants:before.assistantCount,lastAssistantText:s.lastAssistantSignature,
      blocker:!!live.dialogIssue},Date.now());
    return stable.ready;
  },240000,id);
  const s=await getState();
  await save({attempt:null,currentChat:null,completed:[...new Set([...s.completed,id])],lastResult:'Completed one chat and verified stable response.'});
}
async function execute({mode,maxChats=1}){
  if(live)throw Error('ALREADY_RUNNING');
  const s=await getState();
  if(!['primary','secondary'].includes(s.account))throw Error('SELECT_ACCOUNT_FIRST');
  if(s.attempt||s.phase==='needs_review')throw Error('UNCERTAIN_ATTEMPT_REQUIRES_REVIEW');
  const tab=await selectedTab();
  const q=mode==='current'?[{id:chatId(tab.url)}]:s.queue;
  if(!q.length||q.some(x=>!x?.id))throw Error('NO_CONVERSATION_SELECTED');
  if(!Number.isSafeInteger(maxChats)||maxChats<1||maxChats>100)throw Error('INVALID_CHAT_LIMIT');
  await attachOneTab();
  const toDo=(mode==='current'?q:q.filter(x=>!s.completed.includes(x.id))).slice(0,maxChats);
  let outcome='completed';
  try{
    for(const c of toDo){
      ensureActive();
      const count=(await tabsSnapshot());
      if(count.count!==1||count.tabId!==live.tabId)throw Error('CHATGPT_TAB_COUNT_CHANGED');
      live.escapes=0;
      await continueOne(c.id);
    }
    await save({phase:'idle',reason:null,lastResult:`Finished ${toDo.length} conversation(s) with the same Chrome tab.`});
  }catch(error){
    outcome='needs_review';
    const reason=live?.dialogIssue||error.message||'UNKNOWN_ERROR';
    await save({phase:'needs_review',reason,
      lastResult:`Stopped: ${reason}. Check the current conversation before retrying; no automatic duplicate send.`});
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
  (async()=>{
    const s=await getState();
    switch(message?.type){
      case 'STATUS':return {ok:true,state:s,tabs:await tabsSnapshot()};
      case 'SET_ACCOUNT':{
        if(live||launching)throw Error('CANNOT_CHANGE_ACCOUNT_WHILE_RUNNING');
        if(!['primary','secondary'].includes(message.account))throw Error('SELECT_VALID_ACCOUNT');
        if(s.attempt)throw Error('UNRESOLVED_ATTEMPT_REQUIRES_REVIEW');
        if(s.phase==='needs_review')throw Error('CLEAR_BLOCKER_BEFORE_ACCOUNT_CHANGE');
        await save({account:message.account,completed:s.account===message.account?s.completed:[],queue:s.account===message.account?s.queue:[],phase:'idle',reason:null});
        return {ok:true,message:'Account label selected. Verify the ChatGPT login in the tab; this is not an identity check.'};
      }
      case 'IMPORT_QUEUE':{
        if(live||launching)throw Error('RUNNING');
        // Reimport must NEVER erase an uncertain send and allow a duplicate.
        if(s.attempt||s.phase==='needs_review')throw Error('UNRESOLVED_ATTEMPT_REQUIRES_REVIEW');
        const queue=importQueue(message.raw);
        await save({queue,completed:[],phase:'idle',reason:null});
        return {ok:true,message:`Loaded ${queue.length} private conversation IDs. No messages sent.`};
      }
      case 'CONTINUE_CURRENT': {
        if(live||launching)throw Error('ALREADY_RUNNING');
        if(!s.account)throw Error('SELECT_ACCOUNT_FIRST');
        const tab=await selectedTab();if(!chatId(tab.url))throw Error('OPEN_A_CONVERSATION_FIRST');
        launching=true;
        void execute({mode:'current',maxChats:1}).catch(async e=>{
          await save({phase:'needs_review',reason:e.message,lastResult:'Start failed: '+e.message});
        }).finally(()=>{launching=false;});
        return {ok:true,message:'Requested one-chat test using existing tab.'};
      }
      case 'START': {
        if(live||launching)throw Error('ALREADY_RUNNING');
        if(!s.account)throw Error('SELECT_ACCOUNT_FIRST');
        if(!s.queue.length)throw Error('IMPORT_QUEUE_FIRST');
        await selectedTab();
        launching=true;
        void execute({mode:'queue',maxChats:message.maxChats}).catch(async e=>{
          await save({phase:'needs_review',reason:e.message,lastResult:'Start failed: '+e.message});
        }).finally(()=>{launching=false;});
        return {ok:true,message:'Requested imported queue using existing tab.'};
      }
      case 'STOP':
        if(live){live.stop=true;await save({phase:'paused',reason:'USER_STOP',lastResult:'Stop requested. In-flight chat outcome requires review.'});}
        else await save({phase:s.attempt?'needs_review':'paused',reason:'USER_STOP',lastResult:'Paused; no current runner.'});
        return {ok:true,message:'Stop requested. Chrome remains open.'};
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
