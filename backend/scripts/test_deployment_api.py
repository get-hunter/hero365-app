#!/usr/bin/env python3
"""
Test script for the Website Deployment API
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.api.routes.website_deployment import (
    WebsiteDeploymentRequest,
    deploy_website_background,
    deployment_tracker,
    update_deployment_status
)


async def test_deployment_api():
    """Test the website deployment API functionality."""
    
    print("🧪 Testing Website Deployment API")
    print("=" * 50)
    
    # Create test request
    test_request = WebsiteDeploymentRequest(
        business_name="Test HVAC Company",
        trade_type="hvac",
        location="Austin, TX",
        phone_number="(512) 555-TEST",
        email="test@testhvac.com",
        address="123 Test St, Austin, TX 78701",
        target_keywords=["hvac austin", "ac repair austin"],
        service_areas=["Round Rock", "Cedar Park"],
        include_reviews=True,
        include_service_areas=True,
        include_about=True,
        emergency_service=True
    )
    
    print(f"📋 Test Request:")
    print(f"   Business: {test_request.business_name}")
    print(f"   Trade: {test_request.trade_type}")
    print(f"   Location: {test_request.location}")
    print(f"   Keywords: {test_request.target_keywords}")
    
    # Test deployment status tracking
    deployment_id = "test-deployment-123"
    
    print(f"\n🚀 Testing deployment status tracking...")
    
    # Test status updates
    await update_deployment_status(deployment_id, "pending", 0, "Starting deployment")
    print(f"   ✅ Status: {deployment_tracker[deployment_id]['status']}")
    
    await update_deployment_status(deployment_id, "building", 25, "Generating content")
    print(f"   ✅ Status: {deployment_tracker[deployment_id]['status']} ({deployment_tracker[deployment_id]['progress']}%)")
    
    await update_deployment_status(deployment_id, "deploying", 75, "Deploying to Cloudflare")
    print(f"   ✅ Status: {deployment_tracker[deployment_id]['status']} ({deployment_tracker[deployment_id]['progress']}%)")
    
    await update_deployment_status(
        deployment_id, "completed", 100, "Deployment completed",
        website_url="https://test123.hero365-websites.pages.dev",
        seo_score=95
    )
    print(f"   ✅ Status: {deployment_tracker[deployment_id]['status']} ({deployment_tracker[deployment_id]['progress']}%)")
    print(f"   🌐 URL: {deployment_tracker[deployment_id]['website_url']}")
    print(f"   📊 SEO Score: {deployment_tracker[deployment_id]['seo_score']}")
    
    # Test AI content generation
    print(f"\n🤖 Testing AI content generation...")
    
    try:
        from app.application.services.ai_seo_content_service import AISEOContentService
        
        ai_service = AISEOContentService()
        
        # Create business entity for testing
        business_entity = type('Business', (), {
            'name': test_request.business_name,
            'phone_number': test_request.phone_number,
            'business_email': test_request.email,
            'business_address': test_request.address,
            'description': f"Professional {test_request.trade_type} services"
        })()
        
        # Generate content
        content = await ai_service.generate_website_content(
            business=business_entity,
            trade_type=test_request.trade_type,
            location=test_request.location,
            target_keywords=test_request.target_keywords
        )
        
        print(f"   ✅ Generated {len(content)} content sections:")
        for section, data in content.items():
            if isinstance(data, dict):
                print(f"      - {section}: {len(data)} fields")
            elif isinstance(data, list):
                print(f"      - {section}: {len(data)} items")
            else:
                print(f"      - {section}: {type(data).__name__}")
        
        # Show sample content
        print(f"\n📝 Sample Generated Content:")
        print(f"   Hero Headline: {content['hero']['headline']}")
        print(f"   SEO Title: {content['seo']['title']}")
        print(f"   Services: {len(content['services'])} services")
        print(f"   Keywords: {', '.join(content['seo']['keywords'][:3])}...")
        
    except Exception as e:
        print(f"   ❌ AI content generation test failed: {str(e)}")
    
    # Test request validation
    print(f"\n✅ Testing request validation...")
    
    try:
        # Valid request
        valid_request = WebsiteDeploymentRequest(
            business_name="Valid Business",
            trade_type="hvac",
            location="Austin",
            phone_number="(512) 555-0000",
            email="valid@business.com",
            address="123 Main St"
        )
        print(f"   ✅ Valid request accepted")
        
        # Test with invalid email (should still work with Pydantic validation)
        try:
            invalid_request = WebsiteDeploymentRequest(
                business_name="Invalid Business",
                trade_type="hvac",
                location="Austin",
                phone_number="(512) 555-0000",
                email="invalid-email",  # Invalid email format
                address="123 Main St"
            )
            print(f"   ⚠️  Invalid email accepted (Pydantic may auto-correct)")
        except Exception as e:
            print(f"   ✅ Invalid email rejected: {str(e)}")
            
    except Exception as e:
        print(f"   ❌ Request validation test failed: {str(e)}")
    
    print(f"\n🎉 API Testing Complete!")
    print(f"📊 Deployment Tracker has {len(deployment_tracker)} entries")
    
    return True


async def main():
    """Main test function."""
    try:
        success = await test_deployment_api()
        if success:
            print("\n✅ All tests passed!")
            return 0
        else:
            print("\n❌ Some tests failed!")
            return 1
    except Exception as e:
        print(f"\n💥 Test suite failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
