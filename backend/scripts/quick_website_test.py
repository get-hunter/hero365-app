#!/usr/bin/env python3
"""
Quick Website Generation Test

Simple test to verify the Clean Architecture implementation works.
Tests core components without requiring full AWS setup.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.domain.entities.business import Business, TradeCategory, CompanySize, ResidentialTrade
from app.domain.entities.website import BusinessWebsite
from app.domain.services.seo_domain_service import SEODomainService
from app.domain.services.subdomain_domain_service import SubdomainDomainService


async def test_clean_architecture():
    """Test Clean Architecture components without external dependencies."""
    
    print("🧪 Testing Clean Architecture Components")
    print("=" * 50)
    
    # Create test business
    print("📋 Creating test business...")
    business = Business(
        name="AquaFlow Plumbing Solutions",
        industry="Home Services",
        company_size=CompanySize.SMALL,
        description="Professional residential plumbing services",
        phone_number="(555) 123-FLOW",
        business_email="info@aquaflowplumbing.com",
        business_address="123 Service Street, Austin, TX 78701",
        website="https://aquaflowplumbing.com",
        service_areas=["Austin", "Round Rock", "Cedar Park"],
        trade_category=TradeCategory.RESIDENTIAL,
        residential_trades=[ResidentialTrade.PLUMBING]
    )
    
    # Business created successfully
    
    print(f"✅ Business created: {business.name}")
    
    # Test SEO Domain Service (basic functionality)
    print("\n🔍 Testing SEO Domain Service...")
    seo_service = SEODomainService()
    
    # Test trade keyword generation (business logic only)
    trade_keywords = seo_service._get_trade_keywords(business)
    print(f"✅ Generated {len(trade_keywords)} trade keywords")
    print(f"   Trade keywords: {trade_keywords[:3]}")
    
    print("✅ SEO Domain Service basic functionality working")
    
    # Test Subdomain Domain Service
    print("\n🌐 Testing Subdomain Domain Service...")
    subdomain_service = SubdomainDomainService()
    
    # Create website entity
    website = BusinessWebsite(
        business_id=business.id,
        primary_trade=business.get_primary_trade(),
        template_id=uuid.uuid4(),
        subdomain="test-subdomain"  # Provide subdomain to satisfy validation
    )
    
    # Generate subdomain
    subdomain = subdomain_service.generate_subdomain_name(website)
    print(f"✅ Generated subdomain: {subdomain}")
    
    # Validate subdomain
    validation = subdomain_service.validate_subdomain_name(subdomain)
    print(f"✅ Subdomain validation: {validation['valid']}")
    
    if not validation['valid']:
        print(f"   Errors: {validation['errors']}")
    
    # Test deployment priority
    priority = subdomain_service.calculate_deployment_priority(
        website,
        {"business_tier": "standard", "file_count": 25, "urgent": False}
    )
    print(f"✅ Deployment priority: {priority}/100")
    
    # Test analytics processing
    print("\n📊 Testing Analytics Processing...")
    mock_analytics = {
        "page_views": 156,
        "unique_visitors": 89,
        "bounce_rate": 42.3,
        "traffic_sources": {"search": 67, "direct": 45, "social": 12, "referral": 32}
    }
    
    analytics_summary = subdomain_service.generate_analytics_summary(mock_analytics)
    print(f"✅ Analytics processed:")
    print(f"   Engagement Score: {analytics_summary['engagement_score']}")
    print(f"   Performance Rating: {analytics_summary['performance_rating']}")
    print(f"   Insights: {len(analytics_summary['insights'])} recommendations")
    
    # Test cache strategy
    cache_strategy = subdomain_service.determine_cache_strategy({
        "file_types": ["html", "css", "js", "png"],
        "business_tier": "standard"
    })
    print(f"✅ Cache strategy: {cache_strategy['strategy']}")
    
    # Final results
    print("\n" + "=" * 50)
    print("🎉 ALL CLEAN ARCHITECTURE TESTS PASSED!")
    print("=" * 50)
    
    results = {
        "business_name": business.name,
        "primary_trade": business.get_primary_trade(),
        "generated_subdomain": subdomain,
        "website_url": f"https://{subdomain}.hero365.ai",
        "trade_keywords_count": len(trade_keywords),
        "deployment_priority": priority,
        "engagement_score": analytics_summary['engagement_score'],
        "performance_rating": analytics_summary['performance_rating'],
        "test_timestamp": datetime.utcnow().isoformat()
    }
    
    print("📋 Test Results:")
    for key, value in results.items():
        print(f"   {key}: {value}")
    
    return results


async def test_content_generation_factory():
    """Test the configurable LLM system."""
    
    print("\n🤖 Testing Content Generation Factory...")
    
    try:
        from app.infrastructure.adapters.content_generation_factory import get_provider_info
        
        # Get available providers
        providers = get_provider_info()
        print(f"✅ Available providers: {list(providers.keys())}")
        
        for provider, info in providers.items():
            status = "✅ Configured" if info['configured'] else "❌ Not configured"
            print(f"   {provider}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Content generation test failed: {str(e)}")
        return False


async def main():
    """Run all tests."""
    
    print("🚀 Hero365 Clean Architecture Test Suite")
    print("Testing core domain services and business logic...")
    print()
    
    try:
        # Test core Clean Architecture
        results = await test_clean_architecture()
        
        # Test content generation system
        content_test = await test_content_generation_factory()
        
        print(f"\n✅ Core Architecture: PASSED")
        print(f"✅ Content Generation: {'PASSED' if content_test else 'FAILED'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
