import { getBackendUrl, getDefaultHeaders } from '@/lib/shared/config/api-config';
import { getBusinessIdFromHost } from '@/lib/server/host-business-resolver';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function GET() {
  try {
    const resolution = await getBusinessIdFromHost();
    const backendUrl = 'https://5ab8f8ec32f1.ngrok-free.app';
    const profileUrl = `${backendUrl}/api/v1/public/contractors/profile/${resolution.businessId}`;

    let profileStatus: number | null = null;
    let profileOk = false;
    let profileBodySnippet = '';
    try {
      const res = await fetch(profileUrl, { headers: getDefaultHeaders() });
      profileStatus = res.status;
      profileOk = res.ok;
      const text = await res.text();
      profileBodySnippet = text.slice(0, 200);
    } catch (err: any) {
      profileBodySnippet = `fetch_error:${err?.message || 'unknown'}`;
    }

    return Response.json({
      environment: process.env.NEXT_PUBLIC_ENVIRONMENT || 'unknown',
      backendUrl,
      resolution,
      profile: {
        url: profileUrl,
        status: profileStatus,
        ok: profileOk,
        bodySnippet: profileBodySnippet,
      },
    });
  } catch (error: any) {
    return Response.json({ error: error?.message || 'unknown' }, { status: 500 });
  }
}


