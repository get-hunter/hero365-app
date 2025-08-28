export const runtime = 'edge';

// Hardcode backend base for reliability on Pages Functions runtime
const BACKEND_BASE = 'https://64ab0c42f974.ngrok-free.app';

function joinUrl(base: string, path: string) {
  return base.replace(/\/$/, '') + '/' + path.replace(/^\//, '');
}

function getSearch(req: Request) {
  const url = new URL(req.url);
  return url.search || '';
}

export async function GET(req: Request, ctx: any) {
  const qs = getSearch(req);
  const segments: string[] = ctx?.params?.path || [];
  const upstream = joinUrl(BACKEND_BASE, `api/v1/public/${segments.join('/')}${qs}`);
  const res = await fetch(upstream, { method: 'GET', headers: { Accept: 'application/json' } });
  return new Response(res.body, { status: res.status, headers: res.headers });
}

export async function POST(req: Request, ctx: any) {
  const body = await req.text();
  const qs = getSearch(req);
  const segments: string[] = ctx?.params?.path || [];
  const upstream = joinUrl(BACKEND_BASE, `api/v1/public/${segments.join('/')}${qs}`);
  const res = await fetch(upstream, {
    method: 'POST',
    headers: {
      'Content-Type': (req.headers as any).get?.('content-type') || 'application/json',
      Accept: 'application/json',
    },
    body,
  });
  return new Response(res.body, { status: res.status, headers: res.headers });
}

export async function PATCH(req: Request, ctx: any) {
  const body = await req.text();
  const qs = getSearch(req);
  const segments: string[] = ctx?.params?.path || [];
  const upstream = joinUrl(BACKEND_BASE, `api/v1/public/${segments.join('/')}${qs}`);
  const res = await fetch(upstream, {
    method: 'PATCH',
    headers: {
      'Content-Type': (req.headers as any).get?.('content-type') || 'application/json',
      Accept: 'application/json',
    },
    body,
  });
  return new Response(res.body, { status: res.status, headers: res.headers });
}

export async function PUT(req: Request, ctx: any) {
  const body = await req.text();
  const qs = getSearch(req);
  const segments: string[] = ctx?.params?.path || [];
  const upstream = joinUrl(BACKEND_BASE, `api/v1/public/${segments.join('/')}${qs}`);
  const res = await fetch(upstream, {
    method: 'PUT',
    headers: {
      'Content-Type': (req.headers as any).get?.('content-type') || 'application/json',
      Accept: 'application/json',
    },
    body,
  });
  return new Response(res.body, { status: res.status, headers: res.headers });
}

export async function DELETE(req: Request, ctx: any) {
  const qs = getSearch(req);
  const segments: string[] = ctx?.params?.path || [];
  const upstream = joinUrl(BACKEND_BASE, `api/v1/public/${segments.join('/')}${qs}`);
  const res = await fetch(upstream, { method: 'DELETE' });
  return new Response(res.body, { status: res.status, headers: res.headers });
}
