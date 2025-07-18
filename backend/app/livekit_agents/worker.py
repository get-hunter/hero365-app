"""
Hero365 Voice Agent Worker for LiveKit Integration
Enhanced with preloaded business context support and intelligent agent routing
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
    RunContext,
    function_tool,
    WorkerOptions,
    cli,
)
from livekit.plugins import deepgram, openai, cartesia, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from .config import LiveKitConfig
from .context_preloader import ContextPreloader
from .context_validator import ContextValidator
from .business_context_manager import BusinessContextManager
from .hero365_triage_agent import Hero365TriageAgent
from .specialists.contact_agent import ContactAgent
from .specialists.job_agent import JobAgent
from .specialists.estimate_agent import EstimateAgent
from .specialists.scheduling_agent import SchedulingAgent
from ..infrastructure.config.dependency_injection import get_container

logger = logging.getLogger(__name__)


class Hero365MainAgent(Agent):
    """Main Hero365 Voice Agent with intelligent routing to specialist agents"""
    
    def __init__(self, business_context: dict = None, user_context: dict = None):
        logger.info("🔧 Hero365MainAgent.__init__ called")
        
        # Initialize business context
        self.business_context = business_context or {}
        self.user_context = user_context or {}
        
        # Merge user context into business context for easier access
        if user_context:
            self.business_context.update(user_context)
        
        logger.info(f"🔧 Main agent initialized with business context: {bool(self.business_context)}")
        
        # Initialize specialist agents
        self.config = LiveKitConfig()
        self.specialist_agents = self._initialize_specialist_agents()
        
        # Initialize as LiveKit Agent with enhanced instructions
        super().__init__(
            instructions=self._generate_routing_instructions()
        )
        
    def _initialize_specialist_agents(self) -> Dict[str, Agent]:
        """Initialize all specialist agents"""
        agents = {
            'contact': ContactAgent(self.config),
            'job': JobAgent(self.config),
            'estimate': EstimateAgent(self.config),
            'scheduling': SchedulingAgent(self.config)
        }
        
        # Set business context for all specialist agents
        for agent_name, agent in agents.items():
            if hasattr(agent, 'set_business_context'):
                agent.set_business_context(self.business_context)
            logger.info(f"🔧 Initialized {agent_name} specialist agent")
            
        return agents
        
    def _generate_routing_instructions(self) -> str:
        """Generate routing-aware instructions"""
        base_instructions = """You are the Hero365 AI Assistant, a specialized voice agent for home service businesses with intelligent routing capabilities."""
        
        if self.business_context:
            business_name = self.business_context.get('business_name', 'your business')
            business_type = self.business_context.get('business_type', 'home service business')
            user_name = self.business_context.get('user_name', 'User')
            
            context_instructions = f"""
            
BUSINESS CONTEXT:
- You are speaking with {user_name} from {business_name}
- This is a {business_type}
- You have access to current business information and can help with specific tasks

INTELLIGENT ROUTING:
You can route users to specialist agents for specific tasks:
- Contact management: "I'll connect you with our contact specialist"
- Job management: "Let me transfer you to our job specialist"  
- Estimate management: "I'll connect you with our estimate specialist"
- Scheduling: "Let me transfer you to our scheduling specialist"

IMPORTANT INSTRUCTIONS:
1. When users ask about business information, use the get_business_info tool for accurate details
2. When users ask about their name or user information, use the get_user_info tool
3. When users ask for business overview or status, use the get_business_status tool
4. For contact-related requests, use the route_to_contact_specialist tool
5. For job-related requests, use the route_to_job_specialist tool
6. For estimate-related requests, use the route_to_estimate_specialist tool
7. For scheduling-related requests, use the route_to_scheduling_specialist tool
8. Always use the available tools to get real, current data
9. Be helpful, professional, and conversational in your responses
10. Reference the business context naturally in your responses

You help with:
- Managing contacts and customer relationships
- Creating and tracking estimates and invoices
- Scheduling jobs and appointments
- Providing business insights and overviews
- General business management tasks
- Routing to appropriate specialists

Always be professional, helpful, and use the available tools to provide accurate information."""
        else:
            context_instructions = """

INTELLIGENT ROUTING:
You can route users to specialist agents for specific tasks:
- Contact management: "I'll connect you with our contact specialist"
- Job management: "Let me transfer you to our job specialist"  
- Estimate management: "I'll connect you with our estimate specialist"
- Scheduling: "Let me transfer you to our scheduling specialist"

IMPORTANT INSTRUCTIONS:
1. When users ask about business information, use the get_business_info tool
2. When users ask about their name or user information, use the get_user_info tool
3. When users ask for business overview or status, use the get_business_status tool
4. For contact-related requests, use the route_to_contact_specialist tool
5. For job-related requests, use the route_to_job_specialist tool
6. For estimate-related requests, use the route_to_estimate_specialist tool
7. For scheduling-related requests, use the route_to_scheduling_specialist tool
8. Always use the available tools to get real data
9. Be helpful, professional, and conversational in your responses
10. If business information is not available, inform the user politely

You help with:
- Managing contacts and customer relationships
- Creating and tracking estimates and invoices
- Scheduling jobs and appointments
- Providing business insights and overviews
- General business management tasks
- Routing to appropriate specialists

