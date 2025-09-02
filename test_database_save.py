#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.db import get_supabase_client
from app.domain.entities.service_page_content import ContentBlock, ContentBlockType, ContentSource
import json

def test_database_save():
    # Get Supabase client
    supabase = get_supabase_client()
    
    # Create a simple content block
    block = ContentBlock(
        type=ContentBlockType.HERO,
        content={'h1': 'Test Hero', 'description': 'Test description'},
        source=ContentSource.TEMPLATE
    )
    
    # Serialize it
    block_data = block.model_dump()
    print(f"Block data: {block_data}")
    
    # Test data to save
    test_data = {
        "business_id": "550e8400-e29b-41d4-a716-446655440010",
        "service_slug": "test-save",
        "title": "Test Save",
        "meta_description": "Test",
        "canonical_url": "/test",
        "target_keywords": [],
        "content_blocks": [block_data],
        "schema_blocks": [],
        "content_source": "template",
        "revision": 1,
        "content_hash": "test",
        "metrics": {
            "word_count": 0,
            "heading_count": 0,
            "faq_count": 0,
            "image_count": 0,
            "internal_link_count": 0,
            "external_link_count": 0,
            "keyword_density": {},
            "readability_score": None
        },
        "status": "published"
    }
    
    print(f"Test data content_blocks: {test_data['content_blocks']}")
    
    # Try to save
    try:
        # Delete existing
        supabase.table("service_page_contents").delete().eq(
            "business_id", "550e8400-e29b-41d4-a716-446655440010"
        ).eq("service_slug", "test-save").execute()
        
        # Insert new
        result = supabase.table("service_page_contents").insert(test_data).execute()
        print(f"Insert result: {result}")
        
        # Verify
        verify = supabase.table("service_page_contents").select("content_blocks").eq(
            "business_id", "550e8400-e29b-41d4-a716-446655440010"
        ).eq("service_slug", "test-save").execute()
        
        if verify.data:
            saved_blocks = verify.data[0].get('content_blocks', [])
            print(f"Saved blocks: {saved_blocks}")
        else:
            print("No data found after insert!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_database_save()
