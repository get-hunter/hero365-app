#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.application.services.llm_orchestrator import LLMContentOrchestrator
from app.domain.entities.service_page_content import ContentBlockType
import json

async def test_serialization():
    orchestrator = LLMContentOrchestrator()
    
    context = {
        'business_name': 'Elite HVAC Austin',
        'service_name': 'AC Installation',
        'city': 'Austin',
        'state': 'TX',
        'phone': '(512) 555-0123',
        'email': 'info@elitehvacaustin.com'
    }
    
    # Test generating full page content
    page_content = await orchestrator.generate_service_page_content(
        business_id="550e8400-e29b-41d4-a716-446655440010",
        service_slug="ac-installation",
        context=context
    )
    
    print(f"Page content blocks: {len(page_content.content_blocks)}")
    
    # Test serialization
    content_blocks_data = [block.model_dump() for block in page_content.content_blocks]
    print(f"Serialized content blocks: {len(content_blocks_data)}")
    
    for i, block_data in enumerate(content_blocks_data):
        print(f"Block {i}: {block_data['type']} - {len(str(block_data['content']))} chars")
        print(f"  Content keys: {list(block_data['content'].keys())}")
    
    # Test JSON serialization
    try:
        json_str = json.dumps(content_blocks_data)
        print(f"JSON serialization successful: {len(json_str)} chars")
    except Exception as e:
        print(f"JSON serialization failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_serialization())
