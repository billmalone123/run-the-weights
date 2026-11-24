const CACHE = 'monk-mode-v129';

//  Icons are versioned by file name, so a new icon set gets new names here.
var PRECACHE = ['manifest.json', 'assets/brand/rtw-apple-touch-180-v2.png', 'assets/brand/rtw-icon-192-v2.png', 'assets/brand/rtw-icon-512-v2.png', 'assets/brand/rtw-icon-maskable-512-v2.png'];

self.addEventListener('install', function(e) {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(function(c) { return c.addAll(PRECACHE); }).catch(function() {}));
});

self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(keys.filter(function(k) { return k !== CACHE; }).map(function(k) { return caches.delete(k); }));
    }).then(function() {
      return self.clients.matchAll({ type: 'window' });
    }).then(function(clients) {
      clients.forEach(function(client) { client.postMessage({ type: 'RELOAD' }); });
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function(e) {
  if (e.request.method !== 'GET') return;

  // HTML: always network-first so deploys are instant
  if (e.request.headers.get('accept') && e.request.headers.get('accept').includes('text/html')) {
    e.respondWith(
      fetch(e.request).then(function(response) {
        var clone = response.clone();
        caches.open(CACHE).then(function(cache) { cache.put(e.request, clone); });
        return response;
      }).catch(function() {
        return caches.match(e.request);
      })
    );
    return;
  }

  // Everything else: cache-first
  e.respondWith(
    caches.match(e.request).then(function(cached) {
      var fresh = fetch(e.request).then(function(response) {
        if (response && response.status === 200) {
          var clone = response.clone();
          caches.open(CACHE).then(function(cache) { cache.put(e.request, clone); });
        }
        return response;
      }).catch(function() { return cached; });
      return cached || fresh;
    })
  );
});
