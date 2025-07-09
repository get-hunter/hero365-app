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

# Configure logging with more detailed debug info
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add detailed startup logging
logger.info("🔧 Worker module loaded, setting up entrypoint...")


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for the voice agent worker.
    
    This function is called when a job is assigned to this worker.
    Pattern based on: https://github.com/livekit/agents/blob/main/examples/voice_agents/basic_agent.py
    
    Args:
        ctx: JobContext containing room, job info, and connection details
    """
    logger.info("🚀🚀🚀 ENTRYPOINT CALLED - Voice agent job started!")
    logger.info(f"📋 Job info: {ctx.job}")
    logger.info(f"🏠 Room info: name={ctx.room.name}, sid={ctx.room.sid}")
    logger.info(f"👤 Room participants: {len(ctx.room.remote_participants)}")
    logger.info(f"📊 Room metadata: {ctx.room.metadata}")
    
    # Step 1: Connect to the room first - This is the CRITICAL pattern from the latest SDK
    # Reference: https://docs.livekit.io/agents/quickstarts/voice-agent/
    logger.info("🔌 Attempting to connect to LiveKit room...")
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.AUDIO_ONLY)
    logger.info("✅ Connected to LiveKit room successfully")
    
    # Log initial room state with more detail
    logger.info(f"🏠 Connected to room: {ctx.room.name} (sid: {ctx.room.sid})")
    logger.info(f"👥 Current participants: {len(ctx.room.remote_participants)}")
    logger.info(f"📱 Local participant: {ctx.room.local_participant}")
    
    # Step 2: Extract agent context from room metadata
    # Our custom pattern for passing business/user context through room metadata
    business_context = None
    user_context = None
    agent_config_data = None
    
    logger.info("🔍 Parsing room metadata for agent context...")
    try:
        # The API stores agent context in room metadata
        if ctx.room.metadata:
            import json
            logger.debug(f"📋 Raw room metadata: {ctx.room.metadata}")
            room_metadata = json.loads(ctx.room.metadata)
            logger.info(f"📋 Parsed room metadata: {room_metadata}")
            
            # Extract agent context from metadata
            agent_context = room_metadata.get("agent_context", {})
            if agent_context:
                business_context = agent_context.get("business_context", {})
                user_context = agent_context.get("user_context", {})
                agent_config_data = agent_context.get("agent_config", {})
                logger.info(f"👤 Agent context loaded for user: {user_context.get('name', 'Unknown')}")
                logger.debug(f"🏢 Business context: {business_context}")
                logger.debug(f"👤 User context: {user_context}")
                logger.debug(f"⚙️ Agent config: {agent_config_data}")
            else:
                logger.warning("⚠️ No agent context found in room metadata")
        else:
            logger.warning("⚠️ No room metadata found")
            
    except Exception as e:
        logger.error(f"❌ Failed to parse room metadata: {e}")
        import traceback
        logger.debug(f"🐛 Metadata parsing traceback: {traceback.format_exc()}")
        logger.info("📝 Using default context")
    
    # Step 3: Use extracted context or fall back to defaults
    if not business_context:
        logger.info("🏢 Using default business context")
        business_context = {
            "id": "default_business",
            "name": "Hero365",
            "type": "Home services AI-native ERP",
            "capabilities": ["contract management", "invoicing", "job scheduling", "payment processing"]
        }
    
    if not user_context:
        logger.info("👤 Using default user context")
        user_context = {
            "id": "default_user",
            "name": "User",
            "preferences": {}
        }
    
    # Step 4: Create agent configuration
    logger.info("⚙️ Creating agent configuration...")
    agent_config = PersonalAgentConfig(
        agent_type=AgentType.PERSONAL,
        agent_name="Hero365 Assistant",
        voice_profile=VoiceProfile.PROFESSIONAL,
        voice_model=VoiceModel.SONIC_2,
        temperature=agent_config_data.get("temperature", 0.7) if agent_config_data else 0.7,
        max_conversation_duration=agent_config_data.get("max_duration", 3600) if agent_config_data else 3600
    )
    logger.info("✅ Agent configuration created")
    
    # Step 5: Create the PersonalVoiceAgent to get tools and prompts
    # This is our custom agent that provides business-specific tools
    logger.info("🤖 Creating PersonalVoiceAgent...")
    personal_agent = PersonalVoiceAgent(
        business_context=business_context,
        user_context=user_context,
        agent_config=agent_config
    )
    logger.info("✅ PersonalVoiceAgent created successfully")
    
    # Step 6: Create the LiveKit Agent with tools and instructions
    # Pattern from: https://github.com/livekit/agents/blob/main/examples/voice_agents/basic_agent.py
    logger.info("🧠 Creating LiveKit Agent with tools and instructions...")
    agent = Agent(
        instructions=personal_agent.get_system_prompt(),
        tools=personal_agent.get_tools()
    )
    logger.info(f"🛠️ LiveKit Agent created with {len(personal_agent.get_tools())} tools")
    
    # Step 7: Create AgentSession with STT, LLM, TTS pipeline
    # STT-LLM-TTS pipeline pattern from the latest SDK examples
    # Reference: https://docs.livekit.io/agents/quickstarts/voice-agent/
    logger.info("🎙️ Setting up STT, LLM, TTS pipeline...")
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(voice="79a125e8-cd45-4c13-8a67-188112f4dd22")  # Professional male voice
    )
    logger.info("✅ Pipeline created successfully")
    
    # Step 8: Start the session with the agent
    # This is the standard pattern from the latest SDK
    logger.info("🚀 Starting agent session...")
    await session.start(agent=agent, room=ctx.room)
    logger.info("🎙️ Agent session started successfully")
    
    # Step 9: Generate initial greeting when user joins
    # Generate a personalized greeting based on the business and user context
    business_name = business_context.get("name", "Hero365")
    user_name = user_context.get("name", "there")
    
    logger.info(f"💬 Generating greeting for {user_name} from {business_name}...")
    await session.generate_reply(
        instructions=f"Greet {user_name} politely and introduce yourself as the {business_name} AI assistant. Ask how you can help them today with their business operations."
    )
    
    logger.info("💬 Initial greeting generated successfully")
    logger.info("🎯 Worker entrypoint completed successfully - agent is now active!")
    
    # The session will continue running until the connection is closed
    # or the user leaves the room


def main():
    """
    Main function to run the worker.
    
    Pattern reference: https://github.com/livekit/agents/blob/main/examples/voice_agents/basic_agent.py
    CLI usage: https://docs.livekit.io/agents/overview/
    """
    
    logger.info("🚀 Starting main() function...")
    
    # Step 1: Verify required environment variables
    # These are the standard environment variables for LiveKit agents
    required_vars = [
        "LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET",
        "OPENAI_API_KEY", "DEEPGRAM_API_KEY", "CARTESIA_API_KEY"
    ]
    
    logger.info("🔐 Checking environment variables...")
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            logger.debug(f"✅ {var}: {'*' * min(len(value), 10)}...")
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    logger.info("✅ All required environment variables are set")
    
    # Log LiveKit connection details
    logger.info(f"🌐 LiveKit URL: {os.getenv('LIVEKIT_URL')}")
    logger.info(f"🔑 LiveKit API Key: {os.getenv('LIVEKIT_API_KEY')[:10]}...")
    
    # Step 2: Run the worker with the entrypoint function
    # This is the standard CLI pattern from the latest SDK version 1.1.5
    # Reference: https://github.com/livekit/agents/blob/main/examples/voice_agents/basic_agent.py
    logger.info("🚀 Starting LiveKit worker with automatic room joining...")
    
    # Create worker options for automatic room assignment
    # Pattern from: https://github.com/livekit/agents/blob/main/examples/voice_agents/basic_agent.py
    worker_options = WorkerOptions(
        entrypoint_fnc=entrypoint,
        # The worker will automatically be assigned to rooms when they are created
        # No need to specify specific rooms - it will handle all rooms by default
    )
    
    logger.info(f"🔧 Worker options created: {worker_options}")
    logger.info("⏳ Starting CLI app - this will register the worker and wait for jobs...")
    
    # Run the worker - this will start the agent and wait for room assignments
    cli.run_app(worker_options)


if __name__ == "__main__":
    # Entry point for the worker
    # Run with: python worker.py start
    # CLI modes: console, dev, start
    # Reference: https://docs.livekit.io/agents/overview/
    logger.info("🎬 Worker script starting...")
    main() 