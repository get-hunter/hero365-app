import { NextRequest, NextResponse } from 'next/server'
import { revalidatePath, revalidateTag } from 'next/cache'

export async function POST(request: NextRequest) {
  try {
    // Verify secret
    const secret = request.nextUrl.searchParams.get('secret')
    if (secret !== process.env.REVALIDATE_SECRET) {
      return NextResponse.json({ message: 'Invalid secret' }, { status: 401 })
    }

    const body = await request.json()
    const { path, tag, type = 'path' } = body

    if (type === 'tag' && tag) {
      // Revalidate by tag
      revalidateTag(tag)
      console.log(`✅ Revalidated tag: ${tag}`)
      
      return NextResponse.json({ 
        revalidated: true, 
        type: 'tag',
        tag,
        now: Date.now() 
      })
    } else if (type === 'path' && path) {
      // Revalidate by path
      revalidatePath(path)
      console.log(`✅ Revalidated path: ${path}`)
      
      return NextResponse.json({ 
        revalidated: true, 
        type: 'path',
        path,
        now: Date.now() 
      })
    } else {
      return NextResponse.json(
        { message: 'Missing path or tag parameter' }, 
        { status: 400 }
      )
    }
  } catch (err) {
    console.error('❌ Revalidation error:', err)
    return NextResponse.json(
      { message: 'Error revalidating', error: err.message }, 
      { status: 500 }
    )
  }
}

// Health check endpoint
export async function GET() {
  return NextResponse.json({ 
    status: 'ok', 
    service: 'revalidation-api',
    timestamp: new Date().toISOString()
  })
}