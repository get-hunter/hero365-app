export const dynamic = 'force-dynamic';

export async function GET() {
  return new Response(JSON.stringify({ status: 'ok', ts: Date.now() }), {
    headers: { 'Content-Type': 'application/json' },
    status: 200,
  });
}


