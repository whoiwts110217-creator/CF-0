// CF Skill Foundry — local-only offline cache. CacheStorage is ORIGIN-wide,
// so never delete or read caches belonging to Mission Control or other CF-0 apps.
const PREFIX = 'cf-skill-foundry-';
const VERSION = PREFIX + 'v0.2.5';
const FILES = ['./', './index.html', './manifest.webmanifest', './icon.svg', './apple-touch-icon.png'];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(VERSION).then(cache => cache.addAll(FILES)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(key => key.startsWith(PREFIX) && key !== VERSION)
          .map(key => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET' || new URL(request.url).origin !== self.location.origin) return;
  // Consult ONLY this Foundry cache, not all same-origin PWA caches.
  event.respondWith(
    caches.open(VERSION).then(cache =>
      cache.match(request).then(cached => {
        if (cached) return cached;
        return fetch(request).then(response => {
          if (response.ok) event.waitUntil(cache.put(request, response.clone()));
          return response;
        });
      })
    )
  );
});
