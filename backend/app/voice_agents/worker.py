"""
LiveKit Agent Worker for Hero365

This module implements the LiveKit Agents framework worker that handles
voice agent sessions for Hero365 personal and outbound agents.

Usage:
    python -m app.voice_agents.worker dev    # Development mode
    python -m app.voice_agents.worker start  # Production mode
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../..', 'environments', 'production.env'))

from livekit import agents
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger(__name__)


class Hero365VoiceAgent(Agent):
    """Hero365 Voice Agent for personal assistance and business automation"""
    
    def __init__(self, agent_config: Dict[str, Any]) -> None:
        # Extract configuration
        instructions = agent_config.get("instructions", "You are Hero365, an AI assistant for home services contractors.")
        
        super().__init__(instructions=instructions)
        
        self.agent_config = agent_config
        self.business_context = agent_config.get("business_context", {})
        self.user_context = agent_config.get("user_context", {})
        
        logger.info(f"🤖 Hero365 agent initialized for user: {self.user_context.get('name', 'Unknown')}")
    
    async def on_enter(self) -> None:
        """Called when the agent enters the session"""
        logger.info(f"🚀 Hero365 agent entering session")
        
        # Generate initial greeting
        user_name = self.user_context.get("name", "")
        is_driving = self.user_context.get("is_driving", False)
        
        if is_driving:
            greeting = f"Hi {user_name}! I'm Hero365, your AI assistant. I see you're driving, so I'll keep things hands-free. How can I help you today?"
        else:
            greeting = f"Hello {user_name}! I'm Hero365, your AI assistant for managing your home services business. What can I help you with today?"
        
        # Generate the initial greeting
        await self.session.generate_reply(instructions=f"Say this greeting: '{greeting}'")
    
    async def on_exit(self) -> None:
        """Called when the agent exits the session"""
        logger.info(f"👋 Hero365 agent exiting session")


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for Hero365 voice agents
    
    This function is called when a user joins a LiveKit room and needs
    to be connected to a Hero365 voice agent.
    """
    logger.info(f"🚀 ENTRYPOINT CALLED! Hero365 agent connecting to room: {ctx.room.name}")
    logger.info(f"🔍 Job context: {ctx.job}")
    logger.info(f"🔍 Room info: {ctx.room}")
    
    try:
        # Connect to the room first
        logger.info(f"🔗 Connecting to room...")
        await ctx.connect()
        logger.info(f"✅ Connected to room {ctx.room.name}")
        
        # Check room participants after connecting
        logger.info(f"🔍 Room participants after connect: {len(ctx.room.remote_participants)}")
        
        # Extract agent configuration from room name or metadata
        agent_config = {
            "instructions": "You are Hero365, an AI assistant for home services contractors. You help manage jobs, schedules, estimates, invoices, and customer communications.",
            "business_context": {
                "name": "Your Business",
                "type": "Home Services",
                "services": []
            },
            "user_context": {
                "name": "User",
                "is_driving": False,
                "safety_mode": False
            }
        }
        
        # Try to extract configuration from job metadata if available
        if hasattr(ctx.job, 'metadata') and ctx.job.metadata:
            try:
                import json
                metadata = json.loads(ctx.job.metadata) if isinstance(ctx.job.metadata, str) else ctx.job.metadata
                if isinstance(metadata, dict):
                    agent_config.update(metadata)
                    logger.info(f"🔍 Updated agent config from metadata: {metadata}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse job metadata: {e}")
        
        logger.info(f"🔍 Final agent config: {agent_config}")
        
        # Create the AgentSession with all necessary components
        session = AgentSession(
            stt=deepgram.STT(model="nova-3", language="multi"),
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=cartesia.TTS(model="sonic-2", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),
            vad=silero.VAD.load(),
            turn_detection=MultilingualModel(),
        )
        
        # Create the Hero365 agent
        agent = Hero365VoiceAgent(agent_config)
        
        # Start the session
        logger.info(f"🎙️ Starting Hero365 agent session...")
        await session.start(
            agent=agent,
            room=ctx.room,
        )
        
        logger.info(f"✅ Hero365 agent session started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error in Hero365 agent entrypoint: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    logger.info("🎙️ Starting Hero365 LiveKit Agent Worker...")
    
    # Verify environment variables
    required_vars = ['LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET', 'OPENAI_API_KEY', 'DEEPGRAM_API_KEY', 'CARTESIA_API_KEY']
    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"❌ Missing required environment variable: {var}")
            exit(1)
    
    logger.info("✅ All required environment variables are set")
    logger.info(f"🔗 Connecting to LiveKit server: {os.getenv('LIVEKIT_URL')}")
    
    # Run the worker using CLI
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            # No agent_name = automatic dispatch for web/mobile clients
        )
    ) 