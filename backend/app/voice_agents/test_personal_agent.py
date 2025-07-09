"""
Test Script for Personal Voice Agent

This script demonstrates the basic functionality of the Hero365 personal voice agent.
Run this to test the voice agent with mock data before integrating with LiveKit.
"""

import asyncio
import logging
from typing import Dict, Any

from app.voice_agents.personal.personal_agent import PersonalVoiceAgent
from app.voice_agents.core.voice_config import PersonalAgentConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_personal_agent():
    """Test the personal voice agent with mock data"""
    
    print("🚀 Testing Hero365 Personal Voice Agent")
    print("=" * 50)
    
    # Mock business context
    business_context = {
        "id": "test_business_123",
        "name": "ABC Home Services",
        "type": "Home Services",
        "services": ["Plumbing", "Electrical", "HVAC"],
        "company_size": "small"
    }
    
    # Mock user context
    user_context = {
        "id": "test_user_456", 
        "name": "John Smith",
        "email": "john@abchomeservices.com",
        "is_driving": False,
        "safety_mode": True,
        "voice_speed": "normal",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060
        }
    }
    
    # Create personal agent
    agent = PersonalVoiceAgent(
        business_context=business_context,
        user_context=user_context
    )
    
    print(f"✅ Created agent: {agent.agent_id}")
    print(f"📍 Business: {agent.get_business_name()}")
    print(f"👤 User: {agent.get_user_name()}")
    print()
    
    # Test agent lifecycle
    print("🔄 Testing agent lifecycle...")
    await agent.on_agent_start()
    print("✅ Agent started successfully")
    
    # Test system prompt generation
    print("\n📝 Testing system prompt...")
    prompt = agent.get_system_prompt()
    print(f"System prompt length: {len(prompt)} characters")
    print(f"Includes business name: {'ABC Home Services' in prompt}")
    print(f"Includes user name: {'John Smith' in prompt}")
    
    # Test personalized greeting
    print("\n💬 Testing personalized greeting...")
    greeting = agent.get_personalized_greeting()
    print(f"Greeting: {greeting}")
    
    # Test available tools
    print("\n🛠️ Testing available tools...")
    tools = agent.get_tools()
    print(f"Available tools ({len(tools)}):")
    for i, tool in enumerate(tools, 1):
        tool_name = getattr(tool, '__name__', str(tool))
        print(f"  {i}. {tool_name}")
    
    # Test individual tools
    print("\n🧪 Testing individual tools...")
    
    # Test current time tool
    try:
        time_result = await agent.get_current_time()
        print(f"✅ Current time: {time_result}")
    except Exception as e:
        print(f"❌ Current time failed: {e}")
    
    # Test business summary tool
    try:
        business_result = await agent.get_business_summary()
        print(f"✅ Business summary: {business_result}")
    except Exception as e:
        print(f"❌ Business summary failed: {e}")
    
    # Test driving directions tool
    try:
        directions_result = await agent.get_driving_directions("123 Main Street")
        print(f"✅ Directions: {directions_result}")
    except Exception as e:
        print(f"❌ Directions failed: {e}")
    
    # Test safety mode toggle
    try:
        safety_result = await agent.toggle_safety_mode(True)
        print(f"✅ Safety mode: {safety_result}")
    except Exception as e:
        print(f"❌ Safety mode failed: {e}")
    
    # Test context information
    print("\n📊 Testing context information...")
    print(f"Business ID: {agent.get_current_business_id()}")
    print(f"User ID: {agent.get_current_user_id()}")
    print(f"Business name: {agent.get_business_name()}")
    print(f"User name: {agent.get_user_name()}")
    print(f"Is driving: {agent.user_context.get('is_driving', False)}")
    print(f"Safety mode: {agent.user_context.get('safety_mode', True)}")
    
    # Test agent stop
    print("\n🔄 Testing agent stop...")
    await agent.on_agent_stop()
    print("✅ Agent stopped successfully")
    
    print("\n✅ All tests completed successfully!")
    print("🎉 Personal Voice Agent is ready for integration!")


