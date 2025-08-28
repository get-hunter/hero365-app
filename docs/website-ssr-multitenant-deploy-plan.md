## Goal

Enable dynamic, multi-tenant contractor websites with super-low infra cost by deploying the Next.js app on Cloudflare Pages with SSR (Next-on-Pages), while the FastAPI backend serves data (availabilities, products, services, service areas, bookings).

## Architecture Overview

- Frontend: Next.js on Cloudflare Pages with Next-on-Pages (SSR/Edge Functions).
- Backend: FastAPI + Supabase (existing), public endpoints under `/api/v1/public/...` for read data; authenticated endpoints for actions (e.g., bookings).
- Multi-tenancy: One Pages project for all contractors; tenant resolved from `Host` header (wildcard subdomain like `*.hero365.app`) or mapped custom domain.
- Domain mapping: On deploy, call Cloudflare Pages Custom Domains API to attach contractor-owned domains/subdomains.

## Implementation Steps

1) Next-on-Pages SSR setup
- Add dependency and scripts:
  - `npx @cloudflare/next-on-pages@latest` to produce `.vercel/output` compatible bundle.
  - Build script: `"build:ssr": "next build && npx @cloudflare/next-on-pages"`.
  - Deploy script: `"deploy:ssr": "wrangler pages deploy .vercel/output/static --project-name $CF_PAGES_PROJECT"`.
- Update `wrangler.toml` for Pages project; keep `pages_build_output_dir = ".vercel/output/static"` for SSR.
- Re-enable Next.js API routes and server components (remove `output: 'export'`).

2) Tenant resolution (multi-tenant by host)
- Create `website-builder/middleware.ts` (edge) or a small `lib/tenant/resolve-tenant.ts` utility used at the app root to:
  - Read `Host` header, parse subdomain (e.g., `austin-elite.hhero365.app` → `austin-elite`).
  - If custom domain, use full host.
  - Call backend resolver endpoint (see step 3) to get `business_id` + config; store in request context or cookies for the request lifecycle.
  - Fallback to a default business when resolution fails (configurable for previews).

3) Backend: public resolver endpoint for host/subdomain
- Add `GET /api/v1/public/websites/resolve?host=<host>` returning `{ business_id, subdomain, custom_domain, status }`.
- Implement using `SupabaseBusinessWebsiteRepository.get_by_subdomain()` and, when appropriate, `domain` column for custom domains.
- Cache results with short TTL (e.g., 60s) in the backend to minimize DB hits.

4) Domain linking automation
- Extend deployment flow (`publish_website_task`) to (optionally) attach a custom domain:
  - Cloudflare API: `POST /accounts/{account_id}/pages/projects/{project_name}/domains` with `{ name: "contractor-domain.com" }`.
  - Store `website_url` and verification state in `business_websites`.
  - Expose status via `/api/v1/websites/deployments/:id` (already present) and `/api/v1/public/websites/resolve`.

5) CORS and security
- Add the Pages host patterns to CORS allowlist (`*.pages.dev`, `*.hero365.app`, custom domains as they are attached).
- Keep auth flows server → backend via the mobile app; website only uses public endpoints and booking create endpoint (with rate limits + bot protection).

6) Booking + dynamic data
- Frontend calls backend public endpoints directly; for SSR fetches, call from the edge/runtime using server components or API routes as needed (no client-side secrets).
- Keep booking submission via authenticated or public booking endpoint with idempotency.

7) Deploy pipeline
- Build: `npm run build:ssr` in `website-builder`.
- Deploy: `CF_PAGES_PROJECT=hero365-professional wrangler pages deploy .vercel/output/static`.
- After deploy, update `website_url` in Supabase and (optionally) attach custom domain.

8) Multi-tenant wildcard domain (lowest ops)
- Configure DNS: `*.hero365.app` CNAME to the Pages project domain.
- Resolve business from subdomain; gradually allow custom-domain attachments per contractor.

## File/Config Changes (planned)

- `website-builder/package.json`
  - Add `build:ssr` and `deploy:ssr` scripts; keep existing `build` for local dev.
- `website-builder/wrangler.toml`
  - Set `pages_build_output_dir = ".vercel/output/static"`.
- `website-builder/next.config.js`
  - Remove `output: 'export'`; keep standard SSR build.
- `website-builder/middleware.ts`
  - Implement host parsing and set a request-scoped tenant header/cookie.
- `website-builder/lib/tenant/resolve-tenant.ts`
  - Utility to call backend resolver and memoize tenant for the request.
- Backend `backend/app/api/routes/public_websites.py`
  - New resolver route `GET /api/v1/public/websites/resolve`.
- Backend `backend/app/workers/website_tasks.py`
  - Add optional custom-domain attach step via Cloudflare API.

## Environment & Secrets

- Cloudflare: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `CF_PAGES_PROJECT`.
- Backend: Allowlist Pages origins in CORS; set `BACKEND_CORS_ORIGINS` to include `*.pages.dev`, `*.hero365.app`, contractor custom domains.

## Testing Plan

1) Local: run Next with edge runtime locally; verify tenant resolution by simulating `Host` header.
2) Staging Pages project: deploy SSR build, confirm SSR routes and API routes respond; verify public data loads.
3) Resolver: test `/public/websites/resolve?host=` returns correct `business_id` for subdomain/custom domain.
4) Custom domain attach: call Pages API for a test domain; verify DNS + HTTPS status, confirm resolver.
5) Booking flow E2E with idempotency and error handling.

## Rollout

- Phase 1: Wildcard `*.hero365.app` subdomains only, resolver-based multi-tenant.
- Phase 2: Enable custom domains per contractor via backend automation.
- Phase 3: Observability (logs, 4xx/5xx rate, cache hits) and performance tuning at the edge.

## Cost Notes

- Cloudflare Pages + Workers free tier typically suffices initially (SSR/API routes at edge); scale later with low cost.
- No servers for the frontend; only the existing FastAPI backend remains.


