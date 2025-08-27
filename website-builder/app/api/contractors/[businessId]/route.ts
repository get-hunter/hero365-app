import { NextRequest, NextResponse } from 'next/server';

/**
 * Server-side proxy for contractors profile API
 * This bypasses browser CORS and connectivity issues
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ businessId: string }> }
) {
  try {
    const { businessId } = await params;
    
    // Use the backend API URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    const apiUrl = `${backendUrl}/api/v1/public/contractors/profile/${businessId}`;
    
    console.log('🔧 [SERVER] Fetching from:', apiUrl);
    
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });
    
    if (!response.ok) {
      console.error('❌ [SERVER] Backend API error:', response.status, response.statusText);
      return NextResponse.json(
        { error: 'Failed to fetch contractor profile' },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log('✅ [SERVER] Successfully fetched profile for:', data.business_name);
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ [SERVER] Proxy error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
