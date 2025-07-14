#!/usr/bin/env python3
"""
Test script to verify OpenAI Agents SDK conversation management
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.voice_agents.core.context_manager import ContextManager
from app.voice_agents.triage.triage_agent import TriageAgent
from app.voice_agents.specialists.contact_agent import ContactAgent


async def test_conversation_management():
    """Test the OpenAI Agents SDK conversation management"""
    print("🧪 Testing OpenAI Agents SDK conversation management...")
    
    # Initialize context manager
    context_manager = ContextManager()
    
    # Initialize context
    test_context = await context_manager.initialize_context(
        user_id="test_user",
        business_id="test_business",
        session_id="test_session"
    )
    
    # Create specialist agents
    contact_agent = ContactAgent(context_manager)
    specialist_agents = {
        'contact': contact_agent
    }
    
    # Create triage agent
    triage_agent = TriageAgent(context_manager, specialist_agents)
    
    # Test conversation flow
    print("\n💬 Test 1: Start contact creation")
    response1 = await triage_agent.process_user_request("I want to create a new contact")
    print(f"Response 1: {response1}")
    
    print("\n💬 Test 2: Provide name")
    response2 = await triage_agent.process_user_request("Luis Enrique")
    print(f"Response 2: {response2}")
    
    print("\n💬 Test 3: Provide phone")
    response3 = await triage_agent.process_user_request("012345678")
    print(f"Response 3: {response3}")
    
    print("\n💬 Test 4: Provide email")
    response4 = await triage_agent.process_user_request("luis@example.com")
    print(f"Response 4: {response4}")
    
    # Check context
    final_context = await context_manager.get_current_context()
    print(f"\n📊 Final context conversation history length: {len(final_context.get('conversation_history', []))}")
    print(f"📊 Ongoing operation: {final_context.get('ongoing_operation', 'None')}")
    
    print("\n✅ Test completed!")


if __name__ == "__main__":
    asyncio.run(test_conversation_management()) 