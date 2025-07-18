"""
Hero365 LiveKit Worker - Modern Agent implementation for voice sessions
Uses LiveKit Agents 1.0 pattern with Agent and AgentSession for automatic room joining
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from livekit import agents, rtc
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import deepgram, openai, cartesia, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from .config import LiveKitConfig
from .hero365_triage_agent import Hero365TriageAgent
from .specialists.contact_agent import ContactAgent
from .specialists.job_agent import JobAgent
from .specialists.estimate_agent import EstimateAgent
from .specialists.scheduling_agent import SchedulingAgent
from .context_management import get_context_manager
from .monitoring.metrics import get_metrics
from .business_context_manager import get_business_context_manager, BusinessContextManager

logger = logging.getLogger(__name__)

class Hero365Agent(Agent):
    """Hero365 Voice Agent with Business Context and Intelligent Multi-Agent Workflow"""
    
    def __init__(self):
        super().__init__(
            instructions="""You are Hero365, an AI assistant specialized in helping home-services contractors and independent professionals manage their business operations. 

You have comprehensive knowledge of the business context, including:
- Current business information and owner details
- Recent contacts and their interaction history
- Active jobs and scheduled work
- Pending estimates and proposals
- Business performance metrics

You can provide immediate, contextual assistance without needing to search for basic information. You intelligently route conversations to specialized agents when needed and provide proactive suggestions based on current business state."""
        )
        self.config = LiveKitConfig()
        self.session_id = None
        self.user_id = None
        self.business_id = None
        self.context_manager = None
        self.metrics = None
        self.business_context_manager: Optional[BusinessContextManager] = None
        
        # Initialize specialized agents
        self.triage_agent = None
        self.contact_agent = None
        self.job_agent = None
        self.estimate_agent = None
        self.scheduling_agent = None
        self.current_specialist = None
        
        # Conversation context
        self.conversation_history = []
        self.current_task = None
        
    async def on_enter(self):
        """Called when the agent enters a room"""
        logger.info(f"🎯 Hero365 Agent entering room")
        
        # Initialize context manager and metrics
        self.context_manager = await get_context_manager()
        self.metrics = await get_metrics()
        
        # Extract session info from room metadata
        await self._extract_session_info()
        
        # Initialize session context
        if self.context_manager:
            await self.context_manager.initialize_session(
                self.session_id, self.user_id, self.business_id
            )
        
        if self.metrics:
            await self.metrics.start_session(self.session_id, self.user_id, self.business_id)
        
        # Initialize business context manager
        await self._initialize_business_context()
        
        # Initialize specialized agents
        await self._initialize_specialists()
        
        # Generate initial contextual greeting
        await self._generate_contextual_greeting()
        
        logger.info("🎤 Hero365 Agent ready to handle voice conversations")
        
    async def _extract_session_info(self):
        """Extract session information from room metadata"""
        # TODO: Implement room metadata extraction when we understand the correct API
        # For now, we'll use defaults - this should be enhanced to extract real user/business info
        self.session_id = "voice_session_default"
        self.user_id = "c0760bda-b547-4151-990f-eef1169f90b1"  # Default for testing
        self.business_id = "660e8400-e29b-41d4-a716-446655440000"  # Default for testing
    
    async def _initialize_business_context(self):
        """Initialize comprehensive business context"""
        try:
            if not self.user_id or not self.business_id:
                logger.warning("⚠️ No user_id or business_id available, skipping business context initialization")
                return
                
            # Get business context manager
            self.business_context_manager = await get_business_context_manager()
            
            # Initialize with user and business context
            await self.business_context_manager.initialize(
                user_id=self.user_id,
                business_id=self.business_id
            )
            
            # Log context summary
            context_summary = self.business_context_manager.get_context_summary()
            logger.info(f"🏢 Business context loaded: {context_summary}")
            
        except Exception as e:
            logger.error(f"❌ Error initializing business context: {e}")
    
    async def _initialize_specialists(self):
        """Initialize all specialized agents with business context"""
        try:
            config = self.config
            
            # Initialize triage agent (main router)
            self.triage_agent = Hero365TriageAgent(config)
            
            # Initialize specialist agents
            self.contact_agent = ContactAgent(config)
            self.job_agent = JobAgent(config)
            self.estimate_agent = EstimateAgent(config)
            self.scheduling_agent = SchedulingAgent(config)
            
            # Set current specialist to triage by default
            self.current_specialist = self.triage_agent
            
            # Share business context with specialists
            await self._share_business_context_with_specialists()
            
            logger.info("✅ All specialist agents initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing specialists: {e}")
            # Fall back to triage agent only
            self.triage_agent = Hero365TriageAgent(config)
            self.current_specialist = self.triage_agent
    
    async def _share_business_context_with_specialists(self):
        """Share business context with all specialist agents"""
        try:
            if not self.business_context_manager:
                return
                
            # Add business context to each specialist
            specialists = [
                self.triage_agent,
                self.contact_agent,
                self.job_agent,
                self.estimate_agent,
                self.scheduling_agent
            ]
            
            for specialist in specialists:
                if specialist and hasattr(specialist, 'set_business_context'):
                    specialist.set_business_context(self.business_context_manager)
                    
        except Exception as e:
            logger.error(f"❌ Error sharing business context with specialists: {e}")
    
    async def _generate_contextual_greeting(self):
        """Generate contextual greeting based on business context"""
        try:
            if not self.business_context_manager:
                return
                
            business_context = self.business_context_manager.get_business_context()
            business_summary = self.business_context_manager.get_business_summary()
            suggestions = self.business_context_manager.get_contextual_suggestions()
            
            if business_context and business_summary:
                # Create personalized greeting
                greeting_parts = []
                
                # Time-based greeting
                current_hour = datetime.now().hour
                if current_hour < 12:
                    greeting_parts.append("Good morning")
                elif current_hour < 17:
                    greeting_parts.append("Good afternoon")
                else:
                    greeting_parts.append("Good evening")
                
                # Business context
                greeting_parts.append(f"Welcome to {business_context.business_name}!")
                
                # Business summary
                if business_summary.active_jobs > 0:
                    greeting_parts.append(f"You have {business_summary.active_jobs} active jobs.")
                
                if business_summary.pending_estimates > 0:
                    greeting_parts.append(f"There are {business_summary.pending_estimates} pending estimates.")
                
                # Contextual suggestions
                if suggestions and suggestions.urgent_items:
                    greeting_parts.append("I noticed some urgent items that need attention.")
                
                greeting_parts.append("What would you like to work on today?")
                
                contextual_greeting = " ".join(greeting_parts)
                logger.info(f"🎯 Generated contextual greeting: {contextual_greeting[:100]}...")
                
        except Exception as e:
            logger.error(f"❌ Error generating contextual greeting: {e}")
    
    async def _analyze_and_route_with_context(self, message: str) -> tuple[str, Optional[str]]:
        """Use business context and LLM to intelligently analyze user intent"""
        
        # Get business context for enhanced routing
        business_context = ""
        if self.business_context_manager:
            business_summary = self.business_context_manager.get_business_summary()
            recent_contacts = self.business_context_manager.get_recent_contacts(5)
            recent_jobs = self.business_context_manager.get_recent_jobs(5)
            recent_estimates = self.business_context_manager.get_recent_estimates(5)
            suggestions = self.business_context_manager.get_contextual_suggestions()
            
            # Build context string
            context_parts = []
            
            if business_summary:
                context_parts.append(f"Business Summary: {business_summary.active_jobs} active jobs, {business_summary.pending_estimates} pending estimates")
            
            if recent_contacts:
                contact_names = [c.name for c in recent_contacts]
                context_parts.append(f"Recent Contacts: {', '.join(contact_names[:3])}")
            
            if recent_jobs:
                job_titles = [j.title for j in recent_jobs]
                context_parts.append(f"Recent Jobs: {', '.join(job_titles[:3])}")
            
            if recent_estimates:
                estimate_titles = [e.title for e in recent_estimates]
                context_parts.append(f"Recent Estimates: {', '.join(estimate_titles[:3])}")
                
            if suggestions and suggestions.urgent_items:
                context_parts.append(f"Urgent Items: {', '.join(suggestions.urgent_items[:2])}")
            
            business_context = " | ".join(context_parts)
        
        # Get conversation context
        recent_messages = self.conversation_history[-5:] if len(self.conversation_history) > 5 else self.conversation_history
        conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
        
        # Enhanced LLM prompt with business context
        routing_prompt = f"""
        Analyze the user's message and determine the most appropriate specialist to handle their request.
        
        Available specialists:
        - contact: For creating, searching, updating customer contacts, phone numbers, emails, addresses
        - job: For creating, scheduling, tracking work orders, repairs, installations, maintenance
        - estimate: For creating quotes, proposals, pricing, cost estimates
        - schedule: For booking appointments, checking availability, calendar management
        - general: For general questions, weather, directions, or unclear requests
        
        Current Business Context:
        {business_context}
        
        Recent conversation context:
        {conversation_context}
        
        Current user message: "{message}"
        
        Consider the business context when making routing decisions. If the user mentions a specific contact, job, or estimate name that appears in the context, prioritize that information.
        
        Respond with ONLY the specialist name (contact, job, estimate, schedule, or general) that best matches the user's intent.
        """
        
        try:
            # Use the LLM to determine routing
            from livekit.plugins.openai import LLM
            llm = LLM(model="gpt-4o-mini", temperature=0.1)
            
            # Get the routing decision
            routing_response = await llm.agenerate(routing_prompt)
            specialist_type = routing_response.strip().lower()
            
            # Validate the response
            valid_specialists = ["contact", "job", "estimate", "schedule", "general"]
            if specialist_type not in valid_specialists:
                specialist_type = "general"
            
            # Determine if handoff is needed
            current_type = self._get_current_specialist_type()
            handoff_needed = current_type != specialist_type
            
            logger.info(f"🤖 Context-aware routing analysis: {specialist_type} (handoff needed: {handoff_needed})")
            
            return specialist_type, None if not handoff_needed else specialist_type
            
        except Exception as e:
            logger.error(f"❌ Error in context-aware routing analysis: {e}")
            return "general", None
    
    async def _seamless_handoff(self, specialist_type: str) -> None:
        """Perform seamless handoff to specialist without user notification"""
        try:
            # Get the specialist agent
            specialist_map = {
                "contact": self.contact_agent,
                "job": self.job_agent, 
                "estimate": self.estimate_agent,
                "schedule": self.scheduling_agent
            }
            
            new_specialist = specialist_map.get(specialist_type)
            if not new_specialist:
                logger.warning(f"Unknown specialist type: {specialist_type}")
                return
            
            # Perform seamless handoff
            previous_specialist = self.current_specialist.__class__.__name__ if self.current_specialist else "None"
            self.current_specialist = new_specialist
            
            logger.info(f"🔄 Seamless handoff: {previous_specialist} → {new_specialist.__class__.__name__}")
            
            # Store handoff context silently
            self.conversation_history.append({
                "type": "handoff",
                "from": previous_specialist,
                "to": new_specialist.__class__.__name__,
                "timestamp": datetime.now().isoformat(),
                "silent": True
            })
            
        except Exception as e:
            logger.error(f"❌ Error in seamless handoff to {specialist_type}: {e}")
    
    async def route_message(self, message: str) -> str:
        """Intelligently route message with business context awareness"""
        try:
            # Refresh business context if needed
            if self.business_context_manager:
                await self.business_context_manager.refresh_context()
            
            # Analyze user intent using business context
            specialist_type, handoff_to = await self._analyze_and_route_with_context(message)
            
            # Perform seamless handoff if needed
            if handoff_to:
                await self._seamless_handoff(handoff_to)
            
            # Process with current specialist
            if hasattr(self.current_specialist, 'process_message'):
                response = await self.current_specialist.process_message(None, message)
            else:
                # Fall back to context-aware general response
                response = await self._generate_context_aware_response(message)
            
            # Store conversation history
            self.conversation_history.append({
                "type": "message",
                "user": message,
                "assistant": response,
                "specialist": self.current_specialist.__class__.__name__,
                "intent": specialist_type,
                "timestamp": datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error routing message: {e}")
            return "I apologize, but I encountered an error. Could you please rephrase your request?"
    
    async def _generate_context_aware_response(self, message: str) -> str:
        """Generate intelligent response using business context"""
        try:
            # Get business context for response generation
            business_context = ""
            if self.business_context_manager:
                business_summary = self.business_context_manager.get_business_summary()
                suggestions = self.business_context_manager.get_contextual_suggestions()
                
                context_parts = []
                if business_summary:
                    context_parts.append(f"Business has {business_summary.active_jobs} active jobs, {business_summary.pending_estimates} pending estimates")
                
                if suggestions and (suggestions.quick_actions or suggestions.urgent_items):
                    context_parts.append("Current priorities available for discussion")
                
                business_context = " | ".join(context_parts)
            
            # Get conversation context
            recent_messages = self.conversation_history[-3:] if len(self.conversation_history) > 3 else self.conversation_history
            conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages if msg.get('role')])
            
            context_aware_prompt = f"""
            You are Hero365, an AI assistant for home-services contractors. Respond naturally and helpfully to the user's message.
            
            Current Business Context:
            {business_context}
            
            Recent conversation:
            {conversation_context}
            
            User message: "{message}"
            
            Provide a helpful, professional response that takes into account the current business context. 
            If the user is asking about something that might relate to their business data, acknowledge what you know and offer assistance.
            Be proactive in suggesting relevant actions when appropriate.
            """
            
            from livekit.plugins.openai import LLM
            llm = LLM(model="gpt-4o-mini", temperature=0.7)
            
            response = await llm.agenerate(context_aware_prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"❌ Error generating context-aware response: {e}")
            return "I'm here to help you manage your business operations. What would you like to work on today?"
    
    def _get_current_specialist_type(self) -> str:
        """Get the type of current specialist"""
        if isinstance(self.current_specialist, ContactAgent):
            return "contact"
        elif isinstance(self.current_specialist, JobAgent):
            return "job"
        elif isinstance(self.current_specialist, EstimateAgent):
            return "estimate"
        elif isinstance(self.current_specialist, SchedulingAgent):
            return "schedule"
        else:
            return "general"
    
    async def handle_message(self, message: str) -> str:
        """Main message handler that integrates with LiveKit framework"""
        try:
            logger.info(f"🎤 Processing voice message: {message[:100]}...")
            
            # Route message to appropriate specialist
            response = await self.route_message(message)
            
            # Log the interaction
            logger.info(f"🤖 Agent response: {response[:100]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."

    async def say_hello(self) -> str:
        """Generate initial greeting for new sessions"""
        try:
            if self.business_context_manager:
                business_context = self.business_context_manager.get_business_context()
                business_summary = self.business_context_manager.get_business_summary()
                
                if business_context and business_summary:
                    greeting = f"Hello! I'm Hero365, your AI assistant for {business_context.business_name}. "
                    
                    if business_summary.active_jobs > 0:
                        greeting += f"I see you have {business_summary.active_jobs} active jobs. "
                    
                    if business_summary.pending_estimates > 0:
                        greeting += f"There are {business_summary.pending_estimates} pending estimates. "
                    
                    greeting += "I'm here to help you manage your business operations. What would you like to work on?"
                    
                    return greeting
            
            # Fallback greeting
            current_time = datetime.now().strftime("%I:%M %p")
            greeting = f"Hello! I'm Hero365, your AI assistant for managing your home services business. "
            greeting += f"It's currently {current_time}. "
            greeting += "I can help you with contacts, jobs, estimates, scheduling, and much more. "
            greeting += "What would you like to work on today?"
            
            return greeting
            
        except Exception as e:
            logger.error(f"❌ Error generating greeting: {e}")
            return "Hello! I'm Hero365, your AI assistant. How can I help you today?"

    async def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and context"""
        status = {
            "session_id": self.session_id,
            "current_specialist": self.current_specialist.__class__.__name__ if self.current_specialist else None,
            "conversation_length": len(self.conversation_history),
            "available_specialists": [
                "ContactAgent", "JobAgent", "EstimateAgent", "SchedulingAgent"
            ],
            "capabilities": self.current_specialist.get_specialist_capabilities() if hasattr(self.current_specialist, 'get_specialist_capabilities') else []
        }
        
        # Add business context info
        if self.business_context_manager:
            status["business_context"] = self.business_context_manager.get_context_summary()
        
        return status

    async def get_handoff_options(self) -> List[Dict[str, Any]]:
        """Get available handoff options for the current session"""
        return [
            {
                "type": "contact",
                "name": "Contact Management",
                "description": "Create, search, and manage customer contacts",
                "capabilities": self.contact_agent.get_specialist_capabilities() if self.contact_agent else []
            },
            {
                "type": "job", 
                "name": "Job Management",
                "description": "Create, schedule, and track work orders",
                "capabilities": self.job_agent.get_specialist_capabilities() if self.job_agent else []
            },
            {
                "type": "estimate",
                "name": "Estimate Management", 
                "description": "Create quotes, proposals, and pricing",
                "capabilities": self.estimate_agent.get_specialist_capabilities() if self.estimate_agent else []
            },
            {
                "type": "schedule",
                "name": "Scheduling Management",
                "description": "Book appointments and manage calendar",
                "capabilities": self.scheduling_agent.get_specialist_capabilities() if self.scheduling_agent else []
            }
        ]

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