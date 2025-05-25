// Service Worker for Frizerie Barbershop App

const CACHE_NAME = 'frizerie-cache-v1';
const OFFLINE_URL = '/offline.html';

// Files to cache for offline use
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/offline.html',
  '/manifest.json',
  '/favicon.ico',
  '/logo192.png',
  '/logo512.png',
  '/static/css/main.chunk.css',
  '/static/js/main.chunk.js',
  '/static/js/vendors.chunk.js',
  '/static/js/bundle.js',
  // Add paths to important images, fonts, etc.
  '/hairstyles/classic-fade.png',
  '/hairstyles/pompadour.png',
  '/hairstyles/buzz-cut.png',
  '/hairstyles/textured-crop.png',
  '/hairstyles/long-layers.png',
];

// URLs that should be fetched from network first, falling back to cache
const NETWORK_FIRST_URLS = [
  '/api/auth/login',
  '/api/bookings',
  '/api/users/me',
];

// Install event - cache assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        // Cache offline page first
        return fetch(OFFLINE_URL)
          .then((response) => {
            return cache.put(OFFLINE_URL, response);
          })
          .then(() => {
            // Cache other assets
            return cache.addAll(ASSETS_TO_CACHE);
          });
      })
      .then(() => {
        // Activate immediately
        return self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.filter((cacheName) => {
          return cacheName !== CACHE_NAME;
        }).map((cacheName) => {
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});

// Fetch event - handle offline fetching strategy
self.addEventListener('fetch', (event) => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // For API requests, try network first, then fall back to cache
  if (NETWORK_FIRST_URLS.some(url => event.request.url.includes(url))) {
    event.respondWith(networkFirstStrategy(event.request));
    return;
  }

  // For navigation requests, use network first strategy
  if (event.request.mode === 'navigate') {
    event.respondWith(networkFirstStrategy(event.request));
    return;
  }

  // For other requests, use cache first strategy
  event.respondWith(cacheFirstStrategy(event.request));
});

// Cache-first strategy - try cache, fallback to network and update cache
function cacheFirstStrategy(request) {
  return caches.match(request)
    .then((cachedResponse) => {
      if (cachedResponse) {
        // Return cached response immediately
        // Fetch in the background to update cache
        fetchAndUpdateCache(request);
        return cachedResponse;
      }

      // If not in cache, fetch from network
      return fetchAndUpdateCache(request);
    })
    .catch(() => {
      // If both cache and network fail, show offline page for navigation
      if (request.mode === 'navigate') {
        return caches.match(OFFLINE_URL);
      }
      
      // For other resources, return a fallback if available
      return fallbackResponse(request);
    });
}

// Network-first strategy - try network, fallback to cache
function networkFirstStrategy(request) {
  return fetchAndUpdateCache(request)
    .catch(() => {
      return caches.match(request)
        .then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          
          // For navigation, show offline page
          if (request.mode === 'navigate') {
            return caches.match(OFFLINE_URL);
          }
          
          // For other resources, return a fallback if available
          return fallbackResponse(request);
        });
    });
}

// Helper function to fetch and update cache
function fetchAndUpdateCache(request) {
  return fetch(request)
    .then((response) => {
      // Check if valid response
      if (!response || response.status !== 200 || response.type !== 'basic') {
        return response;
      }

      // Clone the response as it can only be consumed once
      const responseToCache = response.clone();

      caches.open(CACHE_NAME)
        .then((cache) => {
          cache.put(request, responseToCache);
        });

      return response;
    });
}

// Helper function to return fallback responses
function fallbackResponse(request) {
  // For images, return a placeholder image
  if (request.url.match(/\.(jpg|jpeg|png|gif|svg)$/)) {
    return caches.match('/images/fallback-image.png');
  }
  
  // For fonts, try to return any cached font
  if (request.url.match(/\.(woff|woff2|ttf|eot)$/)) {
    return caches.match('/fonts/fallback-font.woff2');
  }
  
  // Default - return nothing
  return Promise.reject('No fallback available');
}

// Background sync for offline data
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-bookings') {
    event.waitUntil(syncBookings());
  }
  
  if (event.tag === 'sync-profile') {
    event.waitUntil(syncProfile());
  }
});

// Sync pending bookings when online
function syncBookings() {
  return getDataFromIndexedDB('pending-bookings')
    .then((bookings) => {
      return Promise.all(
        bookings.map((booking) => {
          return fetch('/api/bookings', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${booking.token}`
            },
            body: JSON.stringify(booking.data)
          })
          .then((response) => {
            if (response.ok) {
              // If sync successful, remove from pending
              return removeFromIndexedDB('pending-bookings', booking.id);
            }
          })
          .catch((error) => {
            console.error('Error syncing booking:', error);
          });
        })
      );
    });
}

// Sync profile changes when online
function syncProfile() {
  return getDataFromIndexedDB('pending-profile-updates')
    .then((updates) => {
      return Promise.all(
        updates.map((update) => {
          return fetch('/api/users/me', {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${update.token}`
            },
            body: JSON.stringify(update.data)
          })
          .then((response) => {
            if (response.ok) {
              // If sync successful, remove from pending
              return removeFromIndexedDB('pending-profile-updates', update.id);
            }
          })
          .catch((error) => {
            console.error('Error syncing profile:', error);
          });
        })
      );
    });
}

// Helper functions for IndexedDB operations
function getDataFromIndexedDB(storeName) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('frizerie-offline-db', 1);
    
    request.onerror = (event) => {
      reject('Error opening IndexedDB');
    };
    
    request.onsuccess = (event) => {
      const db = event.target.result;
      const transaction = db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const getAll = store.getAll();
      
      getAll.onsuccess = () => {
        resolve(getAll.result);
      };
      
      getAll.onerror = () => {
        reject('Error getting data from IndexedDB');
      };
    };
  });
}

function removeFromIndexedDB(storeName, id) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('frizerie-offline-db', 1);
    
    request.onerror = (event) => {
      reject('Error opening IndexedDB');
    };
    
    request.onsuccess = (event) => {
      const db = event.target.result;
      const transaction = db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const deleteRequest = store.delete(id);
      
      deleteRequest.onsuccess = () => {
        resolve();
      };
      
      deleteRequest.onerror = () => {
        reject('Error removing data from IndexedDB');
      };
    };
  });
} 