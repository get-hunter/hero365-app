"""
LiveKit Agent Worker for Hero365

This module implements the LiveKit Agents framework worker that handles
voice agent sessions for Hero365 personal and outbound agents.
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(__file__), '../../..', 'environments', 'production.env'))

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger(__name__)

# Global storage for agent contexts
agent_contexts: Dict[str, Dict[str, Any]] = {}


class Hero365Agent(Agent):
    """Hero365 AI Assistant Agent"""
    
    def __init__(self, business_context: Dict[str, Any] = None, user_context: Dict[str, Any] = None):
        business_name = business_context.get("name", "Hero365") if business_context else "Hero365"
        user_name = user_context.get("name", "User") if user_context else "User"
        
        # Check if user is driving for safety-focused prompts
        is_driving = user_context.get("is_driving", False) if user_context else False
        safety_mode = user_context.get("safety_mode", True) if user_context else True
        
        instructions = f"""You are Hero365's personal AI assistant for {business_name}.

USER CONTEXT:
- Name: {user_name}
- Business: {business_name}
- Current Status: {"Driving (Safety Mode)" if is_driving and safety_mode else "Available"}

CAPABILITIES:
You can help with:
- Job management (create, update, reschedule, check status)
- Upcoming job schedules and details
- Quick business information
- Time and reminder services
- Navigation assistance

COMMUNICATION STYLE:
- Be concise and professional
- Use hands-free friendly responses
- Provide clear confirmations for actions
- Ask clarifying questions when needed"""

        if is_driving and safety_mode:
            instructions += """

SAFETY PROTOCOLS (USER IS DRIVING):
- Keep ALL responses under 20 words when possible
- Prioritize voice-only interactions
- Suggest pulling over for complex tasks
- Use simple yes/no confirmations
- Avoid detailed information unless essential
- Focus on immediate, actionable items"""
        
        instructions += """

RESPONSE FORMAT:
- Speak naturally as if talking to a colleague
- Use "I can help you with..." for capabilities
- Confirm actions before executing
- Provide brief status updates after actions
- Ask "Is there anything else?" to continue helping

Remember: You represent {business_name} professionally while being helpful and efficient."""
        
        super().__init__(instructions=instructions)
        self.business_context = business_context or {"name": "Hero365", "id": "default"}
        self.user_context = user_context or {"name": "User", "id": "default"}
        
        logger.info(f"Initialized Hero365Agent for {business_name}")


async def entrypoint(ctx: agents.JobContext):
    """
    Main entrypoint for Hero365 voice agents
    
    This function is called when a user joins a LiveKit room and needs
    to be connected to a Hero365 voice agent.
    """
    logger.info(f"🚀 Hero365 agent connecting to room: {ctx.room.name}")
    
    # Extract agent configuration from room metadata or name
    agent_id = ctx.room.name.replace("voice-session-", "") if ctx.room.name.startswith("voice-session-") else "default"
    logger.info(f"🔍 Extracted agent ID: {agent_id}")
    
    # Get agent context if available
    context = agent_contexts.get(agent_id, {})
    business_context = context.get("business_context", {"name": "Hero365", "id": "default"})
    user_context = context.get("user_context", {"name": "User", "id": "default"})
    
    logger.info(f"🏢 Business context: {business_context.get('name', 'Unknown')}")
    logger.info(f"👤 User context: {user_context.get('name', 'Unknown')}")
    
    # Create the agent session with AI providers
    session = AgentSession(
        stt=deepgram.STT(model="nova-2", language="en"),
        llm=openai.LLM(model="gpt-4o-mini", temperature=0.7),
        tts=cartesia.TTS(
            model="sonic-2", 
            voice="a0e99841-438c-4a64-b679-ae501e7d6091"  # Friendly voice
        ),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )
    
    # Configure room input options with noise cancellation
    room_input_options = RoomInputOptions()
    try:
        room_input_options.noise_cancellation = noise_cancellation.BVC()
        logger.info("✅ Noise cancellation enabled")
    except Exception as e:
        logger.warning(f"Could not configure noise cancellation: {e}")
    
    # Start the agent session
    logger.info(f"🎤 Starting agent session...")
    await session.start(
        room=ctx.room,
        agent=Hero365Agent(business_context=business_context, user_context=user_context),
        room_input_options=room_input_options,
    )
    
    # Connect to the room
    logger.info(f"🔗 Connecting to room {ctx.room.name}...")
    await ctx.connect()
    logger.info(f"✅ Connected to room {ctx.room.name}")
    
    # Generate personalized greeting
    business_name = business_context.get("name", "Hero365")
    user_name = user_context.get("name", "User")
    is_driving = user_context.get("is_driving", False)
    
    # Check time of day for appropriate greeting
    hour = datetime.now().hour
    if hour < 12:
        time_greeting = "Good morning"
    elif hour < 17:
        time_greeting = "Good afternoon"
    else:
        time_greeting = "Good evening"
    
    if is_driving:
        greeting_instructions = f"{time_greeting}, {user_name}! I'm your {business_name} assistant. Drive safely - I'll keep responses brief. How can I help you today?"
    else:
        greeting_instructions = f"{time_greeting}, {user_name}! I'm your {business_name} assistant. How can I help you today?"
    
    # Send greeting through the session
    logger.info(f"👋 Sending greeting: {greeting_instructions}")
    await session.generate_reply(instructions=greeting_instructions)
    
    logger.info(f"🎉 Hero365 agent {agent_id} started successfully in room {ctx.room.name}")


def register_agent_context(agent_id: str, context: Dict[str, Any]):
    """Register agent context for use in entrypoint"""
    agent_contexts[agent_id] = context
    logger.info(f"📋 Registered context for agent {agent_id}")


def main():
    """Main entry point for CLI execution"""
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🎙️ Starting Hero365 LiveKit Agent Worker...")
    
    # Check required environment variables
    required_vars = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY", 
        "LIVEKIT_API_SECRET",
        "OPENAI_API_KEY",
        "DEEPGRAM_API_KEY",
        "CARTESIA_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    logger.info("✅ All required environment variables are set")
    logger.info(f"🔗 Connecting to LiveKit server: {os.getenv('LIVEKIT_URL')}")
    
    # Use LiveKit CLI to run the worker
    try:
        agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
    except Exception as e:
        logger.error(f"❌ Failed to start LiveKit agent worker: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 