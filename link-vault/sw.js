/* CF Link Vault: network-first for page + catalog, cached fallback when offline. */
const CACHE="cf-link-vault-v2";
const ASSETS=["./","./index.html","./enhance.js","./links.json","./manifest.webmanifest","./icon.svg"];
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
   const hot=req.mode==="navigate" || /\/(index\.html|links\.json|enhance\.js)$/.test(u.pathname);
   if(hot){
     try{const network=await fetch(req);if(network.ok)await cache.put(req,network.clone());return network}
     catch(_){return await cache.match(req,{ignoreSearch:true}) || await cache.match("./index.html") || Response.error()}
   }
   const cached=await cache.match(req,{ignoreSearch:true});
   if(cached)return cached;
   try{const network=await fetch(req);if(network.ok)await cache.put(req,network.clone());return network}
   catch(_){return Response.error()}
 })());
});