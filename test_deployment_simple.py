#!/usr/bin/env python3
"""
Simple Mobile Deployment Test

A basic test script to verify the mobile deployment endpoints are working.
This script can be used to test the API structure without full authentication.
"""

import json
import uuid
import requests
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

# Mock test data
TEST_DATA = {
    "subdomain": f"test-{uuid.uuid4().hex[:8]}",
    "service_areas": [
        {
            "postal_code": "78701",
            "country_code": "US",
            "city": "Austin",
            "region": "TX",
            "emergency_services_available": True,
            "regular_services_available": True
        }
    ],
    "services": [
        {
            "name": "HVAC Repair",
            "description": "Professional HVAC repair services",
            "pricing_model": "hourly",
            "unit_price": 125.0,
            "estimated_duration_hours": 2.0,
            "is_emergency": True,
            "is_featured": True
        }
    ],
    "products": [
        {
            "name": "Air Filter",
            "sku": "AF-001",
            "description": "High-efficiency air filter",
            "unit_price": 25.99,
            "is_featured": True
        }
    ],
    "locations": [
        {
            "name": "Main Office",
            "address": "123 Main St",
            "city": "Austin",
            "state": "TX",
            "postal_code": "78701",
            "is_primary": True
        }
    ],
    "hours": [
        {"day_of_week": 1, "is_open": True, "open_time": "08:00:00", "close_time": "17:00:00"},
        {"day_of_week": 2, "is_open": True, "open_time": "08:00:00", "close_time": "17:00:00"},
        {"day_of_week": 3, "is_open": True, "open_time": "08:00:00", "close_time": "17:00:00"},
        {"day_of_week": 4, "is_open": True, "open_time": "08:00:00", "close_time": "17:00:00"},
        {"day_of_week": 5, "is_open": True, "open_time": "08:00:00", "close_time": "17:00:00"}
    ],
    "branding": {
        "primary_color": "#3B82F6",
        "secondary_color": "#10B981"
    },
    "idempotency_key": str(uuid.uuid4())
}

def test_deployment_endpoint():
    """Test the deployment endpoint structure."""
    print("🧪 Testing Mobile Deployment API Structure")
    print("=" * 50)
    
    # Test data validation
    print(f"📋 Test subdomain: {TEST_DATA['subdomain']}")
    print(f"📊 Service areas: {len(TEST_DATA['service_areas'])}")
    print(f"🔧 Services: {len(TEST_DATA['services'])}")
    print(f"📦 Products: {len(TEST_DATA['products'])}")
    print(f"🏢 Locations: {len(TEST_DATA['locations'])}")
    print(f"⏰ Business hours: {len(TEST_DATA['hours'])}")
    
    # Test endpoint (will fail without auth, but we can see the structure)
    print("\n🚀 Testing deployment endpoint...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/mobile/website/deploy",
            json=TEST_DATA,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📄 Response headers: {dict(response.headers)}")
        
        if response.status_code == 401:
            print("✅ Endpoint exists but requires authentication (expected)")
        elif response.status_code == 404:
            print("❌ Endpoint not found - check if API is running")
        else:
            print(f"📝 Response body: {response.text[:500]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the backend running on localhost:8000?")
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
    
    # Test status endpoint structure
    print("\n📊 Testing status endpoint structure...")
    test_deployment_id = str(uuid.uuid4())
    
    try:
        response = requests.get(
            f"{BASE_URL}/mobile/website/deployments/{test_deployment_id}",
            timeout=10
        )
        
        print(f"📡 Status endpoint response: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Status endpoint exists but requires authentication (expected)")
        elif response.status_code == 404:
            print("❌ Status endpoint not found")
            
    except Exception as e:
        print(f"❌ Status request failed: {str(e)}")
    
    # Test list endpoint
    print("\n📋 Testing list endpoint structure...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/mobile/website/deployments",
            timeout=10
        )
        
        print(f"📡 List endpoint response: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ List endpoint exists but requires authentication (expected)")
        elif response.status_code == 404:
            print("❌ List endpoint not found")
            
    except Exception as e:
        print(f"❌ List request failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("• All endpoints should return 401 (Unauthorized) if properly configured")
    print("• 404 errors indicate missing endpoints or incorrect routing")
    print("• Connection errors mean the backend isn't running")
    print("\n💡 To run full tests with authentication:")
    print("   python test_mobile_deployment.py --token YOUR_JWT_TOKEN")

def validate_test_data():
    """Validate the test data structure."""
    print("\n🔍 Validating test data structure...")
    
    required_fields = [
        "subdomain", "service_areas", "services", "hours"
    ]
    
    for field in required_fields:
        if field in TEST_DATA:
            print(f"✅ {field}: OK")
        else:
            print(f"❌ {field}: Missing")
    
    # Validate subdomain format
    subdomain = TEST_DATA["subdomain"]
    if subdomain.islower() and subdomain.replace("-", "").isalnum():
        print(f"✅ Subdomain format: OK ({subdomain})")
    else:
        print(f"❌ Subdomain format: Invalid ({subdomain})")
    
    # Validate hours coverage
    weekdays = [h["day_of_week"] for h in TEST_DATA["hours"]]
    if all(day in weekdays for day in [1, 2, 3, 4, 5]):
        print("✅ Business hours: Monday-Friday covered")
    else:
        print("❌ Business hours: Missing weekdays")
    
    # Validate service areas
    if TEST_DATA["service_areas"] and len(TEST_DATA["service_areas"]) > 0:
        print(f"✅ Service areas: {len(TEST_DATA['service_areas'])} areas")
    else:
        print("❌ Service areas: None provided")
    
    print("✅ Test data validation complete")

if __name__ == "__main__":
    print("🧪 Simple Mobile Deployment Test")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    validate_test_data()
    test_deployment_endpoint()
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
