// Offline shell only. No periodic/background automation, push, or cross-account interception.
const CACHE="cf0-habit-automator-v1";
const ASSETS=["./","./index.html","./app.mjs","./core.mjs","./icon.svg","./icon-180.png","./manifest.webmanifest"];
self.addEventListener("install",event=>{
  event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)).then(()=>self.skipWaiting()));
});
self.addEventListener("activate",event=>{
  event.waitUntil(caches.keys().then(names=>Promise.all(names.filter(n=>n.startsWith("cf0-habit-automator-")&&n!==CACHE).map(n=>caches.delete(n)))).then(()=>self.clients.claim()));
});
self.addEventListener("fetch",event=>{
  const request=event.request;
  if(request.method!=="GET")return;
  const target=new URL(request.url);
  const scope=new URL(self.registration.scope);
  if(target.origin!==scope.origin || !target.pathname.startsWith(scope.pathname))return;
  event.respondWith(fetch(request).then(response=>{
    if(response.ok){const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(request,copy)).catch(()=>{});}
    return response;
  }).catch(()=>caches.match(request)));
});
