#!/usr/bin/env python3
"""
Test optimized Claude API usage - should reduce from 25+ calls to 1-2 calls
"""

import asyncio
import uuid
import time
from pathlib import Path

from app.application.services.website_orchestration_service import WebsiteOrchestrationService
from app.domain.entities.business import Business, TradeCategory, CompanySize, ResidentialTrade
from app.domain.entities.business_branding import BusinessBranding, ColorScheme, Typography
from app.domain.entities.website import BusinessWebsite, WebsiteStatus
from app.infrastructure.templates.website_templates import WebsiteTemplateService, WebsiteTemplate


class APICallCounter:
    """Track Claude API calls to measure optimization."""
    
    def __init__(self):
        self.call_count = 0
        self.start_time = None
        self.end_time = None
    
    def start_tracking(self):
        self.call_count = 0
        self.start_time = time.time()
        print("🔍 Starting API call tracking...")
    
    def increment(self):
        self.call_count += 1
        print(f"📞 Claude API Call #{self.call_count}")
    
    def stop_tracking(self):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        print(f"\n📊 API Usage Summary:")
        print(f"   Total Calls: {self.call_count}")
        print(f"   Duration: {duration:.2f}s")
        print(f"   Calls/Second: {self.call_count/duration:.2f}")
        
        if self.call_count <= 2:
            print("✅ OPTIMIZATION SUCCESS: ≤2 API calls")
        elif self.call_count <= 5:
            print("⚠️  PARTIAL OPTIMIZATION: 3-5 API calls")
        else:
            print("❌ OPTIMIZATION FAILED: >5 API calls")


async def test_optimized_generation():
    """Test the optimized content generation."""
    
    print("🚀 Testing Optimized Claude API Usage")
    print("=" * 60)
    
    counter = APICallCounter()
    
    # Create test business
    business = Business(
        id=uuid.uuid4(),
        name='QuickFix Plumbing',
        industry='plumbing',
        trade_category=TradeCategory.RESIDENTIAL,
        company_size=CompanySize.SMALL,
        phone_number='555-123-4567',
        business_email='test@quickfixplumbing.com',
        service_areas=['New York', 'Brooklyn'],
        residential_trades=[ResidentialTrade.PLUMBING],
        address="123 Main Street",
        city="New York", 
        state="NY",
        zip_code="10001"
    )
    
    branding = BusinessBranding(
        business_id=business.id,
        color_scheme=ColorScheme(
            primary_color='#1e40af',
            secondary_color='#3b82f6'
        ),
        typography=Typography(
            heading_font='Inter',
            body_font='Inter'
        )
    )
    
    website = BusinessWebsite(
        id=uuid.uuid4(),
        business_id=business.id,
        subdomain='quickfix-optimized',
        status=WebsiteStatus.DRAFT,
        seo_keywords=['plumbing', 'repair', 'emergency']
    )
    
    # Get template
    template_data = WebsiteTemplateService.get_template_by_trade('plumbing', TradeCategory.RESIDENTIAL)
    template = WebsiteTemplate(**template_data)
    
    print(f"🏢 Business: {business.name}")
    print(f"🎨 Template: {template.name}")
    print(f"📄 Pages: {len(template.structure.get('pages', []))}")
    
    # Count sections
    total_sections = 0
    for page in template.structure.get('pages', []):
        sections = len(page.get('sections', []))
        total_sections += sections
        print(f"   - {page.get('name')}: {sections} sections")
    
    print(f"📋 Total Sections: {total_sections}")
    print(f"\n🔥 OLD APPROACH: Would make ~{len(template.structure.get('pages', [])) * 2 + total_sections} API calls")
    print(f"⚡ NEW APPROACH: Should make 1-2 API calls")
    
    # Test optimized generation
    from app.infrastructure.adapters.hero365_subdomain_adapter import Hero365SubdomainAdapter
    hosting_service = Hero365SubdomainAdapter()
    orchestration_service = WebsiteOrchestrationService(hosting_service)
    
    try:
        counter.start_tracking()
        
        print(f"\n🏗️ Building website with optimized generation...")
        
        # Monkey patch to count API calls
        original_create = orchestration_service.content_generator.client.messages.create
        
        async def counting_create(*args, **kwargs):
            counter.increment()
            return await original_create(*args, **kwargs)
        
        orchestration_service.content_generator.client.messages.create = counting_create
        
        # Build website
        result = await orchestration_service.build_website(
            business=business,
            branding=branding,
            template=template,
            options={"subdomain": "quickfix-optimized"}
        )
        
        counter.stop_tracking()
        
        if result["success"]:
            print(f"\n✅ Website build successful!")
            print(f"   Build Path: {result['build_path']}")
            print(f"   Build Time: {result.get('build_time_seconds', 0):.2f}s")
            print(f"   Content Pages: {len(result.get('content_pages', []))}")
            
            # Check if we have real content
            if result.get('content_pages'):
                print(f"\n📄 Generated Content Preview:")
                for page in result['content_pages'][:2]:  # Show first 2 pages
                    print(f"   - {page}")
        else:
            print(f"\n❌ Website build failed: {result.get('error')}")
        
        # Calculate optimization impact
        old_calls = len(template.structure.get('pages', [])) * 2 + total_sections
        new_calls = counter.call_count
        reduction = ((old_calls - new_calls) / old_calls) * 100
        
        print(f"\n🎯 Optimization Results:")
        print(f"   Old Approach: {old_calls} calls")
        print(f"   New Approach: {new_calls} calls") 
        print(f"   Reduction: {reduction:.1f}%")
        
        if reduction >= 80:
            print(f"   🏆 EXCELLENT optimization!")
        elif reduction >= 50:
            print(f"   ✅ GOOD optimization!")
        else:
            print(f"   ⚠️  Needs more optimization")
            
    except Exception as e:
        counter.stop_tracking()
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_optimized_generation())
