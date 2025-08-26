#!/usr/bin/env node

/**
 * Verification script to check what business data should be displayed
 */

const businessId = 'a1b2c3d4-e5f6-7890-1234-567890abcdef';

async function verifyBusinessData() {
  console.log('🔍 BUSINESS DATA VERIFICATION');
  console.log('============================');
  console.log('');

  try {
    const response = await fetch(`http://127.0.0.1:8000/api/v1/public/professional/profile/${businessId}`);
    
    if (!response.ok) {
      console.log('❌ API Error:', response.status, response.statusText);
      return;
    }

    const profile = await response.json();
    
    console.log('✅ REAL BUSINESS DATA FROM API:');
    console.log('  Business Name:', profile.business_name);
    console.log('  Phone:', profile.phone);
    console.log('  Trade Type:', profile.trade_type);
    console.log('  Description:', profile.description);
    console.log('  Service Areas:', profile.service_areas?.join(', '));
    console.log('  Emergency Service:', profile.emergency_service);
    console.log('');
    
    console.log('🎯 WHAT YOU SHOULD SEE ON THE WEBSITE:');
    console.log('  Header: "Austin Elite HVAC" (business name)');
    console.log('  Phone: "(888) 343-7969" ✅ Already showing!');
    console.log('  Hero: "Professional hvac Services" (tagline)');
    console.log('  Location: "Austin" (first service area)');
    console.log('  Emergency: Available (if true)');
    
  } catch (error) {
    console.log('❌ Error:', error.message);
  }
}

verifyBusinessData();
