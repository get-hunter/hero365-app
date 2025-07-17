"""
Hero365 LiveKit Worker - Modern Agent implementation for voice sessions
Uses LiveKit Agents 1.0 pattern with Agent and AgentSession for automatic room joining
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
from livekit import agents, rtc
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, openai, cartesia, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from .config import LiveKitConfig
from .hero365_triage_agent import Hero365TriageAgent
from .context_management import get_context_manager
from .monitoring.metrics import get_metrics

logger = logging.getLogger(__name__)

class Hero365Agent(Agent):
    """Hero365 Voice Agent using modern LiveKit Agents 1.0 pattern"""
    
    def __init__(self):
        super().__init__(
            instructions="You are Hero365, an AI assistant specialized in helping home-services contractors and independent professionals manage their business operations. You can help with contact management, job scheduling, estimate creation, invoice management, and business analytics. You're knowledgeable about construction, plumbing, electrical, HVAC, and general contracting work."
        )
        self.config = LiveKitConfig()
        self.session_id = None
        self.user_id = None
        self.business_id = None
        self.context_manager = None
        self.metrics = None
        
    async def on_enter(self):
        """Called when the agent enters a room"""
        logger.info(f"🎯 Hero365 Agent entering room")
        
        # Initialize context manager and metrics
        self.context_manager = await get_context_manager()
        self.metrics = await get_metrics()
        
        # Set default session info for now
        self.session_id = "voice_session_default"
        self.user_id = None
        self.business_id = None
        
        # Initialize session context with defaults
        if self.context_manager:
            await self.context_manager.initialize_session(
                self.session_id, self.user_id, self.business_id
            )
        
        if self.metrics:
            await self.metrics.start_session(self.session_id, self.user_id, self.business_id)
        
        # Generate initial greeting
        logger.info("🎤 Hero365 Agent ready to handle voice conversations")
        
    async def _extract_session_info(self):
        """Extract session information from room metadata - placeholder for future implementation"""
        # TODO: Implement room metadata extraction when we understand the correct API
        # For now, we'll use defaults
        self.session_id = "voice_session_default"
        self.user_id = None
        self.business_id = None

async def entrypoint(ctx: JobContext):
    """Main entrypoint for Hero365 voice agents"""
    logger.info(f"🚀 Hero365 Voice Agent starting for job: {ctx.job.id}")
    
    # Connect to the room first
    await ctx.connect()
    logger.info(f"✅ Connected to room: {ctx.room.name}")
    
    # Get voice pipeline configuration
    config = LiveKitConfig()
    
    # Create agent session with optimized voice pipeline
    session = AgentSession(
        # Speech-to-Text with industry-specific keywords
        stt=deepgram.STT(
            model="nova-2",
            language="en-US",
            keywords=[
                ("estimate", 1.5), ("invoice", 1.5), ("job", 1.5), ("contractor", 1.5), 
                ("plumbing", 1.5), ("electrical", 1.5), ("HVAC", 1.5), ("construction", 1.5), 
                ("repair", 1.5), ("install", 1.5), ("maintenance", 1.5), ("quote", 1.5), 
                ("appointment", 1.5), ("schedule", 1.5), ("customer", 1.5), ("service", 1.5), 
                ("technician", 1.5), ("project", 1.5), ("materials", 1.5), ("labor", 1.5),
                ("permit", 1.5), ("inspection", 1.5), ("warranty", 1.5), ("emergency", 1.5), 
                ("equipment", 1.5)
            ],
            interim_results=True,
            smart_format=True,
        ),
        
        # Language Model optimized for business conversations
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7,
        ),
        
        # Text-to-Speech with professional voice
        tts=cartesia.TTS(
            model="sonic-2",
            voice="a0e99841-438c-4a64-b679-ae501e7d6091",  # Professional male voice
            language="en"
        ),
        
        # Voice Activity Detection
        vad=silero.VAD.load(),
        
        # Turn detection optimized for professional conversations
        turn_detection=MultilingualModel(),
    )
    
    # Create Hero365 agent instance
    agent = Hero365Agent()
    
    # Start the session - this will automatically join the room and begin processing
    await session.start(
        room=ctx.room,
        agent=agent,
    )
    
    logger.info(f"✅ Hero365 Voice Agent successfully started for job: {ctx.job.id}")

# Worker options for production
def get_worker_options() -> WorkerOptions:
    """Get optimized worker options for Hero365"""
    config = LiveKitConfig()
    
    return WorkerOptions(
        entrypoint_fnc=entrypoint,
        # No agent_name means this worker will receive all jobs automatically
        num_idle_processes=config.LIVEKIT_WORKER_PROCESSES,
        load_threshold=config.LIVEKIT_LOAD_THRESHOLD,
        job_memory_limit_mb=config.LIVEKIT_MEMORY_LIMIT_MB,
        job_memory_warn_mb=config.LIVEKIT_MEMORY_WARN_MB,
        ws_url=config.LIVEKIT_URL,
        api_key=config.LIVEKIT_API_KEY,
        api_secret=config.LIVEKIT_API_SECRET,
    )

# CLI runner with improved error handling
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('hero365_voice_agent.log')
        ]
    )
    
    logger.info("🚀 Starting Hero365 Voice Agent Worker")
    
    # Validate configuration before starting
    config = LiveKitConfig()
    if not config.validate():
        logger.error("❌ Configuration validation failed")
        exit(1)
    
    # Log configuration status
    ai_services = config.validate_ai_services()
    logger.info(f"🔧 AI Services Configuration: {ai_services}")
    
    missing_services = [service for service, available in ai_services.items() if not available]
    if missing_services:
        logger.warning(f"⚠️ Missing AI service configurations: {missing_services}")
    
    try:
        # Run the worker using the modern CLI
        cli.run_app(get_worker_options())
    except KeyboardInterrupt:
        logger.info("👋 Hero365 Voice Agent Worker shutting down...")
    except Exception as e:
        logger.error(f"❌ Fatal error in Hero365 Voice Agent Worker: {e}")
        exit(1) 