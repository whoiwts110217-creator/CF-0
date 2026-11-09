#!/usr/bin/env node
// Run on OWNER'S desktop; requires a signed-in dedicated Chrome/Edge browser profile.
// This does not run from GitHub Pages, GitHub Actions, or the public HP relay.
import {readFile, writeFile, rename, mkdir} from 'node:fs/promises';
import {resolve, join} from 'node:path';
import {homedir} from 'node:os';
import {createInterface} from 'node:readline/promises';
import {importQueue,newCheckpoint,keyboardDriver,runSweep} from './core.mjs';

const args=process.argv.slice(2);
const value=k=>{const i=args.indexOf(k);return i>=0 ? args[i+1] : undefined;};
const has=k=>args.includes(k);
const account=value('--account');
const queueFile=value('--queue');
const browser=value('--browser')||'chrome';
const pass=Number(value('--pass')||'1');
const maximum=has('--all')?50000:Number(value('--max')||'1');
const privateRoot=join(process.env.LOCALAPPDATA||join(homedir(),'.caveman_focus'),'CavemanFocus','auto08-private');
const profile=join(privateRoot,(account||'not-selected')+'-'+browser+'-profile');
const statePath=join(privateRoot,(account||'not-selected')+'-checkpoint.json');
function usage(){
  console.log('Private AUTO-08 keyboard runner (same tab, no mouse).\n' +
    '  npm install playwright\n' +
    '  node cli.mjs --account primary --login\n' +
    '  node cli.mjs --account primary --queue PATH_TO_PRIVATE_conversations.json --dry-run\n' +
    '  node cli.mjs --account primary --queue PATH_TO_PRIVATE_conversations.json --max 1\n' +
    '  node cli.mjs --account primary --queue PATH_TO_PRIVATE_conversations.json --all\n' +
    '  Optional: --browser msedge | chrome; --pass 2 for an explicit subsequent sweep.\n' +
    '  Stop: Ctrl+C. If a send was in-flight, it stays UNKNOWN for manual review.');
}
if (has('--help') || !['primary','secondary'].includes(account) || !['chrome','msedge'].includes(browser) ||
    (!has('--login')&&!queueFile) || !Number.isSafeInteger(pass)||pass<1||
    !Number.isSafeInteger(maximum)||maximum<1) {usage();process.exitCode=1;}
else {
  await mkdir(privateRoot,{recursive:true});
  if (has('--login')) {
    const {chromium}=await import('playwright');
    const context=await chromium.launchPersistentContext(profile,{channel:browser,headless:false});
    const page=context.pages()[0]||await context.newPage();
    await page.goto('https://chatgpt.com/');
    console.log('Sign in to the explicitly selected '+account+' account. Nothing is sent automatically in --login mode.');
    const rl=createInterface({input:process.stdin,output:process.stdout});
    await rl.question('Once signed in, press Enter here to save this PRIVATE browser profile.');
    rl.close(); await context.close();
  } else {
    const queue=importQueue(JSON.parse(await readFile(resolve(queueFile),'utf8')));
    let checkpoint;
    try { checkpoint=JSON.parse(await readFile(statePath,'utf8')); }
    catch(e) { if(e?.code!=='ENOENT')throw e; checkpoint=newCheckpoint(account,queue); }
    if(checkpoint.schema!=='cf0.auto08.keyboard_checkpoint.v1'||checkpoint.account!==account)
      throw Error('Private checkpoint mismatched account/schema. Refusing to send.');
    for(const chat of queue) if(!checkpoint.entries[chat.id])checkpoint.entries[chat.id]={status:'queued',completedPass:0};
    const save=async snapshot=>{
      const tmp=statePath+'.tmp';
      await writeFile(tmp,JSON.stringify(snapshot,null,2),'utf8');
      await rename(tmp,statePath);
    };
    await save(checkpoint);
    const selected=queue.filter(c=>c.selected).length;
    console.log('Selected account: '+account+'. Private index: '+selected+' conversations. Pass '+pass+'. Cap '+maximum+'.');
    console.log('Navigates ONE browser tab directly by URL; inputs are focus + keyboard text + Enter. NO MOUSE.');
    if(has('--dry-run')) {
      console.log('Dry-run only. Checkpoint: '+statePath+'. No browser started and nothing sent.');
    } else {
      const {chromium}=await import('playwright');
      const context=await chromium.launchPersistentContext(profile,{channel:browser,headless:false});
      const page=context.pages()[0]||await context.newPage();
      const abort=new AbortController();
      process.once('SIGINT',()=>{abort.abort();void page.close().catch(()=>{});console.log('\nSTOP requested. In-flight outcome will remain unknown.');});
      try {
        const outcome=await runSweep({account,queue,checkpoint,driver:keyboardDriver(page),
          save,limit:maximum,pass,signal:abort.signal});
        console.log(JSON.stringify(outcome));
        if(outcome.status==='needs_review')process.exitCode=2;
      } finally {await context.close();}
    }
  }
}
