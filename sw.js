/**
 * Service Worker para PWA
 * Proporciona: offline support, caching, sync, push notifications
 */

const CACHE_NAME = 'udemedellin-v2.0';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/styles.css',
  '/chat.css',
  '/sections.css',
  '/login.css',
  '/admin.css',
  '/advisor.css',
  '/app.jsx',
  '/chat.jsx',
  '/icons.jsx',
  '/AdvisorRequestIntegrado.jsx',
  '/Asistente Virtual UdeMedellin.html'
];

const API_CACHE = 'api-cache-v1';
const IMAGE_CACHE = 'image-cache-v1';

// Installation - cache estático
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker installing...');

  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('📦 Caching static assets');
      return cache.addAll(STATIC_ASSETS);
    })
  );

  self.skipWaiting();
});

// Activation - limpiar cachés viejos
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker activating...');

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== API_CACHE && cacheName !== IMAGE_CACHE) {
            console.log('🗑️ Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );

  self.clients.claim();
});

// Fetch - estrategia cache-first para estáticos, network-first para API
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // API requests - network first, fallback cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.status === 200) {
            const cache = caches.open(API_CACHE);
            cache.then((c) => c.put(request, response.clone()));
          }
          return response;
        })
        .catch(() => {
          return caches.match(request)
            .then((cached) => cached || cacheResponse('offline'));
        })
    );
    return;
  }

  // Images - cache first
  if (request.destination === 'image') {
    event.respondWith(
      caches.match(request).then((cached) => {
        return cached || fetch(request).then((response) => {
          caches.open(IMAGE_CACHE).then((cache) => {
            cache.put(request, response.clone());
          });
          return response;
        }).catch(() => {
          return cacheResponse('offline-image');
        });
      })
    );
    return;
  }

  // Static assets - cache first
  event.respondWith(
    caches.match(request).then((cached) => {
      return cached || fetch(request).then((response) => {
        if (response.status === 200) {
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, response.clone());
          });
        }
        return response;
      }).catch(() => {
        return cacheResponse('offline');
      });
    })
  );
});

// Background Sync - sincronizar datos cuando vuelve conexión
self.addEventListener('sync', (event) => {
  console.log('🔄 Background sync:', event.tag);

  if (event.tag === 'sync-messages') {
    event.waitUntil(syncMessages());
  }

  if (event.tag === 'sync-requests') {
    event.waitUntil(syncRequests());
  }
});

async function syncMessages() {
  try {
    const db = await openIndexDB();
    const messages = await db.getAll('pending_messages');

    for (const msg of messages) {
      const response = await fetch(`/api/advisor/message/${msg.request_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg.text })
      });

      if (response.ok) {
        await db.delete('pending_messages', msg.id);
      }
    }

    console.log('✅ Messages synced');
  } catch (error) {
    console.error('❌ Sync error:', error);
  }
}

async function syncRequests() {
  try {
    const db = await openIndexDB();
    const requests = await db.getAll('pending_requests');

    for (const req of requests) {
      const response = await fetch('/api/advisor/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req)
      });

      if (response.ok) {
        await db.delete('pending_requests', req.id);
      }
    }

    console.log('✅ Requests synced');
  } catch (error) {
    console.error('❌ Sync error:', error);
  }
}

// Push Notifications
self.addEventListener('push', (event) => {
  if (!event.data) return;

  const data = event.data.json();

  const options = {
    body: data.body,
    icon: '/icon-192.png',
    badge: '/badge-72.png',
    tag: data.tag,
    requireInteraction: data.type === 'important',
    actions: [
      { action: 'open', title: '✅ Abrir' },
      { action: 'close', title: '❌ Cerrar' }
    ],
    data: {
      url: data.data?.url || '/',
      request_id: data.data?.request_id
    }
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'close') return;

  const urlToOpen = event.notification.data.url || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // Si ya existe ventana abierta, enfocarla
      for (let i = 0; i < clientList.length; i++) {
        const client = clientList[i];
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus();
        }
      }
      // Si no existe, crear nueva ventana
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

// IndexDB para offline storage
function openIndexDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('UdeMedellin', 1);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(new DBWrapper(request.result));

    request.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains('pending_messages')) {
        db.createObjectStore('pending_messages', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('pending_requests')) {
        db.createObjectStore('pending_requests', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('notifications')) {
        db.createObjectStore('notifications', { keyPath: 'id' });
      }
    };
  });
}

class DBWrapper {
  constructor(db) {
    this.db = db;
  }

  async getAll(store) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(store, 'readonly');
      const request = transaction.objectStore(store).getAll();
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async delete(store, key) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(store, 'readwrite');
      const request = transaction.objectStore(store).delete(key);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  async put(store, value) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(store, 'readwrite');
      const request = transaction.objectStore(store).put(value);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }
}

// Helpers
function cacheResponse(type) {
  if (type === 'offline') {
    return new Response('<h1>📡 Offline</h1><p>La conexión se perdió. Recargando cuando vuelva...</p>', {
      headers: { 'Content-Type': 'text/html' }
    });
  }
  if (type === 'offline-image') {
    return new Response('', { status: 404 });
  }
}

console.log('🚀 Service Worker loaded');
