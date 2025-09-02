#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.application.services.llm_orchestrator import LLMContentOrchestrator
from app.domain.entities.service_page_content import ContentBlockType

async def test_content_generation():
    orchestrator = LLMContentOrchestrator()
    
    context = {
        'business_name': 'Elite HVAC Austin',
        'service_name': 'AC Installation',
        'city': 'Austin',
        'state': 'TX',
        'phone': '(512) 555-0123',
        'email': 'info@elitehvacaustin.com'
    }
    
    # Test generating a hero block
    hero_block = await orchestrator.generate_content_block(
        block_type=ContentBlockType.HERO,
        context=context
    )
    
    print(f"Hero block: {hero_block}")
    if hero_block:
        print(f"Hero content: {hero_block.content}")
        print(f"Hero type: {hero_block.type}")
        print(f"Hero source: {hero_block.source}")
    
    # Test generating full page content
    page_content = await orchestrator.generate_service_page_content(
        business_id="550e8400-e29b-41d4-a716-446655440010",
        service_slug="ac-installation",
        context=context
    )
    
    print(f"\nPage content blocks: {len(page_content.content_blocks)}")
    for i, block in enumerate(page_content.content_blocks):
        print(f"Block {i}: {block.type} - {len(str(block.content))} chars")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_content_generation())
