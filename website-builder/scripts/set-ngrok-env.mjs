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

    const envPath = path.resolve(process.cwd(), '.env.local');
    
    // Read existing .env.local if it exists
    let existingEnv = {};
    if (fs.existsSync(envPath)) {
      const existingContent = fs.readFileSync(envPath, 'utf8');
      existingContent.split('\n').forEach(line => {
        const trimmed = line.trim();
        if (trimmed && !trimmed.startsWith('#')) {
          const [key, ...valueParts] = trimmed.split('=');
          if (key && valueParts.length > 0) {
            existingEnv[key.trim()] = valueParts.join('=').trim();
          }
        }
      });
    }
    
    // Update only the API URL, preserve other variables
    existingEnv['NEXT_PUBLIC_API_URL'] = publicUrl;
    existingEnv['NEXT_PUBLIC_API_VERSION'] = process.env.NEXT_PUBLIC_API_VERSION || 'v1';
    
    // Write back all environment variables
    const allEnvLines = Object.entries(existingEnv).map(([key, value]) => `${key}=${value}`);
    const contents = allEnvLines.join('\n') + '\n';
    
    fs.writeFileSync(envPath, contents, 'utf8');
    console.log(`Updated ${envPath} with NEXT_PUBLIC_API_URL=${publicUrl}, preserved ${Object.keys(existingEnv).length - 2} existing variables`);
  } catch (err) {
    console.warn('Skipping ngrok env injection:', err?.message || err);
    // Do not fail the build; keep existing .env.local if present
    process.exit(0);
  }
}

main();


