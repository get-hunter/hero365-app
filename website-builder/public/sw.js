/**
 * Service Worker for Performance and Offline Support
 * 
 * Implements caching strategies for better performance and
 * basic offline functionality for contractor websites.
 */

const IS_LOCALHOST = self.location.hostname === 'localhost' || self.location.hostname === '127.0.0.1';
const CACHE_NAME = 'hero365-contractor-v1';
const STATIC_CACHE = 'hero365-static-v1';
const DYNAMIC_CACHE = 'hero365-dynamic-v1';

// Resources to cache immediately
const STATIC_ASSETS = [
  '/',
  '/about',
  '/services',
  '/contact',
  '/offline',
  '/manifest.json',
  // Add critical CSS and JS files
  '/_next/static/css/',
  '/_next/static/chunks/',
];

// API endpoints to cache with network-first strategy
const API_ENDPOINTS = [
  '/api/contractors/profile',
  '/api/contractors/services',
  '/api/contractors/products',
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  if (IS_LOCALHOST) {
    // In dev, skip caching to avoid stale chunks
    event.waitUntil(self.skipWaiting());
    return;
  }

  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('Service Worker: Installed successfully');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker: Installation failed', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  if (IS_LOCALHOST) {
    // In dev, clear all caches aggressively and claim clients
    event.waitUntil(
      caches.keys().then((names) => Promise.all(names.map((n) => caches.delete(n)))).then(() => self.clients.claim())
    );
    return;
  }

  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activated successfully');
        return self.clients.claim();
      })
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip chrome-extension and other non-http requests
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // In dev, bypass SW for all requests to avoid chunk staleness
  if (IS_LOCALHOST) {
    return; // Let the network handle it
  }
  
  // Handle different types of requests with appropriate strategies
  if (isStaticAsset(request)) {
    // Cache-first strategy for static assets
    event.respondWith(cacheFirstStrategy(request, STATIC_CACHE));
  } else if (isAPIRequest(request)) {
    // Network-first strategy for API requests
    event.respondWith(networkFirstStrategy(request, DYNAMIC_CACHE));
  } else if (isPageRequest(request)) {
    // Stale-while-revalidate for pages
    event.respondWith(staleWhileRevalidateStrategy(request, DYNAMIC_CACHE));
  } else {
    // Network-only for everything else
    event.respondWith(fetch(request));
  }
});

/**
 * Cache-first strategy: Check cache first, fallback to network
 */
async function cacheFirstStrategy(request, cacheName) {
  try {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      console.log('Service Worker: Serving from cache', request.url);
      return cachedResponse;
    }
    
    console.log('Service Worker: Fetching from network', request.url);
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('Service Worker: Cache-first strategy failed', error);
    return new Response('Offline', { status: 503 });
  }
}

/**
 * Network-first strategy: Try network first, fallback to cache
 */
async function networkFirstStrategy(request, cacheName) {
  try {
    console.log('Service Worker: Trying network first', request.url);
    const networkResponse = await fetch(request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Network failed, trying cache', request.url);
    
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline response for API requests
    return new Response(JSON.stringify({
      error: 'Offline',
      message: 'This content is not available offline'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * Stale-while-revalidate: Serve from cache, update in background
 */
async function staleWhileRevalidateStrategy(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  // Fetch from network in background
  const networkResponsePromise = fetch(request)
    .then((networkResponse) => {
      if (networkResponse.ok) {
        cache.put(request, networkResponse.clone());
      }
      return networkResponse;
    })
    .catch(() => null);
  
  // Return cached response immediately if available
  if (cachedResponse) {
    console.log('Service Worker: Serving stale content', request.url);
    return cachedResponse;
  }
  
  // Otherwise wait for network response
  console.log('Service Worker: Waiting for network', request.url);
  const networkResponse = await networkResponsePromise;
  
  if (networkResponse) {
    return networkResponse;
  }
  
  // Fallback to offline page
  return caches.match('/offline');
}

/**
 * Check if request is for a static asset
 */
function isStaticAsset(request) {
  const url = new URL(request.url);
  return (
    // Exclude Next.js build chunks from SW caching to prevent stale code
    (url.pathname.startsWith('/_next/static/') && false) ||
    url.pathname.startsWith('/static/') ||
    url.pathname.endsWith('.css') ||
    url.pathname.endsWith('.js') ||
    url.pathname.endsWith('.png') ||
    url.pathname.endsWith('.jpg') ||
    url.pathname.endsWith('.jpeg') ||
    url.pathname.endsWith('.webp') ||
    url.pathname.endsWith('.svg') ||
    url.pathname.endsWith('.ico')
  );
}

/**
 * Check if request is for an API endpoint
 */
function isAPIRequest(request) {
  const url = new URL(request.url);
  return url.pathname.startsWith('/api/');
}

/**
 * Check if request is for a page
 */
function isPageRequest(request) {
  const url = new URL(request.url);
  return (
    request.headers.get('accept')?.includes('text/html') &&
    !url.pathname.startsWith('/api/') &&
    !isStaticAsset(request)
  );
}

// Handle background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    console.log('Service Worker: Background sync triggered');
    event.waitUntil(handleBackgroundSync());
  }
});

/**
 * Handle background sync for offline actions
 */
async function handleBackgroundSync() {
  // Handle any queued offline actions
  // This could include form submissions, contact requests, etc.
  console.log('Service Worker: Processing background sync');
}

// Handle push notifications (if needed)
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    console.log('Service Worker: Push notification received', data);
    
    event.waitUntil(
      self.registration.showNotification(data.title, {
        body: data.body,
        icon: '/icon-192x192.png',
        badge: '/badge-72x72.png',
        tag: 'hero365-notification',
        requireInteraction: false,
        actions: [
          {
            action: 'view',
            title: 'View Details'
          }
        ]
      })
    );
  }
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification clicked', event);
  
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});
