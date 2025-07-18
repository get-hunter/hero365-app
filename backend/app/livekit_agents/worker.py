"""
Hero365 Voice Agent Worker for LiveKit Integration
Handles voice interactions with business context awareness
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    function_tool,
    WorkerOptions,
    cli,
)
from livekit.plugins import deepgram, openai, cartesia, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from .config import LiveKitConfig
from .business_context_manager import BusinessContextManager
from ..infrastructure.config.dependency_injection import get_container

logger = logging.getLogger(__name__)


class Hero365VoiceAgent(Agent):
    """Main Hero365 Voice Agent with business context awareness"""
    
    def __init__(self):
        logger.info("🔧 Hero365VoiceAgent.__init__ called")
        
        # Initialize business context manager
        self.business_context_manager = BusinessContextManager()
        self.business_context: Optional[Dict[str, Any]] = None
        self.user_id: Optional[str] = None
        self.business_id: Optional[str] = None
        self.room = None
        
        # Initialize as LiveKit Agent with instructions only
        # Tools will be registered separately to avoid duplicate function issues
        super().__init__(
            instructions="""You are the Hero365 AI Assistant, a specialized voice agent for home service businesses.

IMPORTANT INSTRUCTIONS:
1. When users ask about business information (name, type, contact details), ALWAYS use the get_business_info tool to get accurate information.
2. When users ask about their name or user information, ALWAYS use the get_user_info tool.
3. When users ask for business overview or status, use the get_business_status tool.
4. NEVER make assumptions about business details - always use the tools to get real data.
5. Be helpful, professional, and conversational in your responses.
6. If business information is not available, inform the user politely.

You help with:
- Managing contacts and customer relationships
- Creating and tracking estimates and invoices
- Scheduling jobs and appointments
- Providing business insights and overviews
- General business management tasks

