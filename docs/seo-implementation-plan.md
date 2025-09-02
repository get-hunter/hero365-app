# SEO Implementation Plan - Static-First with ISR

## Architecture Decision
- Static-first with ISR and on‑demand revalidation
- Server-render the full body copy, content blocks, and JSON‑LD into the initial HTML
- Use fallback: 'blocking' to scale long-tail pages without heavy full builds

## Target Outcomes
- <200ms TTFB at edge for cached pages; Largest Contentful Paint <2.5s on mobile
- 100% of money pages indexed with unique content
- JSON‑LD coverage for Service, LocalBusiness, FAQ, Offer
- Revalidate changed pages in <10s after publish

## Implementation Plan

### 1) Data Model (Supabase)
- Add/confirm tables:
  - generated_seo_pages(business_id, page_url, html, meta, word_count, last_modified)
  - service_page_contents(business_id, service_slug, location_slug, content_blocks JSONB, schema_blocks JSONB, status)
- Indexes:
  - (business_id, page_url)
  - (business_id, service_slug, location_slug)
- RLS: allow only backend service role to write; public read via API
- Migration: create with supabase migration file; run via MCP tools

### 2) Backend API (FastAPI)
- Pages index:
  - GET /api/v1/seo/pages/{business_id}?include_content=true
  - Returns pages + navigation + content_blocks (typed with Pydantic)
- Page content:
  - GET /api/v1/seo/page-content/{business_id}?page_path=/services/ac-installation
  - Returns merged html + blocks for a single page
- Publish hook:
  - POST /api/v1/seo/revalidate → forwards to website revalidation endpoint (signed)
- Quality gates:
  - Enforce minimum word count, uniqueness, local entities, CTAs before status='published'
- Always run /scripts/generate-client.sh after API changes

### 3) Content Pipeline (LLM)
- LLM orchestrator produces typed blocks:
  - hero, benefits, process_steps, faq, trust, offers
- Persist to service_page_contents as 'draft'; run content_quality_gate; on pass → 'published'
- Save canonical HTML (rendered from blocks) into generated_seo_pages for fast reads
- Trigger on‑demand revalidation for affected page_url(s)

### 4) Website Builder (Next 15 – App Router)
- Server-only page rendering:
  - Load pages via lib/seo-data on the server (include_content=true)
  - Pass contentBlocks to a server component to render; no client hooks for critical content
- Static generation:
  - generateStaticParams: prebuild top N service, location, service×location pages (ranked by traffic/priority)
  - Route config: export const revalidate = 86400; use revalidateTag('seo:page:'+path)
  - Fallback: 'blocking' to cache long-tail pages on first request
- Revalidation endpoint:
  - app/api/revalidate/route.ts with secret; supports path and tag revalidation
- JSON‑LD:
  - Render server-side per page using content blocks; embed via <script type="application/ld+json">
- Sitemaps:
  - app/sitemap.ts dynamic index + segmented sitemaps (services, locations, combos) with lastmod from Supabase
  - Ping search engines on publish/revalidate
- Canonicals/robots:
  - Set canonical to page_url; enforce trailing-slash policy; exclude non-indexable routes in robots.txt
- Internal linking:
  - Server-render related services/locations; ensure crawl depth ≤3

### 5) Performance/CDN
- Cache-Control: public, s-maxage=86400, stale-while-revalidate=604800 for HTML
- Optimize images, fonts, critical CSS; defer non-critical JS
- Edge logging for cache hit ratio; lighthouse CI budget

### 6) Observability and QA
- HTML snapshot tests to assert H1, main copy, JSON‑LD present
- E2E crawl of internal links; broken-link check
- Export revalidation and publish events to logs/metrics; Search Console monitoring

### 7) Ops, Redirects, Resilience
- Redirects table for slug changes; serve 301s from website layer
- Rollback: keep previous published HTML; revalidate to restore
- Rate-limit and auth for revalidate endpoint (shared secret)

### 8) Environment/Config (request to add)
- NEXT_PUBLIC_API_URL
- NEXT_PUBLIC_BUSINESS_ID
- REVALIDATE_SECRET
- BACKEND_REVALIDATE_WEBHOOK_URL

### 9) Rollout Plan
- Phase 1: Server-render blocks, ISR, revalidate endpoint, sitemap
- Phase 2: Quality gates + publish hook + redirect table
- Phase 3: Long-tail coverage (fallback blocking), freshness scheduler (monthly slice)

### 10) Testing Matrix
- Unit: block renderers, schema builders
- Contract: API response types with Pydantic + generated client
- Integration: page HTML snapshot (content + JSON‑LD present)
- E2E: crawl top 200 pages; verify status 200, canonical, structured data, and internal links

### 11) Measurable Acceptance
- CLS < 0.1, LCP < 2.5s on 75th percentile mobile
- 100% JSON‑LD validation on money pages
- 95% cache hit ratio after warmup
- Index coverage > 95% within 14 days of deployment

### 12) Immediate Code Changes
- Make `components/EnhancedSEOPageContent.tsx` a server component; remove hooks; accept `contentBlocks` prop
- In `app/[...slug]/page.tsx`, fetch `contentBlocks` server-side and pass down
- Add `app/api/revalidate/route.ts` with secret
- Update `lib/seo-data.ts` to expose server helpers that fetch API with include_content=true
- Add dynamic `app/sitemap.ts`; wire lastmod from Supabase

### 13) Security
- Validate revalidation secret; audit logs
- Principle of least privilege to Supabase service role
- Input validation via Pydantic everywhere

### 14) Developer Ergonomics
- Scripts:
  - pnpm dev:website (builder)
  - uv run uvicorn backend.app.main:app --reload
  - scripts/generate-openapi.sh then /scripts/generate-client.sh
- Storybook (optional) to preview block variants with fixtures
