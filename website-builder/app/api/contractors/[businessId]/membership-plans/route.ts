import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ businessId: string }> }
) {
  try {
    const resolvedParams = await params;
    const { businessId } = resolvedParams;
    
    console.log('🔄 [MEMBERSHIP PLANS] Loading plans for business:', businessId);
    
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    const response = await fetch(
      `${backendUrl}/api/v1/public/contractors/membership-plans/${businessId}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        next: { revalidate: 300 } // Cache for 5 minutes
      }
    );
    
    if (!response.ok) {
      console.error('❌ [MEMBERSHIP PLANS] Backend error:', response.status, response.statusText);
      return NextResponse.json([], { status: 200 }); // Return empty array on error
    }
    
    const plans = await response.json();
    console.log('✅ [MEMBERSHIP PLANS] Loaded:', plans.length, 'plans');
    
    return NextResponse.json(plans);
  } catch (error) {
    console.error('❌ [MEMBERSHIP PLANS] Error:', error);
    return NextResponse.json([], { status: 200 }); // Return empty array on error
  }
}
