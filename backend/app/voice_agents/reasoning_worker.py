"""
LiveKit Reasoning Voice Agent Worker for Hero365

This module provides a dedicated worker process for handling reasoning-enabled 
voice agent sessions using the LiveKit Agents framework.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from .env file
from dotenv import load_dotenv

# Calculate path to environments directory
current_dir = Path(__file__).parent  # app/voice_agents/
app_dir = current_dir.parent  # app/
backend_dir = app_dir.parent  # backend/
project_root = backend_dir.parent  # project root
env_file = project_root / "environments" / ".env"

# Load environment variables
if env_file.exists():
    load_dotenv(env_file)
    logging.info(f"Loaded environment variables from {env_file}")
else:
    logging.warning(f"Environment file not found at {env_file}")

from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.agents.voice import MetricsCollectedEvent
from livekit.agents.metrics import usage_collector
from livekit.plugins import deepgram, openai, cartesia, silero

from app.voice_agents.personal.reasoning_personal_agent import ReasoningPersonalVoiceAgent
from app.voice_agents.core.voice_config import PersonalAgentConfig, DEFAULT_PERSONAL_CONFIG

logger = logging.getLogger(__name__)


class Hero365ReasoningAgent(Agent):
    """LiveKit Agent wrapper for Hero365 ReasoningPersonalVoiceAgent"""
    
    def __init__(self, 
                 business_context: dict, 
                 user_context: dict, 
                 agent_config: PersonalAgentConfig,
                 max_reasoning_iterations: int = 3):
        
        # Create reasoning-enabled agent
        self.reasoning_agent = ReasoningPersonalVoiceAgent(
            business_context=business_context,
            user_context=user_context,
            config=agent_config,
            max_reasoning_iterations=max_reasoning_iterations
        )
        
        logger.info(f"Initialized Hero365ReasoningAgent with {max_reasoning_iterations} max iterations")
        
        # Initialize LiveKit Agent with tools and instructions
        super().__init__(
            instructions=self.reasoning_agent.get_system_prompt(),
            tools=self.reasoning_agent.get_tools()
        )
        
        logger.info("Hero365ReasoningAgent initialized successfully")


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for the reasoning voice agent worker.
    This function is called when a job is assigned to this worker.
    """
    logger.info(f"Reasoning voice agent starting for room: {ctx.room.name}")
    
    # Connect to the room
    await ctx.connect()
    logger.info("Connected to room successfully")
    
    # Extract agent context from room metadata
    room_metadata = ctx.room.metadata
    business_context = {
        "name": "Hero365 Demo", 
        "services": ["plumbing", "electrical", "HVAC", "handyman"],
        "capabilities": ["reasoning", "planning", "multi-tool_coordination"]
    }
    user_context = {
        "name": "User", 
        "safety_mode": True,
        "reasoning_preferences": {
            "explain_reasoning": True,
            "show_plan": True,
            "confirm_complex_actions": True
        }
    }
    agent_config_data = None
    
    try:
        if room_metadata:
            import json
            metadata = json.loads(room_metadata)
            business_context = metadata.get("business_context", business_context)
            user_context = metadata.get("user_context", user_context)
            agent_config_data = metadata.get("agent_config", {})
            
            logger.info(f"Loaded contexts from room metadata: business={business_context.get('name')}")
    except Exception as e:
        logger.warning(f"Failed to parse room metadata: {e}")
    
    # Create agent configuration
    agent_config = DEFAULT_PERSONAL_CONFIG
    if agent_config_data:
        try:
            # Update configuration with provided data
            for key, value in agent_config_data.items():
                if hasattr(agent_config, key):
                    setattr(agent_config, key, value)
        except Exception as e:
            logger.warning(f"Failed to apply agent configuration: {e}")
    
    # Get reasoning configuration from environment or room metadata
    max_reasoning_iterations = int(os.getenv("MAX_REASONING_ITERATIONS", "3"))
    
    # Override with room metadata if available
    if room_metadata:
        try:
            import json
            metadata = json.loads(room_metadata)
            max_reasoning_iterations = metadata.get("max_reasoning_iterations", max_reasoning_iterations)
        except Exception as e:
            logger.warning(f"Failed to parse reasoning configuration: {e}")
    
    # Create Hero365ReasoningAgent
    agent = Hero365ReasoningAgent(
        business_context=business_context,
        user_context=user_context,
        agent_config=agent_config,
        max_reasoning_iterations=max_reasoning_iterations
    )
    
    # Create AgentSession with STT, LLM, TTS
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(voice="79a125e8-cd45-4c13-8a67-188112f4dd22")  # Professional male voice
    )
    
    # Set up metrics collection
    usage_collector_instance = usage_collector.UsageCollector()
    
    @session.on("metrics_collected")
    def on_metrics_collected(event: MetricsCollectedEvent):
        usage_collector_instance.collect(event.metrics)
    
    # Start the session with the agent
    await session.start(agent=agent, room=ctx.room)
    
    # Generate initial reasoning-focused greeting
    business_name = business_context.get("name", "your business")
    greeting = f"""Hello! I'm Hero365 AI with advanced reasoning capabilities. 

I can help you with complex business tasks by breaking them down into logical steps. I use a Plan-Act-Verify approach to handle multi-step workflows efficiently.

Some examples of what I can do:
• Create projects with multiple jobs and estimates in one request
• Manage overdue invoices and create follow-up tasks
• Handle inventory management and automatic reordering
• Process complex scheduling and resource allocation

I'll explain my reasoning process and you can ask me to revise plans at any time. How can I assist you today?"""
    
    await session.generate_reply(
        instructions=f"Greet the user with this message: '{greeting}'"
    )
    
    logger.info(f"Hero365ReasoningAgent session started successfully (max iterations: {max_reasoning_iterations})")
    
    # Keep the session alive
    try:
        await session.wait_for_completion()
    except Exception as e:
        logger.error(f"Session error: {e}")
    finally:
        # Log final usage statistics
        summary = usage_collector_instance.get_summary()
        logger.info(f"Reasoning session completed. Usage summary: {summary}")


def main():
    """Main function to run the reasoning worker"""
    
    # Verify required environment variables
    required_vars = [
        "LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET",
        "OPENAI_API_KEY", "DEEPGRAM_API_KEY", "CARTESIA_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please ensure your environments/.env file contains all required API keys")
        logger.error(f"Environment file path: {env_file}")
        sys.exit(1)
    
    # Reasoning-specific configuration
    max_iterations = int(os.getenv("MAX_REASONING_ITERATIONS", "3"))
    
    logger.info("=" * 60)
    logger.info("🧠 Hero365 Reasoning Voice Agent Worker Starting")
    logger.info("=" * 60)
    logger.info(f"Max reasoning iterations: {max_iterations}")
    logger.info("Features enabled:")
    logger.info("  ✅ Plan-Act-Verify reasoning loop")
    logger.info("  ✅ Multi-tool coordination")
    logger.info("  ✅ Reasoning transparency")
    logger.info("  ✅ Plan revision capabilities")
    logger.info("  ✅ Complex workflow handling")
    logger.info("=" * 60)
    
    # Run the worker
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))


if __name__ == "__main__":
    main() 