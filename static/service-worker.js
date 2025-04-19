self.addEventListener('install', function (event) {
  console.log('[Service Worker] Telepítve');
  self.skipWaiting();
});

self.addEventListener('activate', function (event) {
  console.log('[Service Worker] Aktiválva');
});

self.addEventListener('fetch', function (event) {
  // Jövőbeli offline kezeléshez
});
