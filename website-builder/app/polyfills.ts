'use client'

// Safe polyfills for server/edge build phases where self may be undefined
// Next.js vendor bundles may reference `self` when targeting edge runtimes.
// Ensure `self` exists by aliasing to globalThis if missing.
// This file is imported early in the app to avoid build-time SSR errors.

declare global {
  // eslint-disable-next-line no-var
  var self: any | undefined;
}

if (typeof globalThis !== 'undefined' && typeof (globalThis as any).self === 'undefined') {
  (globalThis as any).self = globalThis as any;
}

export {}