Always be professional, helpful, and use the available tools to provide accurate information."""
        
        return base_instructions + context_instructions
        
    @function_tool
    async def get_business_info(self) -> str:
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
    async def get_user_info(self) -> str:
        """Get current user information"""
        logger.info("🔧 get_user_info tool called")
        
        if not self.business_context:
            return "User information is not available at the moment."
            
        info = []
        if self.business_context.get('user_name'):
            info.append(f"Name: {self.business_context['user_name']}")
        if self.business_context.get('user_email'):
            info.append(f"Email: {self.business_context['user_email']}")
        if self.business_context.get('user_role'):
            info.append(f"Role: {self.business_context['user_role']}")
        if self.business_context.get('user_id'):
            info.append(f"User ID: {self.business_context['user_id']}")
            
        return "\n".join(info) if info else "User information is not available."

    @function_tool
    async def get_business_status(self) -> str:
        """Get complete business status and activity overview"""
        logger.info("🔧 get_business_status tool called")
        
        if not self.business_context:
            return "Business status is not available at the moment."
            
        status = []
        if self.business_context.get('business_name'):
            status.append(f"Business: {self.business_context['business_name']}")
        if self.business_context.get('business_type'):
            status.append(f"Type: {self.business_context['business_type']}")
        if self.business_context.get('active_jobs'):
            status.append(f"Active Jobs: {self.business_context['active_jobs']}")
        if self.business_context.get('pending_estimates'):
            status.append(f"Pending Estimates: {self.business_context['pending_estimates']}")
        if self.business_context.get('total_contacts'):
            status.append(f"Total Contacts: {self.business_context['total_contacts']}")
        if self.business_context.get('recent_contacts_count'):
            status.append(f"Recent Contacts: {self.business_context['recent_contacts_count']}")
        if self.business_context.get('revenue_this_month'):
            status.append(f"Revenue This Month: ${self.business_context['revenue_this_month']}")
        if self.business_context.get('jobs_this_week'):
            status.append(f"Jobs This Week: {self.business_context['jobs_this_week']}")
            
        return "\n".join(status) if status else "Business status is not available."

    @function_tool
    async def route_to_contact_specialist(self) -> tuple:
        """Route the user to the contact management specialist"""
        logger.info("🔧 Routing to contact specialist")
        # Create a fresh contact agent with business context
        contact_agent = ContactAgent(self.config)
        if hasattr(contact_agent, 'set_business_context'):
            contact_agent.set_business_context(self.business_context)
        return contact_agent, "I'll connect you with our contact specialist who can help you manage your contacts, create new ones, search for existing contacts, and handle all contact-related tasks."

    @function_tool
    async def route_to_job_specialist(self) -> tuple:
        """Route the user to the job management specialist"""
        logger.info("🔧 Routing to job specialist")
        # Create a fresh job agent with business context
        job_agent = JobAgent(self.config)
        if hasattr(job_agent, 'set_business_context'):
            job_agent.set_business_context(self.business_context)
        return job_agent, "Let me transfer you to our job specialist who can help you create new jobs, update job status, schedule appointments, track job progress, and manage all your work orders."

    @function_tool
    async def route_to_estimate_specialist(self) -> tuple:
        """Route the user to the estimate management specialist"""
        logger.info("🔧 Routing to estimate specialist")
        # Create a fresh estimate agent with business context
        estimate_agent = EstimateAgent(self.config)
        if hasattr(estimate_agent, 'set_business_context'):
            estimate_agent.set_business_context(self.business_context)
        return estimate_agent, "I'll connect you with our estimate specialist who can help you create estimates, manage proposals, convert estimates to invoices, and handle all your quoting needs."

    @function_tool
    async def route_to_scheduling_specialist(self) -> tuple:
        """Route the user to the scheduling specialist"""
        logger.info("🔧 Routing to scheduling specialist")
        # Create a fresh scheduling agent with business context
        scheduling_agent = SchedulingAgent(self.config)
        if hasattr(scheduling_agent, 'set_business_context'):
            scheduling_agent.set_business_context(self.business_context)
        return scheduling_agent, "Let me transfer you to our scheduling specialist who can help you check availability, book appointments, manage your calendar, and optimize your schedule."

    def get_specialist_agent(self, agent_type: str) -> Optional[Agent]:
        """Get a specialist agent by type"""
        return self.specialist_agents.get(agent_type)


async def entrypoint(ctx: JobContext):
    """Enhanced entrypoint for the Hero365 Voice Agent with comprehensive context validation and intelligent routing"""
    try:
        logger.info(f"🚀 Hero365 Voice Agent starting for job: {ctx.job.id}")
        
        # Initialize context validator
        validator = ContextValidator()
        
        # Connect to the room first
        await ctx.connect()
        logger.info(f"✅ Connected to room: {ctx.room.name}")
        
        # Extract preloaded context from room metadata
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
                        # Continue anyway, but log the issues
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
                        # Extract user info from metadata if available
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
        
        # Initialize the main agent with loaded context and specialist agents
        agent = Hero365MainAgent(business_context=business_context, user_context=user_context)
        
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
        greeting_instructions = "Greet the user warmly and introduce yourself as their Hero365 business assistant with intelligent routing capabilities."
        if business_context and business_context.get('business_name'):
            greeting_instructions += f" Mention that you're here to help with {business_context['business_name']} and can connect them with specialist agents for specific tasks. Ask how you can assist them today."
        else:
            greeting_instructions += " Mention that you can help with general business tasks and connect them with specialist agents for specific needs. Ask how you can help them with their business today."
        
        await session.generate_reply(instructions=greeting_instructions)
        
        logger.info("🎤 Hero365 Main Agent ready to handle voice conversations with intelligent routing to specialist agents")
        
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