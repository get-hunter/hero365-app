#!/usr/bin/env python3
"""
Test script to verify JSON serialization fix for voice agent context
"""

import json
import sys
import os
import asyncio
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal

# Add the app directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.livekit_agents.context_preloader import ContextPreloader

def test_json_serialization():
    """Test that the context preloader can handle UUID and Decimal objects"""
    
    print("🧪 Testing JSON serialization for voice agent context...")
    
    # Create a context preloader instance
    preloader = ContextPreloader()
    
    # Test data with potentially problematic types
    test_data = {
        'user_id': uuid4(),  # UUID object
        'business_id': uuid4(),  # UUID object
        'timestamp': datetime.now(),  # datetime object
        'revenue': Decimal('1250.50'),  # Decimal object
        'contacts': [
            {
                'id': uuid4(),  # UUID object
                'name': 'John Doe',
                'revenue': Decimal('500.25'),  # Decimal object
                'last_contact': datetime.now()  # datetime object
            },
            {
                'id': uuid4(),  # UUID object
                'name': 'Jane Smith',
                'revenue': Decimal('750.25'),  # Decimal object
                'last_contact': datetime.now()  # datetime object
            }
        ],
        'nested_dict': {
            'some_id': uuid4(),  # UUID object
            'amount': Decimal('99.99'),  # Decimal object
            'created_at': datetime.now()  # datetime object
        }
    }
    
    try:
        # Test serialization
        print("📝 Testing _make_json_serializable method...")
        serialized = preloader._make_json_serializable(test_data)
        
        # Test JSON encoding
        print("🔄 Testing JSON encoding...")
        json_str = json.dumps(serialized, ensure_ascii=False, separators=(',', ':'))
        
        # Test JSON decoding
        print("🔄 Testing JSON decoding...")
        decoded = json.loads(json_str)
        
        print("✅ JSON serialization test passed!")
        print(f"📊 Serialized data size: {len(json_str)} characters")
        
        # Print sample of converted data
        print("\n📋 Sample conversions:")
        print(f"  Original user_id type: {type(test_data['user_id'])}")
        print(f"  Converted user_id type: {type(serialized['user_id'])}")
        print(f"  Original revenue type: {type(test_data['revenue'])}")
        print(f"  Converted revenue type: {type(serialized['revenue'])}")
        print(f"  Original timestamp type: {type(test_data['timestamp'])}")
        print(f"  Converted timestamp type: {type(serialized['timestamp'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON serialization test failed: {e}")
        return False

def test_room_metadata_serialization():
    """Test room metadata serialization as it would be done in the API"""
    
    print("\n🧪 Testing room metadata serialization...")
    
    # Create a context preloader instance
    preloader = ContextPreloader()
    
    # Simulate room metadata with context (similar to mobile_voice.py)
    room_metadata = {
        'session_id': 'hero365_voice_test123',
        'user_id': str(uuid4()),  # Already converted to string
        'business_id': str(uuid4()),  # Already converted to string
        'created_at': datetime.utcnow().isoformat(),
        'device_info': {
            'device_name': 'Test iPhone',
            'device_model': 'iPhone 15 Pro',
            'os_version': '17.2.1',
            'app_version': '1.0.0',
            'network_type': 'wifi'
        },
        'session_config': {
            'session_type': 'general',
            'language': 'en-US',
            'background_audio_enabled': True,
            'max_duration_minutes': 60
        },
        'preloaded_context': {
            'preloaded_at': datetime.now().isoformat(),
            'user_id': str(uuid4()),
            'business_id': str(uuid4()),
            'business_context': {
                'business_id': str(uuid4()),
                'business_name': 'Test Plumbing Services',
                'business_type': 'plumbing',
                'revenue_this_month': float(Decimal('5250.50'))
            },
            'user_context': {
                'user_id': str(uuid4()),
                'name': 'John Smith',
                'email': 'john@test.com'
            },
            'recent_contacts': [
                {
                    'id': str(uuid4()),
                    'name': 'Alice Johnson',
                    'last_interaction': datetime.now().isoformat()
                }
            ],
            'context_version': '1.0'
        }
    }
    
    try:
        # Test the same serialization logic as used in mobile_voice.py
        print("📝 Testing room metadata JSON serialization...")
        metadata_json = json.dumps(room_metadata, ensure_ascii=False, separators=(',', ':'))
        
        # Test decoding
        print("🔄 Testing room metadata JSON decoding...")
        decoded = json.loads(metadata_json)
        
        print("✅ Room metadata serialization test passed!")
        print(f"📊 Metadata size: {len(metadata_json)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Room metadata serialization test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting JSON serialization tests for voice agent context...")
    
    results = []
    
    # Test 1: Basic JSON serialization
    results.append(test_json_serialization())
    
    # Test 2: Room metadata serialization
    results.append(test_room_metadata_serialization())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All JSON serialization tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 