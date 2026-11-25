/* CF Link Vault: network-first for page + catalog, cached fallback when offline. */
const CACHE="cf-link-vault-v8";
const ASSETS=["./","./index.html","./enhance.js","./privacy-controls.js","./links.json","./owner-actions.js","./project-paths.js","./spider-core.js","./spider-shell.js","./owner-actions.css","./owner-actions.json","./manifest.webmanifest","./icon.svg"];
self.addEventListener("install",event=>{
 event.waitUntil(caches.open(CACHE).then(async cache=>{
   for(const path of ASSETS){try{await cache.add(path)}catch(_){}}
 }).then(()=>self.skipWaiting()));
});
self.addEventListener("activate",event=>{
 event.waitUntil(Promise.all([
   caches.keys().then(keys=>Promise.all(keys.filter(x=>x.startsWith("cf-link-vault-")&&x!==CACHE).map(x=>caches.delete(x)))),
   self.clients.claim()
 ]));
});
self.addEventListener("fetch",event=>{
 const req=event.request,u=new URL(req.url);
 if(req.method!=="GET" || u.origin!==self.location.origin || !u.pathname.includes("/link-vault/"))return;
 event.respondWith((async()=>{
   const cache=await caches.open(CACHE);
   const hot=req.mode==="navigate" || /\/(index\.html|links\.json|enhance\.js|privacy-controls\.js|owner-actions\.js|project-paths\.js|spider-core\.js|spider-shell\.js|owner-actions\.css|owner-actions\.json)$/.test(u.pathname);
   if(hot){
     const matched=["links.json","enhance.js","privacy-controls.js","owner-actions.js","project-paths.js","spider-core.js","spider-shell.js","owner-actions.css","owner-actions.json"].find(x=>u.pathname.endsWith("/"+x));
   const key=matched?"./"+matched:"./index.html";
     try{const network=await fetch(req);if(network.ok)await cache.put(key,network.clone());return network}
     catch(_){
       const saved=await cache.match(key);
       if(saved)return saved;
       return req.mode==="navigate" ? (await cache.match("./index.html") || Response.error()) : Response.error();
     }
   }
   const cached=await cache.match(req,{ignoreSearch:true});
   if(cached)return cached;
   try{const network=await fetch(req);if(network.ok)await cache.put(req,network.clone());return network}
   catch(_){return Response.error()}
 })());
});