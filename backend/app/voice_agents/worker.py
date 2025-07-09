#!/usr/bin/env python3

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

import livekit.agents as agents
from livekit.agents import JobContext, WorkerOptions, cli, Agent, AgentSession
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


class Hero365Agent(Agent):
    """LiveKit Agent wrapper for Hero365 PersonalVoiceAgent"""
    
    def __init__(self, business_context: dict, user_context: dict, agent_config: PersonalAgentConfig):
        # Create our custom agent to get tools and prompts
        self.personal_agent = PersonalVoiceAgent(
            business_context=business_context,
            user_context=user_context,
            agent_config=agent_config
        )
        
        # Initialize LiveKit Agent with tools and instructions
        super().__init__(
            instructions=self.personal_agent.get_system_prompt(),
            tools=self.personal_agent.get_tools()
        )
        
        logger.info("🤖 Hero365Agent created successfully")


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for the voice agent worker.
    This function is called when a job is assigned to this worker.
    """
    logger.info("🚀 Starting voice agent entrypoint")
    logger.info(f"🏠 Room name: {ctx.room.name}")
    logger.info(f"📋 Job metadata: {ctx.job.metadata}")
    
    # Connect to the room
    await ctx.connect()
    logger.info("✅ Connected to room")
    
    # Extract agent context from room metadata
    business_context = None
    user_context = None
    agent_config_data = None
    
    try:
        # The API stores agent context in room metadata
        import json
        room_metadata = json.loads(ctx.room.metadata) if ctx.room.metadata else {}
        logger.info(f"🔍 Room metadata: {room_metadata}")
        
        # Extract agent context from metadata
        agent_context = room_metadata.get("agent_context", {})
        if agent_context:
            business_context = agent_context.get("business_context", {})
            user_context = agent_context.get("user_context", {})
            agent_config_data = agent_context.get("agent_config", {})
            logger.info(f"✅ Extracted agent context from room metadata")
            logger.info(f"🏢 Business: {business_context.get('name', 'Unknown')}")
            logger.info(f"👤 User: {user_context.get('name', 'Unknown')}")
        else:
            logger.warning("⚠️ No agent context found in room metadata, using defaults")
            
    except Exception as e:
        logger.error(f"❌ Failed to parse room metadata: {e}")
        logger.info("🔄 Using default context")
    
    # Use extracted context or fall back to defaults
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
    
    # Create agent configuration
    agent_config = PersonalAgentConfig(
        agent_type=AgentType.PERSONAL,
        agent_name="Hero365 Assistant",
        voice_profile=VoiceProfile.PROFESSIONAL,
        voice_model=VoiceModel.SONIC_2,
        temperature=agent_config_data.get("temperature", 0.7) if agent_config_data else 0.7,
        max_conversation_duration=agent_config_data.get("max_duration", 3600) if agent_config_data else 3600
    )
    
    # Create the Hero365Agent (LiveKit Agent wrapper)
    logger.info("🤖 Creating Hero365Agent with extracted context")
    agent = Hero365Agent(
        business_context=business_context,
        user_context=user_context,
        agent_config=agent_config
    )
    
    # Create AgentSession with STT, LLM, TTS
    logger.info("🎙️ Creating AgentSession")
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(voice="79a125e8-cd45-4c13-8a67-188112f4dd22")  # Professional male voice
    )
    
    # Start the session with the agent
    logger.info("▶️ Starting AgentSession")
    await session.start(agent=agent, room=ctx.room)
    
    # Generate initial greeting
    logger.info("💬 Generating initial greeting")
    await session.generate_reply(
        instructions="Greet the user politely and ask how you can help them today with their Hero365 business."
    )
    
    logger.info("✅ Hero365Agent session started successfully")


def main():
    """Main function to run the worker"""
    
    # Log environment variable status
    logger.info("🔍 Checking environment variables...")
    
    required_vars = [
        "LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET",
        "OPENAI_API_KEY", "DEEPGRAM_API_KEY", "CARTESIA_API_KEY"
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"✅ {var}: Available")
        else:
            logger.warning(f"❌ {var}: Not set")
    
    # Create worker options for automatic dispatch
    # Removing agent_name enables automatic dispatch - worker will join rooms automatically
    worker_options = WorkerOptions(
        entrypoint_fnc=entrypoint
    )
    
    # Run the worker
    logger.info("🏃 Starting LiveKit worker with automatic dispatch...")
    cli.run_app(worker_options)


if __name__ == "__main__":
    main() 