import { defineCloudflareConfig } from "@opennextjs/cloudflare";

export default defineCloudflareConfig({
  // Optimize caching for better performance
  cache: {
    // HTML caching with SWR semantics
    html: {
      bypassQueryParams: ["preview", "debug"],
      defaultSWR: 60, // 1 minute stale-while-revalidate
    },
    // Static assets caching
    assets: {
      edgeTTL: 31536000, // 1 year for static assets
    },
  },
  
  // Configure for multi-tenant architecture
  // Host header resolution will be handled in the app
  experimental: {
    // Enable any experimental features as needed
  },
});
