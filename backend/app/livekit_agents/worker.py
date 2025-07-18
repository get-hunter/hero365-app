"""
Hero365 Voice Agent Worker for LiveKit Integration
Simplified single-agent architecture with direct tool access
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    function_tool,
    WorkerOptions,
    cli,
)
from livekit.plugins import deepgram, openai, cartesia, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from .config import LiveKitConfig
from .context_preloader import ContextPreloader
from .context import ContextValidator, BusinessContextManager
from .agent import Hero365Agent
from ..infrastructure.config.dependency_injection import get_container

logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext):
    """
    Enhanced entrypoint for the simplified Hero365 Voice Agent
    """
    try:
        logger.info(f"🚀 Hero365 Voice Agent starting for job: {ctx.job.id}")
        
        # Initialize context validator
        validator = ContextValidator()
        
        # Connect to the room first
        await ctx.connect()
        logger.info(f"✅ Connected to room: {ctx.room.name}")
        
        # Extract and validate business context
        business_context = None
        user_context = None
        
        try:
            # Parse room metadata for preloaded context
            if ctx.room.metadata:
                room_metadata = json.loads(ctx.room.metadata)
                logger.info(f"📊 Room metadata parsed successfully")
                
                # Extract preloaded context
                preloaded_context = room_metadata.get('preloaded_context')
                if preloaded_context:
                    logger.info(f"🔧 Found preloaded context in room metadata")
                    
                    # Validate preloaded context
                    is_valid, errors = validator.validate_preloaded_context(preloaded_context)
                    if not is_valid:
                        logger.warning(f"⚠️ Preloaded context validation failed: {errors}")
                        for error in errors:
                            logger.warning(f"  - {error}")
                    else:
                        logger.info(f"✅ Preloaded context validation passed")
                    
                    # Deserialize context for agent use
                    context_preloader = ContextPreloader()
                    agent_context = context_preloader.deserialize_context(preloaded_context)
                    
                    if agent_context:
                        # Validate agent context
                        agent_valid, agent_errors = validator.validate_agent_context(agent_context)
                        if not agent_valid:
                            logger.warning(f"⚠️ Agent context validation failed: {agent_errors}")
                            for error in agent_errors:
                                logger.warning(f"  - {error}")
                        else:
                            logger.info(f"✅ Agent context validation passed")
                        
                        # Log context status
                        validator.log_context_status(agent_context, "Preloaded Agent")
                        
                        # Generate context report
                        report = validator.generate_context_report(agent_context)
                        logger.info(f"📋 Context Report: {report['validation_status']}, {report['completeness']:.1%} complete")
                        
                        business_context = agent_context
                        user_context = {
                            'user_name': agent_context.get('user_name'),
                            'user_email': agent_context.get('user_email'),
                            'user_role': agent_context.get('user_role'),
                            'user_id': agent_context.get('user_id'),
                            'user_permissions': agent_context.get('user_permissions', []),
                            'user_preferences': agent_context.get('user_preferences', {})
                        }
                        logger.info(f"✅ Context deserialized successfully for agent")
                    else:
                        logger.warning("⚠️ Failed to deserialize preloaded context")
                else:
                    logger.warning("⚠️ No preloaded context found in room metadata")
                    
        except Exception as e:
            logger.error(f"❌ Error extracting context from room metadata: {e}")
        
        # Fallback: Try to extract basic info from metadata and load context
        if not business_context:
            logger.info("🔄 Attempting fallback context loading")
            try:
                if ctx.room.metadata:
                    room_metadata = json.loads(ctx.room.metadata)
                    user_id = room_metadata.get('user_id')
                    business_id = room_metadata.get('business_id')
                    
                    if user_id and business_id:
                        logger.info(f"🔧 Loading context via fallback for user_id: {user_id}, business_id: {business_id}")
                        
                        # Initialize business context manager and load context
                        context_manager = BusinessContextManager()
                        container = get_container()
                        user_info = room_metadata.get('user_info')
                        await context_manager.initialize(user_id, business_id, container, user_info)
                        
                        # Convert to agent context format
                        business_ctx = context_manager.get_business_context()
                        user_ctx = context_manager.get_user_context()
                        
                        if business_ctx:
                            business_context = {
                                'business_name': business_ctx.business_name,
                                'business_type': business_ctx.business_type,
                                'phone': business_ctx.phone,
                                'email': business_ctx.email,
                                'address': business_ctx.address,
                                'timezone': business_ctx.timezone,
                                'active_jobs': business_ctx.active_jobs,
                                'pending_estimates': business_ctx.pending_estimates,
                                'recent_contacts_count': business_ctx.recent_contacts_count,
                                'recent_jobs_count': business_ctx.recent_jobs_count,
                                'recent_estimates_count': business_ctx.recent_estimates_count,
                                'last_refresh': business_ctx.last_refresh.isoformat() if business_ctx.last_refresh else None
                            }
                            
                            # Validate fallback context
                            fallback_valid, fallback_errors = validator.validate_agent_context(business_context)
                            if not fallback_valid:
                                logger.warning(f"⚠️ Fallback context validation failed: {fallback_errors}")
                            else:
                                logger.info(f"✅ Fallback context validation passed")
                            
                            # Log fallback context status
                            validator.log_context_status(business_context, "Fallback")
                            
                        if user_ctx:
                            user_context = {
                                'user_name': user_ctx.name,
                                'user_email': user_ctx.email,
                                'user_role': user_ctx.role,
                                'user_id': user_ctx.user_id,
                                'user_permissions': user_ctx.permissions,
                                'user_preferences': user_ctx.preferences
                            }
                            
                        logger.info(f"✅ Fallback context loaded successfully")
                    else:
                        logger.warning("⚠️ No user_id or business_id found for fallback loading")
                        
            except Exception as e:
                logger.error(f"❌ Error in fallback context loading: {e}")
        
        # Final context validation and logging
        if business_context:
            # Generate final context report
            final_report = validator.generate_context_report(business_context)
            logger.info(f"🎯 Final Context Report:")
            logger.info(f"  Status: {final_report['validation_status']}")
            logger.info(f"  Completeness: {final_report['completeness']:.1%}")
            logger.info(f"  Errors: {len(final_report['errors'])}")
            logger.info(f"  Warnings: {len(final_report['warnings'])}")
            
            # Log business details
            business_name = business_context.get('business_name', 'Unknown')
            business_type = business_context.get('business_type', 'Unknown')
            user_name = business_context.get('user_name', 'Unknown')
            logger.info(f"🏢 Agent will serve {user_name} from {business_name} ({business_type})")
            
            # Log metrics
            active_jobs = business_context.get('active_jobs', 0)
            pending_estimates = business_context.get('pending_estimates', 0)
            total_contacts = business_context.get('total_contacts', 0)
            logger.info(f"📊 Business Metrics: {active_jobs} active jobs, {pending_estimates} pending estimates, {total_contacts} total contacts")
            
        else:
            logger.warning("⚠️ Agent will start without business context - limited functionality available")
        
        # Initialize the single powerful agent
        agent = Hero365Agent(business_context=business_context, user_context=user_context)
        
        # Set up business context manager if available
        if business_context:
            try:
                context_manager = BusinessContextManager()
                container = get_container()
                user_id = business_context.get('user_id')
                business_id = business_context.get('business_id')
                
                if user_id and business_id:
                    await context_manager.initialize(user_id, business_id, container)
                    agent.set_business_context_manager(context_manager)
                    logger.info("✅ Business context manager set for agent")
            except Exception as e:
                logger.warning(f"⚠️ Could not set business context manager: {e}")
        
        # Get configuration
        config = LiveKitConfig()
        voice_config = config.get_voice_pipeline_config()
        
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
        
        # Generate context-aware initial greeting
        greeting_instructions = "Greet the user warmly and introduce yourself as their Hero365 business assistant."
        if business_context and business_context.get('business_name'):
            greeting_instructions += f" Mention that you're here to help with {business_context['business_name']} and can assist with contacts, jobs, estimates, and business insights. Ask how you can help them today."
        else:
            greeting_instructions += " Mention that you can help with contacts, jobs, estimates, and business management. Ask how you can help them with their business today."
        
        await session.generate_reply(instructions=greeting_instructions)
        
        logger.info("🎤 Hero365 Agent ready - single powerful agent with all capabilities")
        
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