// Free, dependency-free headless Chromium integration smoke test.
// Executes the real Gambatte-derived browser core against road-v01.gb.
// Not a physical iPhone or real hardware test.
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { join, normalize, extname } from 'node:path';
import { tmpdir } from 'node:os';

const root = new URL('../site/', import.meta.url).pathname;
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const mime = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.gb':'application/octet-stream','.svg':'image/svg+xml','.webmanifest':'application/manifest+json'};
const server=createServer(async(req,res)=>{
  const path=normalize(decodeURIComponent((req.url||'/').split('?')[0])).replace(/^\/+/, '');
  if(path.startsWith('..')){res.writeHead(403);res.end();return}
  try{
    const name=join(root,path||'index.html'),data=await readFile(name);
    res.writeHead(200,{'content-type':mime[extname(name)]||'application/octet-stream','cache-control':'no-cache'});
    res.end(data)
  }catch(e){res.writeHead(404);res.end('Not found')}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin='http://127.0.0.1:'+server.address().port+'/';
const chromeExe=process.env.DK_CHROME || 'google-chrome';
const chrome=spawn(chromeExe,['--headless=new','--no-sandbox','--disable-gpu','--no-first-run','--disable-dev-shm-usage','--remote-debugging-port=9227','--user-data-dir='+join(tmpdir(),'dk-chrome-'+process.pid),'about:blank'],{stdio:'ignore'});
let socket=null;
async function debuggerUrl(){
 for(let i=0;i<100;i++){
   try{
     const data=await fetch('http://127.0.0.1:9227/json');
     if(data.ok){const targets=await data.json();const tab=targets.find(x=>x.type==='page');if(tab?.webSocketDebuggerUrl)return tab.webSocketDebuggerUrl}
   }catch(e){}
   await sleep(100)
 }
 throw Error('Could not connect to Chromium debugging endpoint');
}
let requestId=0;const pending=new Map();
function send(method,params={}){
 const id=++requestId;
 return new Promise((resolve,reject)=>{
  const timeout=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method))},20000);
  pending.set(id,{resolve,reject,timeout});
  socket.send(JSON.stringify({id,method,params}));
 });
}
async function evaluate(expression){
 const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
 if(r.error||r.result?.exceptionDetails)throw Error('Browser JS failed: '+JSON.stringify(r.error||r.result.exceptionDetails));
 return r.result?.result?.value;
}
try{
 const endpoint=await debuggerUrl();
 socket=new WebSocket(endpoint);
 await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject});
 socket.onmessage=e=>{const m=JSON.parse(e.data);if(!m.id)return;const p=pending.get(m.id);if(!p)return;clearTimeout(p.timeout);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m)};
 await send('Runtime.enable');await send('Page.enable');await send('Page.navigate',{url:origin});
 await sleep(1200);
 const initial=await evaluate('({ready:document.readyState,emulator:typeof window.embedGameBoy,button:!!document.getElementById("road-button")})');
 if(initial.emulator!=='function'||!initial.button)throw Error('Emulator core or launcher button unavailable: '+JSON.stringify(initial));
 await evaluate('document.getElementById("road-button").click()');
 await sleep(1800);
 const state=await evaluate('({launched:!document.getElementById("playing").classList.contains("hidden"),title:document.getElementById("rom-title").textContent,status:document.getElementById("status-line").textContent,canvas:document.querySelectorAll("#game canvas").length,children:document.getElementById("game").childElementCount})');
 console.log('Emulator launch observation:',JSON.stringify(state));
 if(!state.launched||!state.title.includes('ROAD')||!state.canvas)throw Error('Road ROM did not render a browser emulator canvas');
 const pixels=await evaluate(`(()=>{const c=document.querySelector("#game canvas");const context=c?.getContext("2d");if(!context)return {error:"2D canvas unavailable"};const d=context.getImageData(0,0,c.width,c.height).data;const unique=new Set();for(let i=0;i<d.length;i+=4){unique.add([d[i],d[i+1],d[i+2],d[i+3]].join(","));if(unique.size>5)break}return {width:c.width,height:c.height,colors:unique.size}})()`);
 console.log('Emulated frame pixels:',JSON.stringify(pixels));
 if(pixels.error||pixels.colors<2)throw Error('ROM canvas did not paint nonblank pixel data');

 console.log('PASS: GameBoy.js initialized the original Road cartridge in headless Chromium.');
}catch(e){console.error('BROWSER SMOKE FAILED:',e);process.exitCode=1}
finally{for(const p of pending.values())clearTimeout(p.timeout);if(socket)socket.close();chrome.kill('SIGKILL');await new Promise(resolve=>server.close(resolve))}
