#!/usr/bin/env python3
"""
Test Content Generation Providers

CLI script to test and compare different AI content generation providers.
This helps verify that all providers are working correctly and allows
comparison of their output quality.
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.infrastructure.adapters.content_generation_factory import (
    get_provider_info, create_content_adapter
)
from app.domain.entities.business import Business, TradeCategory
from app.domain.entities.business_branding import BusinessBranding
from app.core.config import settings


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")


def print_provider_info(providers: Dict[str, Dict[str, Any]]):
    """Print information about available providers."""
    
    print_header("Available Content Generation Providers")
    
    for name, info in providers.items():
        status = "✅ Configured" if info["configured"] else "❌ Not Configured"
        print(f"\n{name.upper()}:")
        print(f"  Status: {status}")
        print(f"  Description: {info['description']}")
        print(f"  Adapter: {info['adapter_class']}")


async def test_provider(provider_name: str, business: Business, branding: BusinessBranding) -> Dict[str, Any]:
    """Test a specific provider."""
    
    print(f"\n🧪 Testing {provider_name.upper()} provider...")
    
    start_time = datetime.utcnow()
    
    try:
        # Create adapter
        adapter = create_content_adapter(provider=provider_name)
        
        # Test basic content generation
        content = await adapter.generate_page_content(
            business=business,
            branding=branding,
            page_type="home",
            context={"test_mode": True}
        )
        
        # Test SEO content generation
        seo_content = await adapter.generate_seo_content(
            business=business,
            target_keywords=["plumbing services", "emergency plumber", business.city],
            page_type="home"
        )
        
        test_time = (datetime.utcnow() - start_time).total_seconds()
        
        result = {
            "success": True,
            "provider": provider_name,
            "test_duration": test_time,
            "content_keys": list(content.keys()) if content else [],
            "seo_keys": list(seo_content.keys()) if seo_content else [],
            "content_length": len(str(content)) if content else 0,
            "generated_by": content.get("generated_by") if content else None
        }
        
        print(f"   ✅ Success in {test_time:.2f}s")
        print(f"   📄 Content keys: {', '.join(result['content_keys'])}")
        print(f"   🔍 SEO keys: {', '.join(result['seo_keys'])}")
        print(f"   📊 Content length: {result['content_length']} chars")
        
        return result
        
    except Exception as e:
        test_time = (datetime.utcnow() - start_time).total_seconds()
        
        result = {
            "success": False,
            "provider": provider_name,
            "test_duration": test_time,
            "error": str(e)
        }
        
        print(f"   ❌ Failed in {test_time:.2f}s: {str(e)}")
        
        return result


async def compare_providers(business: Business, branding: BusinessBranding):
    """Compare all configured providers."""
    
    print_header("Provider Comparison Test")
    
    providers = get_provider_info()
    configured_providers = [name for name, info in providers.items() if info["configured"]]
    
    if not configured_providers:
        print("❌ No providers are configured. Please set up API keys.")
        return
    
    print(f"Testing {len(configured_providers)} configured providers...")
    
    results = []
    
    for provider_name in configured_providers:
        result = await test_provider(provider_name, business, branding)
        results.append(result)
    
    # Print comparison summary
    print_header("Comparison Summary")
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    if successful_tests:
        print(f"\n✅ Successful tests: {len(successful_tests)}")
        
        # Sort by speed
        successful_tests.sort(key=lambda x: x["test_duration"])
        
        print("\n🏃 Speed ranking:")
        for i, result in enumerate(successful_tests, 1):
            print(f"  {i}. {result['provider'].upper()}: {result['test_duration']:.2f}s")
        
        # Sort by content length
        successful_tests.sort(key=lambda x: x["content_length"], reverse=True)
        
        print("\n📝 Content length ranking:")
        for i, result in enumerate(successful_tests, 1):
            print(f"  {i}. {result['provider'].upper()}: {result['content_length']} chars")
    
    if failed_tests:
        print(f"\n❌ Failed tests: {len(failed_tests)}")
        for result in failed_tests:
            print(f"  - {result['provider'].upper()}: {result['error']}")
    
    return results


async def test_specific_provider(provider_name: str):
    """Test a specific provider in detail."""
    
    print_header(f"Detailed Test: {provider_name.upper()}")
    
    # Create test business
    business = Business(
        name="ABC Plumbing Services",
        trade_category=TradeCategory.RESIDENTIAL,
        primary_residential_trade="Plumbing",
        city="Austin",
        state="TX",
        zip_code="78701",
        phone="(512) 555-0123",
        email="info@abcplumbing.com",
        address="123 Main St"
    )
    
    # Create test branding
    branding = BusinessBranding(
        business_id=business.id,
        primary_color="#1e40af",
        secondary_color="#64748b",
        font_family="Inter",
        theme_name="professional"
    )
    
    try:
        adapter = create_content_adapter(provider=provider_name)
        
        # Test different page types
        page_types = ["home", "services", "contact", "about"]
        
        for page_type in page_types:
            print(f"\n📄 Generating {page_type} page content...")
            
            start_time = datetime.utcnow()
            
            try:
                content = await adapter.generate_page_content(
                    business=business,
                    branding=branding,
                    page_type=page_type
                )
                
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                print(f"   ✅ Generated in {duration:.2f}s")
                print(f"   📊 Keys: {', '.join(content.keys()) if content else 'None'}")
                
                # Show a sample of the content
                if content and "raw_content" in content:
                    sample = content["raw_content"][:200] + "..." if len(content["raw_content"]) > 200 else content["raw_content"]
                    print(f"   📝 Sample: {sample}")
                
            except Exception as e:
                print(f"   ❌ Failed: {str(e)}")
        
        # Test content quality validation
        print(f"\n🔍 Testing content quality validation...")
        
        try:
            test_content = {"title": "Test Page", "content": "This is test content for validation."}
            
            quality_result = await adapter.validate_content_quality(
                content=test_content,
                business=business
            )
            
            print(f"   ✅ Quality validation completed")
            print(f"   📊 Overall score: {quality_result.get('overall_score', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Quality validation failed: {str(e)}")
        
    except Exception as e:
        print(f"❌ Failed to initialize {provider_name} adapter: {str(e)}")


async def main():
    """Main CLI function."""
    
    print_header("Hero365 Content Generation Provider Tester")
    print(f"Current default provider: {settings.CONTENT_GENERATION_PROVIDER}")
    
    # Get available providers
    providers = get_provider_info()
    
    if len(sys.argv) > 1:
        # Test specific provider
        provider_name = sys.argv[1].lower()
        
        if provider_name not in providers:
            print(f"❌ Unknown provider: {provider_name}")
            print(f"Available providers: {', '.join(providers.keys())}")
            return
        
        if not providers[provider_name]["configured"]:
            print(f"❌ Provider {provider_name} is not configured")
            return
        
        await test_specific_provider(provider_name)
    
    else:
        # Show provider info and run comparison
        print_provider_info(providers)
        
        # Create test business for comparison
        business = Business(
            name="ABC Plumbing Services",
            trade_category=TradeCategory.RESIDENTIAL,
            primary_residential_trade="Plumbing",
            city="Austin",
            state="TX",
            zip_code="78701",
            phone="(512) 555-0123",
            email="info@abcplumbing.com",
            address="123 Main St"
        )
        
        branding = BusinessBranding(
            business_id=business.id,
            primary_color="#1e40af",
            secondary_color="#64748b",
            font_family="Inter",
            theme_name="professional"
        )
        
        await compare_providers(business, branding)
    
    print(f"\n{'=' * 60}")
    print("Test completed!")
    
    if len(sys.argv) <= 1:
        print("\nTo test a specific provider in detail, run:")
        print("python test_content_providers.py <provider_name>")
        print(f"Available providers: {', '.join(providers.keys())}")


if __name__ == "__main__":
    asyncio.run(main())
