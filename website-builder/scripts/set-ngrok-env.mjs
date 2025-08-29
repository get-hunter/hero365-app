#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import https from 'https';
import http from 'http';

function get(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    const req = client.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    req.on('error', reject);
    req.end();
  });
}

async function main() {
  try {
    // Prefer explicit NGROK_PUBLIC_URL if provided
    let publicUrl = process.env.NGROK_PUBLIC_URL;
    if (!publicUrl) {
      const apiUrl = process.env.NGROK_API_URL || 'http://127.0.0.1:4040/api/tunnels';
      const { status, body } = await get(apiUrl);
      if (status !== 200) throw new Error(`Failed to query ngrok (${status})`);
      const json = JSON.parse(body);
      const tunnels = Array.isArray(json.tunnels) ? json.tunnels : [];
      const httpsTunnel = tunnels.find((t) => t.public_url && t.public_url.startsWith('https://'));
      if (!httpsTunnel) throw new Error('No https ngrok tunnel found. Start ngrok before building.');
      publicUrl = httpsTunnel.public_url;
    }

    const envLines = [
      `NEXT_PUBLIC_API_URL=${publicUrl}`,
      `NEXT_PUBLIC_API_VERSION=${process.env.NEXT_PUBLIC_API_VERSION || 'v1'}`,
    ];

    const envPath = path.resolve(process.cwd(), '.env.local');
    const contents = envLines.join('\n') + '\n';
    fs.writeFileSync(envPath, contents, 'utf8');
    console.log(`Wrote ${envPath} with NEXT_PUBLIC_API_URL=${publicUrl}`);
  } catch (err) {
    console.warn('Skipping ngrok env injection:', err?.message || err);
    // Do not fail the build; keep existing .env.local if present
    process.exit(0);
  }
}

main();


