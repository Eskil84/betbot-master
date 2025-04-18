const CACHE_NAME = "betbot-cache-v1";
const urlsToCache = [
  "/",
  "/static/manifest.json",
  "/static/icon-192.png",
  "/static/icon-512.png"
];

// Telepítéskor cache-elünk mindent
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Lekérésnél először a cache-t nézzük
self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
