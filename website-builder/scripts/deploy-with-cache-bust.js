#!/usr/bin/env node

/**
 * Deploy with Cache Busting - Ensures Cloudflare always serves latest version
 * Usage: node scripts/deploy-with-cache-bust.js [staging|production]
 */

const { execSync } = require('child_process');
const https = require('https');

const ENVIRONMENT = process.argv[2] || 'staging';
const ZONE_ID = 'c28e66bcb1f56af2ac253ae47bf341f4';

function exec(command, options = {}) {
  console.log(`> ${command}`);
  return execSync(command, { 
    stdio: 'inherit', 
    encoding: 'utf8',
    ...options 
  });
}

function execSilent(command) {
  return execSync(command, { encoding: 'utf8' }).trim();
}

async function purgeCloudflareCache() {
  const token = process.env.CLOUDFLARE_API_TOKEN;
  
  if (!token) {
    console.log('⚠️  CLOUDFLARE_API_TOKEN not set. Skipping cache purge.');
    console.log('   To enable automatic cache purging, set CLOUDFLARE_API_TOKEN environment variable.');
    console.log('   You can manually purge cache at: https://dash.cloudflare.com');
    return;
  }

  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ purge_everything: true });
    
    const options = {
      hostname: 'api.cloudflare.com',
      port: 443,
      path: `/client/v4/zones/${ZONE_ID}/purge_cache`,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };

    const req = https.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        try {
          const response = JSON.parse(responseData);
          if (response.success) {
            console.log('✅ Cache purged successfully');
            resolve(response);
          } else {
            console.error('❌ Cache purge failed:', response.errors);
            reject(new Error('Cache purge failed'));
          }
        } catch (error) {
          console.error('❌ Failed to parse cache purge response:', error);
          reject(error);
        }
      });
    });

    req.on('error', (error) => {
      console.error('❌ Cache purge request failed:', error);
      reject(error);
    });

    req.write(data);
    req.end();
  });
}

async function testDeployment() {
  const testUrl = ENVIRONMENT === 'staging' 
    ? 'https://elite-hvac-austin.tradesites.app'
    : 'https://hero365contractors.com';

  console.log(`🧪 Testing deployment at ${testUrl}...`);
  
  try {
    const response = execSilent(`curl -s -o /dev/null -w "%{http_code}" "${testUrl}"`);
    
    if (response === '200') {
      console.log(`✅ Deployment successful! Site is responding with HTTP ${response}`);
      
      // Test backend connectivity for staging
      if (ENVIRONMENT === 'staging') {
        console.log('🔍 Testing backend connectivity...');
        try {
          const debugResponse = execSilent(`curl -s "${testUrl}/api/debug/home"`);
          const debugData = JSON.parse(debugResponse);
          console.log(`   Backend URL: ${debugData.backendUrl}`);
          console.log(`   Profile OK: ${debugData.profileOk}`);
        } catch (error) {
          console.log('   Debug endpoint not available or failed');
        }
      }
      
      return true;
    } else {
      console.log(`❌ Deployment may have issues. Site responding with HTTP ${response}`);
      return false;
    }
  } catch (error) {
    console.error('❌ Failed to test deployment:', error.message);
    return false;
  }
}

async function main() {
  try {
    console.log(`🚀 Starting deployment to ${ENVIRONMENT} with cache busting...`);

    // Step 1: Build the application
    console.log('📦 Building application...');
    exec('npm run build');
    exec('npx opennextjs-cloudflare build');

    // Step 2: Deploy to Cloudflare Workers
    console.log('🌐 Deploying to Cloudflare Workers...');
    exec(`npx wrangler deploy --env ${ENVIRONMENT}`);

    // Step 3: Get the latest worker version
    console.log('🔍 Getting latest worker version...');
    const versionsOutput = execSilent(`npx wrangler versions list --env ${ENVIRONMENT} --json`);
    const versions = JSON.parse(versionsOutput);
    const latestVersion = versions[0]?.id;
    
    if (!latestVersion) {
      throw new Error('Failed to get latest worker version');
    }
    
    console.log(`Latest version: ${latestVersion}`);

    // Step 4: Deploy 100% traffic to the latest version
    console.log('📌 Deploying 100% traffic to latest version...');
    exec(`npx wrangler versions deploy ${latestVersion}@100 --env ${ENVIRONMENT} --yes`);

    // Step 5: Verify deployment
    console.log('✅ Verifying version deployment...');
    exec(`npx wrangler versions list --env ${ENVIRONMENT}`);

    // Step 6: Purge Cloudflare cache
    console.log('🧹 Purging Cloudflare cache...');
    await purgeCloudflareCache();

    // Step 7: Wait for propagation
    console.log('⏳ Waiting for propagation...');
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Step 8: Test the deployment
    const testPassed = await testDeployment();

    console.log('');
    console.log('🎉 Deployment complete!');
    console.log(`   Environment: ${ENVIRONMENT}`);
    console.log(`   Worker Version: ${latestVersion}`);
    console.log(`   URL: ${ENVIRONMENT === 'staging' ? 'https://elite-hvac-austin.tradesites.app' : 'https://hero365contractors.com'}`);
    console.log('');
    console.log('💡 Tips to avoid stale deployments:');
    console.log('   - Always use this script instead of "wrangler deploy" directly');
    console.log('   - Set CLOUDFLARE_API_TOKEN for automatic cache purging');
    console.log(`   - Check worker versions with: npx wrangler versions list --env ${ENVIRONMENT}`);

    if (!testPassed) {
      process.exit(1);
    }

  } catch (error) {
    console.error('❌ Deployment failed:', error.message);
    process.exit(1);
  }
}

main();
