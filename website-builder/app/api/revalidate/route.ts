import { NextRequest, NextResponse } from 'next/server';
import { revalidateTag } from 'next/cache';

// Note: Using Node.js runtime for OpenNext compatibility
// Edge runtime API routes need to be defined separately for OpenNext

/**
 * On-demand ISR revalidation endpoint
 * 
 * Usage: POST /api/revalidate
 * Body: { secret: "your-secret", tags: ["projects", "profile"], businessId: "..." }
 * 
 * This allows your backend/Supabase to trigger cache invalidation
 * when content is updated, ensuring fresh data within seconds.
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { secret, tags, businessId } = body;

    // Verify secret to prevent unauthorized revalidation
    if (secret !== process.env.REVALIDATION_SECRET) {
      return NextResponse.json({ message: 'Invalid secret' }, { status: 401 });
    }

    if (!tags || !Array.isArray(tags)) {
      return NextResponse.json({ message: 'Tags array required' }, { status: 400 });
    }

    // Revalidate specified tags
    for (const tag of tags) {
      revalidateTag(tag);
      if (businessId) {
        revalidateTag(`${tag}-${businessId}`);
      }
    }

    console.log(`✅ [REVALIDATION] Revalidated tags:`, tags, businessId ? `for business ${businessId}` : '');

    return NextResponse.json({ 
      message: 'Revalidated successfully', 
      tags,
      businessId,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ [REVALIDATION] Error:', error);
    return NextResponse.json(
      { message: 'Internal server error' }, 
      { status: 500 }
    );
  }
}

// Health check endpoint
export async function GET() {
  return NextResponse.json({ 
    message: 'Revalidation endpoint is healthy',
    timestamp: new Date().toISOString()
  });
}
