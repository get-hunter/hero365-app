#!/usr/bin/env node

/**
 * Debug script to test the API call that's failing in the browser
 * This will help us understand what URL is being constructed and what error occurs
 */

// Simulate browser environment
global.process = {
  env: {
    NEXT_PUBLIC_API_URL: 'http://localhost:8000',
    NEXT_PUBLIC_BUSINESS_ID: 'a1b2c3d4-e5f6-7890-1234-567890abcdef',
    NEXT_PUBLIC_BUSINESS_NAME: 'Austin Elite HVAC',
    NEXT_PUBLIC_BUSINESS_PHONE: '(512) 555-COOL',
    NEXT_PUBLIC_BUSINESS_EMAIL: 'info@austinelitehvac.com',
    NEXT_PUBLIC_ENVIRONMENT: 'development'
  }
};

// Import the modules (we need to use dynamic import for ES modules)
async function testApiCall() {
  try {
    console.log('🔍 DEBUGGING API CALL');
    console.log('===================');
    console.log('');
    
    // Test 1: Check environment variables
    console.log('✅ Environment Variables:');
    console.log('  NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
    console.log('  NEXT_PUBLIC_BUSINESS_ID:', process.env.NEXT_PUBLIC_BUSINESS_ID);
    console.log('  NEXT_PUBLIC_ENVIRONMENT:', process.env.NEXT_PUBLIC_ENVIRONMENT);
    console.log('');
    
    // Test 2: Import and test API config
    const { buildPublicApiUrl, getApiConfig, getBusinessConfig } = await import('./lib/config/api-config.js');
    
    console.log('✅ API Configuration:');
    const apiConfig = getApiConfig();
    console.log('  Base URL:', apiConfig.baseUrl);
    console.log('  Environment:', apiConfig.environment);
    console.log('');
    
    const businessConfig = getBusinessConfig();
    console.log('✅ Business Configuration:');
    console.log('  Business ID:', businessConfig.defaultBusinessId);
    console.log('  Business Name:', businessConfig.defaultBusinessName);
    console.log('');
    
    // Test 3: Test URL construction
    const businessId = businessConfig.defaultBusinessId;
    const testUrl = buildPublicApiUrl(`professional/profile/${businessId}`);
    console.log('✅ URL Construction:');
    console.log('  Constructed URL:', testUrl);
    console.log('');
    
    // Test 4: Test the actual fetch call
    console.log('✅ Testing Fetch Call:');
    const { ProfessionalApiClient } = await import('./lib/api/professional-client.js');
    const client = new ProfessionalApiClient();
    
    console.log('  Making API call...');
    const profile = await client.getProfessionalProfile(businessId);
    console.log('  ✅ SUCCESS! Business:', profile.business_name);
    
  } catch (error) {
    console.error('❌ ERROR DETAILS:');
    console.error('  Type:', error.constructor.name);
    console.error('  Message:', error.message);
    console.error('  Stack:', error.stack);
    
    // Additional debugging for fetch errors
    if (error.message === 'Failed to fetch') {
      console.error('');
      console.error('🔍 FETCH ERROR ANALYSIS:');
      console.error('  This is typically caused by:');
      console.error('  1. Network connectivity issues');
      console.error('  2. CORS blocking the request');
      console.error('  3. Backend server not running');
      console.error('  4. Incorrect URL construction');
      console.error('');
      console.error('  Let\'s test the backend directly:');
      
      try {
        const response = await fetch('http://localhost:8000/health');
        const health = await response.json();
        console.error('  ✅ Backend health check:', health.status);
      } catch (healthError) {
        console.error('  ❌ Backend health check failed:', healthError.message);
      }
    }
  }
}

testApiCall();
