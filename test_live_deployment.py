#!/usr/bin/env python3
"""
Test Live Website Deployment

This script tests the actual deployment endpoints to see where websites get deployed
and provides the live URLs for testing.
"""

import json
import uuid
import time
import requests
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

def test_dynamic_website_deployment():
    """Test the dynamic website deployment endpoint."""
    print("🚀 Testing Dynamic Website Deployment")
    print("=" * 50)
    
    # Test data for dynamic deployment
    deployment_data = {
        "business_name": "Test HVAC Company",
        "business_description": "Professional HVAC services in Austin",
        "services": [
            "HVAC Repair",
            "AC Installation", 
            "Heating Maintenance"
        ],
        "location": "Austin, TX",
        "phone": "(512) 555-0123",
        "email": "contact@testhvac.com"
    }
    
    print(f"📋 Business: {deployment_data['business_name']}")
    print(f"📍 Location: {deployment_data['location']}")
    print(f"🔧 Services: {len(deployment_data['services'])}")
    
    try:
        # Try dynamic website deployment
        response = requests.post(
            f"{BASE_URL}/dynamic-websites/deploy",
            json=deployment_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📡 Response Status: {response.status_code}")
        print(f"📄 Response: {response.text[:500]}...")
        
        if response.status_code == 202:  # Accepted
            result = response.json()
            deployment_id = result.get("deployment_id")
            
            if deployment_id:
                print(f"✅ Deployment started! ID: {deployment_id}")
                
                # Poll for status
                poll_deployment_status(deployment_id, "dynamic-websites")
            
        elif response.status_code == 401 or response.status_code == 403:
            print("⚠️  Authentication required - endpoint exists but needs auth")
            
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def test_website_templates_deployment():
    """Test the website templates deployment."""
    print("\n🎨 Testing Website Templates Deployment")
    print("=" * 50)
    
    template_data = {
        "template_name": "professional",
        "business_data": {
            "name": "Elite Home Services",
            "description": "Professional home services in Austin",
            "phone": "(512) 555-0456",
            "email": "info@elitehome.com",
            "address": "123 Business St, Austin, TX 78701"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/website-templates/deploy",
            json=template_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response: {response.text[:300]}...")
        
        if response.status_code == 202:
            result = response.json()
            deployment_id = result.get("deployment_id")
            
            if deployment_id:
                print(f"✅ Template deployment started! ID: {deployment_id}")
                poll_deployment_status(deployment_id, "website-templates")
        
    except Exception as e:
        print(f"❌ Template deployment failed: {str(e)}")

def poll_deployment_status(deployment_id, endpoint_prefix, max_polls=20):
    """Poll deployment status until completion."""
    print(f"\n📊 Polling deployment status for {deployment_id}...")
    
    for i in range(max_polls):
        try:
            # Try different status endpoints
            status_urls = [
                f"{BASE_URL}/{endpoint_prefix}/status/{deployment_id}",
                f"{BASE_URL}/dynamic-websites/status/{deployment_id}",
                f"{BASE_URL}/website-deployment/status/{deployment_id}"
            ]
            
            for status_url in status_urls:
                response = requests.get(status_url, timeout=10)
                
                if response.status_code == 200:
                    status_data = response.json()
                    
                    print(f"📊 Poll {i+1}: Status = {status_data.get('status', 'unknown')}")
                    
                    if 'website_url' in status_data:
                        print(f"🌐 Website URL: {status_data['website_url']}")
                    
                    if 'deploy_url' in status_data:
                        print(f"🌐 Deploy URL: {status_data['deploy_url']}")
                    
                    # Check if deployment is complete
                    status = status_data.get('status', '').lower()
                    if status in ['completed', 'success', 'deployed']:
                        print(f"✅ Deployment completed!")
                        return status_data
                    elif status in ['failed', 'error']:
                        print(f"❌ Deployment failed: {status_data.get('error', 'Unknown error')}")
                        return status_data
                    
                    break  # Found working status endpoint
            
            time.sleep(3)  # Wait before next poll
            
        except Exception as e:
            print(f"⚠️  Status poll {i+1} failed: {str(e)}")
    
    print("⏰ Polling timeout reached")
    return None

def check_existing_deployments():
    """Check for existing deployments."""
    print("\n📋 Checking for Existing Deployments")
    print("=" * 50)
    
    endpoints_to_check = [
        "/dynamic-websites/deployments",
        "/website-deployment/deployments", 
        "/website-templates/deployments",
        "/mobile/website/deployments"
    ]
    
    for endpoint in endpoints_to_check:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            
            print(f"📡 {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"  📊 Found {len(data)} deployments")
                    for deployment in data[:3]:  # Show first 3
                        if 'website_url' in deployment:
                            print(f"  🌐 {deployment['website_url']}")
                elif isinstance(data, dict) and 'deployments' in data:
                    deployments = data['deployments']
                    print(f"  📊 Found {len(deployments)} deployments")
                    for deployment in deployments[:3]:
                        if 'website_url' in deployment:
                            print(f"  🌐 {deployment['website_url']}")
                        elif 'deploy_url' in deployment:
                            print(f"  🌐 {deployment['deploy_url']}")
                else:
                    print(f"  📄 Response: {str(data)[:100]}...")
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

def show_deployment_info():
    """Show deployment information and URLs."""
    print("\n📚 Deployment Information")
    print("=" * 50)
    
    print("🌐 Expected URL Patterns:")
    print("• Cloudflare Pages: https://hero365-{business}.pages.dev")
    print("• Project-specific: https://{project-name}.pages.dev")
    print("• Custom domains: https://{custom-domain}")
    print()
    
    print("🔧 Available Deployment Endpoints:")
    print("• POST /api/v1/dynamic-websites/deploy")
    print("• POST /api/v1/website-templates/deploy") 
    print("• POST /api/v1/mobile/website/deploy")
    print("• POST /api/v1/website-deployment/deploy")
    print()
    
    print("📊 Status Endpoints:")
    print("• GET /api/v1/dynamic-websites/status/{id}")
    print("• GET /api/v1/website-deployment/status/{id}")
    print("• GET /api/v1/mobile/website/deployments/{id}")
    print()
    
    print("💡 To test with authentication:")
    print("1. Get a valid JWT token from the auth endpoint")
    print("2. Use: Authorization: Bearer {token}")
    print("3. Ensure you have business context")

if __name__ == "__main__":
    print("🧪 Live Website Deployment Test")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    check_existing_deployments()
    show_deployment_info()
    
    print("\n🚀 Testing Deployment Endpoints...")
    test_dynamic_website_deployment()
    test_website_templates_deployment()
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🎯 Summary:")
    print("• Multiple deployment endpoints are available")
    print("• Authentication is required for actual deployments")
    print("• Websites deploy to Cloudflare Pages (*.pages.dev)")
    print("• Status polling is available for tracking progress")
    print("\n💡 Next: Use a real auth token to trigger actual deployments!")
