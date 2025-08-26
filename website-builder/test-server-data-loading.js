#!/usr/bin/env node

/**
 * Test script to verify server-side data loading
 * This simulates what the Next.js server component does
 */

const businessId = 'a1b2c3d4-e5f6-7890-1234-567890abcdef';
const backendUrl = 'http://127.0.0.1:8000';

async function testServerDataLoading() {
  console.log('🧪 TESTING SERVER-SIDE DATA LOADING');
  console.log('====================================');
  console.log('');
  console.log('Business ID:', businessId);
  console.log('Backend URL:', backendUrl);
  console.log('');

  try {
    console.log('🔄 Loading profile...');
    const profileResponse = await fetch(`${backendUrl}/api/v1/public/professional/profile/${businessId}`, {
      headers: { 'Content-Type': 'application/json' }
    });

    if (profileResponse.ok) {
      const profile = await profileResponse.json();
      console.log('✅ Profile loaded successfully:');
      console.log('  - Business Name:', profile.business_name);
      console.log('  - Trade Type:', profile.trade_type);
      console.log('  - Phone:', profile.phone);
      console.log('  - Service Areas:', profile.service_areas?.join(', '));
    } else {
      console.log('❌ Profile failed:', profileResponse.status, profileResponse.statusText);
    }

    console.log('');
    console.log('🔄 Loading services...');
    const servicesResponse = await fetch(`${backendUrl}/api/v1/public/professional/services/${businessId}`, {
      headers: { 'Content-Type': 'application/json' }
    });

    if (servicesResponse.ok) {
      const services = await servicesResponse.json();
      console.log('✅ Services loaded successfully:');
      console.log('  - Count:', services.length);
      if (services.length > 0) {
        console.log('  - First service:', services[0].name);
      }
    } else {
      console.log('❌ Services failed:', servicesResponse.status, servicesResponse.statusText);
    }

  } catch (error) {
    console.log('❌ Error:', error.message);
  }

  console.log('');
  console.log('If both API calls succeed, the server-side data loading should work!');
}

testServerDataLoading();
