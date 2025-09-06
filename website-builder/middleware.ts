import { NextRequest, NextResponse } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // Handle /services/{city}/{service} -> /services/{service}/{city} redirects
  if (pathname.startsWith('/services/')) {
    const pathParts = pathname.split('/').filter(Boolean)
    
    // Check if it's a 3-part path: services/{segment1}/{segment2}
    if (pathParts.length === 3 && pathParts[0] === 'services') {
      const segment1 = pathParts[1]
      const segment2 = pathParts[2]
      
      // Define known city patterns (this should ideally come from your business data)
      const cityPatterns = [
        'austin', 'austin-tx', 'round-rock', 'round-rock-tx', 'cedar-park', 'cedar-park-tx',
        'georgetown', 'georgetown-tx', 'pflugerville', 'pflugerville-tx', 'leander', 'leander-tx'
      ]
      
      // Define known service patterns
      const servicePatterns = [
        'ac-installation', 'hvac-repair', 'heating-installation', 'cooling-repair',
        'ac-repair', 'hvac-installation', 'heating-repair', 'cooling-installation',
        'ductless-installation', 'ductless-repair', 'air-quality', 'maintenance'
      ]
      
      // Check if segment1 is a city and segment2 is a service
      if (cityPatterns.includes(segment1) && servicePatterns.includes(segment2)) {
        // Redirect to canonical format: /services/{service}/{city}
        const canonicalUrl = `/services/${segment2}/${segment1}`
        return NextResponse.redirect(new URL(canonicalUrl, request.url), 301)
      }
    }
  }
  
  // Create response with cache-control headers to prevent stale HTML caching
  const response = NextResponse.next()
  
  // Add cache-busting headers for HTML pages (not static assets)
  if (!pathname.startsWith('/_next/') && 
      !pathname.startsWith('/api/') && 
      !pathname.includes('.') && // Skip files with extensions
      request.headers.get('accept')?.includes('text/html')) {
    response.headers.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate')
    response.headers.set('Pragma', 'no-cache')
    response.headers.set('Expires', '0')
    response.headers.set('Surrogate-Control', 'no-store')
    response.headers.set('X-Build-Time', Date.now().toString())
  }
  
  return response
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
