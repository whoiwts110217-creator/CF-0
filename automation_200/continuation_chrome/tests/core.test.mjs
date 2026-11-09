import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {chatId,chatURL,eligibleTabs,pickSingleTab,importQueue,capturedSidebarQueue,hasLoadedConversation,classifyOverlay,acknowledgedContinue,stableResponse,initialState,CONTINUE_TEXT} from '../core.mjs';
const id='11111111-1111-4111-8111-111111111111';
test('only existing, exactly one ChatGPT tab is eligible',()=>{
 assert.equal(pickSingleTab([{id:1,url:chatURL(id)},{id:2,url:'https://github.com'}]).id,1);
 assert.throws(()=>pickSingleTab([]),/NO_CHATGPT_TAB/);
 assert.throws(()=>pickSingleTab([{id:1,url:chatURL(id)},{id:3,url:'https://chatgpt.com/'}]),/MULTIPLE_CHATGPT_TABS/);
 assert.equal(eligibleTabs([{id:1,url:'https://evil.chatgpt.com/'},{id:2,url:chatURL(id)}]).length,1);
});
test('strict chat URL and private export parsing',()=>{
 assert.equal(chatId(chatURL(id)),id);
 assert.equal(chatId('https://evil.com/c/'+id),null);
 assert.throws(()=>chatURL('nope'));
 assert.equal(importQueue([{id,title:'One'},{id,title:'Duplicate'}]).length,1);
 assert.throws(()=>importQueue({}));
});
test('visible sidebar capture is bounded, local and strict about ChatGPT routes',()=>{
 const id2='22222222-2222-4222-8222-222222222222';
 const links=['/c/'+id,chatURL(id),'https://chatgpt.com/c/'+id2,
   'https://evil.com/c/'+id,'//evil.com/c/'+id,
   'https://chatgpt.com/c/not-a-uuid'];
 assert.deepEqual(capturedSidebarQueue(links).map(x=>x.id),[id,id2]);
 assert.equal(capturedSidebarQueue([]).length,0);
 assert.throws(()=>capturedSidebarQueue('not an array'),/INVALID_VISIBLE_SIDEBAR/);
 assert.throws(()=>capturedSidebarQueue(Array(2001).fill('/c/'+id)),/INVALID_VISIBLE_SIDEBAR/);
});
test('a composer with no loaded conversation must fail closed',()=>{
 assert.equal(hasLoadedConversation({userCount:0,assistantCount:0}),false);
 assert.equal(hasLoadedConversation({userCount:1,assistantCount:0}),true);
 assert.equal(hasLoadedConversation({userCount:0,assistantCount:1}),true);
 assert.equal(hasLoadedConversation({userCount:NaN,assistantCount:2}),false);
 assert.equal(hasLoadedConversation(null),false);
});
test('known harmless overlay resumes, unknown/approval/signin blocks',()=>{
 assert.equal(classifyOverlay({dialogVisible:true,dialogText:"What's new in ChatGPT"}),'DISMISS_WITH_ESCAPE');
 assert.equal(classifyOverlay({dialogVisible:true,dialogText:'Approve this purchase'}),'NEEDS_OWNER_REVIEW');
 assert.equal(classifyOverlay({signedOut:true}),'SIGN_IN_REQUIRED');
 assert.equal(classifyOverlay({rateLimit:true}),'RATE_LIMIT');
 assert.equal(classifyOverlay({dialogVisible:false}),'CLEAR');
});
test('completion requires new user and assistant turns, no Stop, stable answer',()=>{
 const x={baselineUsers:1,baselineAssistants:1,userCount:2,assistantCount:2,lastAssistantText:'30:123',lastUserExactContinue:true,stopVisible:false,busy:false,blocker:false};
 let s=stableResponse(null,x,1000,6000);
 assert.equal(s.ready,false);
 s=stableResponse(s,x,7500,6000);
 assert.equal(s.ready,true);
 assert.equal(stableResponse(s,{...x,stopVisible:true},8500,6000).ready,false);
 assert.equal(stableResponse(s,{...x,userCount:1},8500,6000).ready,false);
 assert.equal(stableResponse(s,{...x,userCount:3},8500,6000).ready,false);
 assert.equal(stableResponse(s,{...x,lastUserExactContinue:false},8500,6000).ready,false);
});
test('exact new continue acknowledgement is required; unrelated turns fail closed',()=>{
 assert.equal(acknowledgedContinue({userCount:3,lastUserExactContinue:true},2),true);
 assert.equal(acknowledgedContinue({userCount:3,lastUserExactContinue:false},2),false);
 assert.equal(acknowledgedContinue({userCount:4,lastUserExactContinue:true},2),false);
 assert.equal(acknowledgedContinue({userCount:2,lastUserExactContinue:true},2),false);
 assert.equal(acknowledgedContinue({userCount:3,lastUserExactContinue:true},NaN),false);
 assert.equal(acknowledgedContinue(null,2),false);
});
test('extension uses Chrome tab + debugger, no mouse/new tab/unknown retry',()=>{
 const bg=readFileSync(new URL('../background.js',import.meta.url),'utf8');
 const m=readFileSync(new URL('../manifest.json',import.meta.url),'utf8');
 const bridge=readFileSync(new URL('../master-control.js',import.meta.url),'utf8');
 assert.match(bg,/chrome\.tabs\.query/);
 assert.match(bg,/chrome\.debugger\.attach/);
 assert.match(bg,/Input\.insertText/);
 assert.match(bg,/Input\.dispatchKeyEvent/);
 assert.match(bg,/Page\.navigate/);
 assert.doesNotMatch(bg,/chrome\.tabs\.create|chrome\.windows\.create|\.mouse\.|\.click\(/);
 assert.match(bg,/SERVICE_WORKER_RESTART/);
 assert.match(bg,/status:'pre_send'/);
 assert.match(bg,/status:'maybe_sent'/);
 assert.match(bg,/acknowledgedContinue\(s,before\.userCount\)/);
 assert.match(bg,/lastUserExactContinue/);
 assert.match(bg,/CONVERSATION_HISTORY_NOT_LOADED/);
 assert.match(bg,/case 'CAPTURE_VISIBLE'/);
 assert.match(bridge,/isTrusted/);
 assert.match(bridge,/isTrusted/);
 assert.match(m,/whoiwts110217-creator\.github\.io/);
 assert.equal(CONTINUE_TEXT,'continue');
 assert.equal(initialState().phase,'idle');
});
