#!/usr/bin/env python3

"""
Simple Test Worker for LiveKit Agents 1.1.5
This is a minimal implementation to test basic connectivity.
"""

import logging
import os
import sys
from pathlib import Path

# Add parent directory for app imports
sys.path.append(str(Path(__file__).parent.parent))

# Load environment configuration
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent.parent / "environments" / ".env")

# LiveKit Agents SDK imports
import livekit.agents as agents
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents import Agent, AgentSession
from livekit.plugins import silero, openai, deepgram, cartesia

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext):
    """
    Simple agent entrypoint - minimal implementation for testing.
    """
    logger.info("🎯 SIMPLE AGENT ENTRYPOINT CALLED!")
    logger.info(f"🚀 Agent starting for room: {ctx.room.name}")
    logger.info(f"🔍 Room participants: {len(ctx.room.remote_participants)}")
    
    # Connect to room with audio subscription
    logger.info("🔌 Connecting to LiveKit room...")
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.AUDIO_ONLY)
    logger.info("✅ Connected to LiveKit room")
    
    # Wait for participant to join
    participant = await ctx.wait_for_participant()
    logger.info(f"👤 Participant joined: {participant.identity}")
    
    # Create simple agent with basic instructions
    agent = Agent(
        instructions=(
            "You are a helpful AI assistant. "
            "Be friendly and concise in your responses. "
            "You can help with general questions and have a conversation."
        )
    )
    
    # Create AgentSession with STT-LLM-TTS pipeline
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(
            model="sonic-2",
            voice="79a125e8-cd45-4c13-8a67-188112f4dd22"  # Professional voice
        )
    )
    
    # Start the session
    logger.info("🎙️ Starting agent session...")
    await session.start(agent=agent, room=ctx.room)
    logger.info("✅ Agent session started successfully")
    
    # Generate simple greeting
    await session.generate_reply(
        instructions="Greet the user warmly and introduce yourself as a helpful AI assistant. Ask how you can help them today."
    )
    
    logger.info("💬 Simple agent ready and greeted user")


def main():
    """Main worker entry point."""
    logger.info("🚀 Starting Simple Test Worker")
    
    # Verify required environment variables
    required_vars = [
        "LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET",
        "OPENAI_API_KEY", "DEEPGRAM_API_KEY", "CARTESIA_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    logger.info("✅ Environment variables validated")
    
    # Debug LiveKit connection
    logger.info(f"🔍 LIVEKIT_URL: {os.getenv('LIVEKIT_URL')}")
    logger.info(f"🔍 LIVEKIT_API_KEY: {os.getenv('LIVEKIT_API_KEY', 'NOT_SET')[:10]}...")
    
    # Configure worker with automatic dispatch
    worker_options = WorkerOptions(entrypoint_fnc=entrypoint)
    
    logger.info("🎯 Simple worker configured for automatic room dispatch")
    logger.info("⏳ Waiting for room assignments...")
    
    # Start the worker
    cli.run_app(worker_options)


if __name__ == "__main__":
    main() 