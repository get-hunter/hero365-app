#!/usr/bin/env python3

"""
Hero365 Voice Agent Worker

IMPORTANT: Always check the latest LiveKit agents SDK documentation and examples
before making changes to this file:
- GitHub Repository: https://github.com/livekit/agents
- Documentation: https://docs.livekit.io/agents/
- Latest Examples: https://github.com/livekit/agents/tree/main/examples

The LiveKit agents SDK is rapidly evolving. Always reference the latest patterns
in the repository to ensure compatibility and avoid breaking changes.

Current SDK Version: 1.1.5
Last Updated: 2025-01-09
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent.parent / "environments" / ".env")

# Load environment variables from the configuration
from app.core.config import settings

# Import LiveKit agents SDK components
# Pattern reference: https://github.com/livekit/agents/blob/main/examples/voice_agents/basic_agent.py
import livekit.agents as agents
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents import Agent, AgentSession
from livekit.plugins import silero, openai, deepgram, cartesia

# Import our PersonalVoiceAgent for getting tools and prompts
from app.voice_agents.personal.personal_agent import PersonalVoiceAgent
from app.voice_agents.core.voice_config import PersonalAgentConfig
from app.voice_agents.core.voice_config import AgentType, VoiceProfile, VoiceModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for the voice agent worker.
    
    This function is called when a job is assigned to this worker.
    Pattern based on: https://github.com/livekit/agents/blob/main/examples/voice_agents/basic_agent.py
    
    Args:
        ctx: JobContext containing room, job info, and connection details
    """
    logger.info(f"🚀 Voice agent job started for room: {ctx.room.name}")
    
    # Step 1: Connect to the room first
    # This is the standard pattern from the latest SDK examples
    await ctx.connect()
    logger.info("✅ Connected to LiveKit room successfully")
    
    # Step 2: Extract agent context from room metadata
    # Our custom pattern for passing business/user context through room metadata
    business_context = None
    user_context = None
    agent_config_data = None
    
    try:
        # The API stores agent context in room metadata
        if ctx.room.metadata:
            import json
            room_metadata = json.loads(ctx.room.metadata)
            logger.info(f"📋 Room metadata: {room_metadata}")
            
            # Extract agent context from metadata
            agent_context = room_metadata.get("agent_context", {})
            if agent_context:
                business_context = agent_context.get("business_context", {})
                user_context = agent_context.get("user_context", {})
                agent_config_data = agent_context.get("agent_config", {})
                logger.info(f"👤 Agent context loaded for user: {user_context.get('name', 'Unknown')}")
            else:
                logger.warning("⚠️ No agent context found in room metadata")
        else:
            logger.warning("⚠️ No room metadata found")
            
    except Exception as e:
        logger.error(f"❌ Failed to parse room metadata: {e}")
        logger.info("📝 Using default context")
    
    # Step 3: Use extracted context or fall back to defaults
    if not business_context:
        business_context = {
            "id": "default_business",
            "name": "Hero365",
            "type": "Home services AI-native ERP",
            "capabilities": ["contract management", "invoicing", "job scheduling", "payment processing"]
        }
    
    if not user_context:
        user_context = {
            "id": "default_user",
            "name": "User",
            "preferences": {}
        }
    
    # Step 4: Create agent configuration
    agent_config = PersonalAgentConfig(
        agent_type=AgentType.PERSONAL,
        agent_name="Hero365 Assistant",
        voice_profile=VoiceProfile.PROFESSIONAL,
        voice_model=VoiceModel.SONIC_2,
        temperature=agent_config_data.get("temperature", 0.7) if agent_config_data else 0.7,
        max_conversation_duration=agent_config_data.get("max_duration", 3600) if agent_config_data else 3600
    )
    
    # Step 5: Create the PersonalVoiceAgent to get tools and prompts
    # This is our custom agent that provides business-specific tools
    personal_agent = PersonalVoiceAgent(
        business_context=business_context,
        user_context=user_context,
        agent_config=agent_config
    )
    
    # Step 6: Create the LiveKit Agent with tools and instructions
    # Pattern from: https://github.com/livekit/agents/blob/main/examples/voice_agents/basic_agent.py
    agent = Agent(
        instructions=personal_agent.get_system_prompt(),
        tools=personal_agent.get_tools()
    )
    
    logger.info("🤖 Hero365Agent initialized successfully")
    
    # Step 7: Create AgentSession with STT, LLM, TTS pipeline
    # STT-LLM-TTS pipeline pattern from the latest SDK examples
    # Reference: https://docs.livekit.io/agents/quickstarts/voice-agent/
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(voice="79a125e8-cd45-4c13-8a67-188112f4dd22")  # Professional male voice
    )
    
    # Step 8: Start the session with the agent
    # This is the standard pattern from the latest SDK
    await session.start(agent=agent, room=ctx.room)
    logger.info("🎙️ Agent session started successfully")
    
    # Step 9: Generate initial greeting
    # Generate a personalized greeting based on the business and user context
    business_name = business_context.get("name", "Hero365")
    user_name = user_context.get("name", "there")
    
    await session.generate_reply(
        instructions=f"Greet {user_name} politely and introduce yourself as the {business_name} AI assistant. Ask how you can help them today with their business operations."
    )
    
    logger.info("💬 Initial greeting generated")


def main():
    """
    Main function to run the worker.
    
    Pattern reference: https://github.com/livekit/agents/blob/main/examples/voice_agents/basic_agent.py
    CLI usage: https://docs.livekit.io/agents/overview/
    """
    
    # Step 1: Verify required environment variables
    # These are the standard environment variables for LiveKit agents
    required_vars = [
        "LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET",
        "OPENAI_API_KEY", "DEEPGRAM_API_KEY", "CARTESIA_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    logger.info("✅ All required environment variables are set")
    
    # Step 2: Run the worker with the entrypoint function
    # This is the standard CLI pattern from the latest SDK version 1.1.5
    # Reference: https://github.com/livekit/agents/blob/main/examples/voice_agents/basic_agent.py
    logger.info("🚀 Starting LiveKit worker with automatic room joining...")
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))


if __name__ == "__main__":
    # Entry point for the worker
    # Run with: python worker.py start
    # CLI modes: console, dev, start
    # Reference: https://docs.livekit.io/agents/overview/
    main() 