Always be professional, helpful, and use the available tools to provide accurate information."""
        )
        
        logger.info("🔧 Hero365VoiceAgent initialized successfully")
        
    async def on_enter(self, room=None):
        """Initialize agent when entering a room"""
        try:
            logger.info(f"🎤 Hero365 Voice Agent entering room: {room.name if room else 'unknown'}")
            
            # Store room reference for metadata access
            self.room = room
            
            # Extract user and business IDs from room metadata
            session_info = self._extract_session_info(room)
            self.user_id = session_info.get('user_id')
            self.business_id = session_info.get('business_id')
            
            logger.info(f"🎯 Agent initialized for user: {self.user_id}, business: {self.business_id}")
            
            # Initialize business context if we have the required IDs
            if self.user_id and self.business_id:
                await self._initialize_business_context()
            else:
                logger.warning("⚠️ Missing user_id or business_id, using defaults")
                
        except Exception as e:
            logger.error(f"❌ Error in on_enter: {e}")
            # Continue with defaults if initialization fails
            
    def _extract_session_info(self, room) -> Dict[str, Any]:
        """Extract session information from room metadata"""
        try:
            if room and hasattr(room, 'metadata') and room.metadata:
                # Parse JSON metadata from room
                metadata = json.loads(room.metadata)
                logger.info(f"📊 Extracted room metadata: {metadata}")
                return {
                    'user_id': metadata.get('user_id'),
                    'business_id': metadata.get('business_id'),
                    'session_id': metadata.get('session_id')
                }
        except Exception as e:
            logger.error(f"❌ Error parsing room metadata: {e}")
            
        # Return defaults if metadata parsing fails
        return {
            'user_id': 'c0760bda-b547-4151-990f-eef1169f90b1',  # Default user ID
            'business_id': '660e8400-e29b-41d4-a716-446655440000',  # Default business ID
            'session_id': 'default_session'
        }
    
    async def _initialize_business_context(self):
        """Initialize business context with user and business data"""
        try:
            container = get_container()
            await self.business_context_manager.initialize(
                self.user_id, 
                self.business_id, 
                container
            )
            
            # Get business context for the agent
            context = self.business_context_manager.get_business_context()
            if context:
                self.business_context = {
                    'business_name': context.business_name,
                    'business_type': context.business_type,
                    'user_name': getattr(context, 'user_name', 'User'),  # Use getattr with default
                    'phone': context.phone,
                    'email': context.email,
                    'address': context.address,
                    'recent_contacts_count': context.recent_contacts_count,
                    'recent_jobs_count': context.recent_jobs_count,
                    'recent_estimates_count': context.recent_estimates_count,
                    'active_jobs': context.active_jobs,
                    'pending_estimates': context.pending_estimates,
                    'last_refresh': context.last_refresh
                }
                logger.info(f"✅ Business context loaded: {self.business_context}")
            else:
                logger.warning("⚠️ No business context found")
            
        except Exception as e:
            logger.error(f"❌ Error initializing business context: {e}")
            self.business_context = None
    
    @function_tool
    def get_business_info(self) -> str:
        """Get current business information including name, type, and contact details"""
        logger.info("🔧 get_business_info tool called")
        
        if not self.business_context:
            return "Business information is not available at the moment."
            
        info = []
        if self.business_context.get('business_name'):
            info.append(f"Business Name: {self.business_context['business_name']}")
        if self.business_context.get('business_type'):
            info.append(f"Business Type: {self.business_context['business_type']}")
        if self.business_context.get('phone'):
            info.append(f"Phone: {self.business_context['phone']}")
        if self.business_context.get('email'):
            info.append(f"Email: {self.business_context['email']}")
        if self.business_context.get('address'):
            info.append(f"Address: {self.business_context['address']}")
            
        return "\n".join(info) if info else "Business information is not available."
    
    @function_tool
    def get_user_info(self) -> str:
        """Get current user information"""
        logger.info("🔧 get_user_info tool called")
        
        if not self.business_context:
            return "User information is not available at the moment."
            
        user_name = self.business_context.get('user_name', 'User')
        return f"User Name: {user_name}"
    
    @function_tool
    def get_business_status(self) -> str:
        """Get complete business status and activity overview"""
        logger.info("🔧 get_business_status tool called")
        
        if not self.business_context:
            return "Business overview is not available at the moment."
            
        overview = []
        overview.append(f"Business: {self.business_context.get('business_name', 'Unknown')}")
        overview.append(f"Recent Contacts: {self.business_context.get('recent_contacts_count', 0)}")
        overview.append(f"Active Jobs: {self.business_context.get('active_jobs', 0)}")
        overview.append(f"Pending Estimates: {self.business_context.get('pending_estimates', 0)}")
        overview.append(f"Recent Jobs: {self.business_context.get('recent_jobs_count', 0)}")
        overview.append(f"Recent Estimates: {self.business_context.get('recent_estimates_count', 0)}")
        
        return "\n".join(overview)


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the Hero365 Voice Agent"""
    try:
        logger.info(f"🚀 Hero365 Voice Agent starting for job: {ctx.job.id}")
        
        # Connect to the room first
        await ctx.connect()
        logger.info(f"✅ Connected to room: {ctx.room.name}")
        
        # Get configuration
        config = LiveKitConfig()
        voice_config = config.get_voice_pipeline_config()
        
        # Initialize the agent
        agent = Hero365VoiceAgent()
        
        # Create agent session with proper configuration
        session = AgentSession(
            stt=deepgram.STT(
                model=voice_config["stt"]["model"],
                language=voice_config["stt"]["language"],
                keywords=[(keyword, 1.5) for keyword in voice_config["stt"]["keywords"]],
                smart_format=True,
                interim_results=voice_config["stt"]["interim_results"],
            ),
            llm=openai.LLM(
                model=voice_config["llm"]["model"],
                temperature=voice_config["llm"]["temperature"],
            ),
            tts=cartesia.TTS(
                voice=voice_config["tts"]["voice"],
                model=voice_config["tts"]["model"],
                language=voice_config["tts"]["language"],
            ),
            vad=silero.VAD.load(
                min_silence_duration=voice_config["turn_detection"]["min_silence_duration"],
                min_speech_duration=voice_config["turn_detection"]["min_speech_duration"],
            ),
            turn_detection=MultilingualModel(),
        )
        
        # Start the session
        await session.start(
            room=ctx.room,
            agent=agent,
        )
        
        # Generate initial greeting
        await session.generate_reply(
            instructions="Greet the user and introduce yourself as their Hero365 business assistant. Ask how you can help them today."
        )
        
        logger.info("🎤 Hero365 Agent ready to handle voice conversations")
        
    except Exception as e:
        logger.error(f"❌ Error in entrypoint: {e}")
        raise


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    ) 