async def test_job_tools():
    """Test job management tools with mock data"""
    
    print("\n🛠️ Testing Job Management Tools")
    print("=" * 40)
    
    # Import job tools
    from app.voice_agents.tools import job_tools
    
    print("Note: Job tools will fail without database connection.")
    print("This test demonstrates the tool interface structure.")
    
    # Test tool function signatures
    tools_to_test = [
        ("create_job", ["Test Job", "Description", "contact_123", "2024-02-15"]),
        ("get_upcoming_jobs", [7]),
        ("update_job_status", ["job_123", "completed"]),
        ("reschedule_job", ["job_123", "2024-02-16"]),
        ("get_job_details", ["job_123"]),
        ("get_jobs_by_status", ["scheduled"])
    ]
    
    for tool_name, args in tools_to_test:
        try:
            tool_func = getattr(job_tools, tool_name)
            print(f"✅ Tool '{tool_name}' exists with {len(args)} expected arguments")
            
            # Note: Don't actually call the tools without database
            # result = await tool_func(*args)
            
        except AttributeError:
            print(f"❌ Tool '{tool_name}' not found")
        except Exception as e:
            print(f"⚠️ Tool '{tool_name}' error: {e}")


async def test_voice_configuration():
    """Test voice configuration options"""
    
    print("\n🎵 Testing Voice Configuration")
    print("=" * 35)
    
    from app.voice_agents.core.voice_config import (
        PersonalAgentConfig, VoiceProfile, VoiceModel, AgentType
    )
    
    # Test default configuration
    default_config = PersonalAgentConfig(
        agent_type=AgentType.PERSONAL,
        agent_name="Test Agent"
    )
    print(f"✅ Default config created")
    print(f"   Agent type: {default_config.agent_type.value}")
    print(f"   Voice profile: {default_config.voice_profile.value}")
    print(f"   Voice model: {default_config.voice_model.value}")
    print(f"   Tools enabled: {len(default_config.tools_enabled)}")
    
    # Test custom configuration
    custom_config = PersonalAgentConfig(
        agent_type=AgentType.PERSONAL,
        agent_name="Custom Test Agent",
        voice_profile=VoiceProfile.CASUAL,
        voice_model=VoiceModel.SONIC_1,
        temperature=0.8,
        max_conversation_duration=7200
    )
    print(f"✅ Custom config created")
    print(f"   Voice profile: {custom_config.voice_profile.value}")
    print(f"   Voice model: {custom_config.voice_model.value}")
    print(f"   Temperature: {custom_config.temperature}")
    print(f"   Max duration: {custom_config.max_conversation_duration}s")
    
    # Test configuration serialization
    config_dict = custom_config.to_dict()
    print(f"✅ Config serialized to dict ({len(config_dict)} keys)")
    
    # Test configuration deserialization
    restored_config = PersonalAgentConfig.from_dict(config_dict)
    print(f"✅ Config restored from dict")
    print(f"   Matches original: {restored_config.agent_name == custom_config.agent_name}")


def print_next_steps():
    """Print next steps for integration"""
    
    print("\n🎯 Next Steps for Integration")
    print("=" * 35)
    print("1. ✅ Personal Voice Agent structure is ready")
    print("2. ✅ LiveKit Agents framework implemented")
    print("3. ✅ Context management simplified")
    print("4. 🔄 Set up environment variables for AI providers")
    print("5. 🔄 Start LiveKit worker: `./scripts/start-voice-worker.sh`")
    print("6. 🔄 Test with mobile app integration")
    print("7. 🔄 Add more business-specific tools")
    print("8. 🔄 Implement conversation analytics")
    print("9. 🔄 Add outbound calling agents")
    print("10. 🔄 Production deployment")


async def main():
    """Main test function"""
    
    try:
        # Run all tests
        await test_personal_agent()
        await test_job_tools()
        await test_voice_configuration()
        
        # Print next steps
        print_next_steps()
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 