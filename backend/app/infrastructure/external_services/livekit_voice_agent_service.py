"""
LiveKit Voice Agent Service

Complete LiveKit-based voice agent implementation with tools, configurations, and session management.
Consolidates all voice agent functionality into a single, cohesive service.
"""

import os
import asyncio
import uuid
import json
import logging
from typing import Optional, Dict, Any, List, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

try:
    import livekit
    from livekit import api, Room, RoomOptions, ConnectOptions
    from livekit.agents import AutoSubscribe, JobContext, JobProcess, WorkerOptions, cli
    from livekit.agents.llm import LLMAgent
    from livekit.agents.voice_assistant import VoiceAssistant
    from livekit.agents.stt import STTAdapter
    from livekit.agents.tts import TTSAdapter
    from livekit.agents.llm import LLMAdapter
    from livekit.plugins import openai, elevenlabs, deepgram
    LIVEKIT_AVAILABLE = True
except ImportError:
    # Fallback for when LiveKit is not installed
    LIVEKIT_AVAILABLE = False
    livekit = None
    api = None

from ...application.ports.voice_agent_service import (
    VoiceAgentServicePort, VoiceToolRegistry, VoiceCommandProcessor,
    VoiceAgentTool, VoiceSessionConfig, OutboundCallConfig, 
    VoiceAgentResult, LiveKitRoomConfig
)
from ...domain.enums import AgentType, VoiceSessionStatus, CallStatus
from ...core.config import settings
from .voice_agent_tools import (
    create_voice_agent_tools, VoiceAgentToolFactory, BaseVoiceAgentTool,
    VoiceAgentContext as EnhancedVoiceAgentContext
)

logger = logging.getLogger(__name__)


# =============================================================================
# VOICE AGENT TOOLS
# =============================================================================

@dataclass
class VoiceAgentContext:
    """Context for voice agent operations."""
    session_id: uuid.UUID
    business_id: uuid.UUID
    user_id: str
    agent_type: str
    participant_identity: Optional[str] = None
    dial_info: Optional[Dict[str, Any]] = None


class TransferCallTool:
    """Tool for transferring calls to human agents."""
    
    @property
    def name(self) -> str:
        return "transfer_call"
    
    @property
    def description(self) -> str:
        return "Transfer the call to a human agent when requested by the customer"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute call transfer to human agent."""
        try:
            # Get transfer number from dial info or use default
            transfer_to = None
            if context.dial_info and "transfer_to" in context.dial_info:
                transfer_to = context.dial_info["transfer_to"]
            elif settings.SIP_DEFAULT_TRANSFER_NUMBER:
                transfer_to = settings.SIP_DEFAULT_TRANSFER_NUMBER
            
            if not transfer_to:
                return {
                    "success": False,
                    "message": "No transfer number available",
                    "action": "inform_customer"
                }
            
            logger.info(f"Transferring call {context.session_id} to {transfer_to}")
            
            return {
                "success": True,
                "message": f"Transferring you to our human agent",
                "transfer_to": transfer_to,
                "action": "execute_transfer"
            }
            
        except Exception as e:
            logger.error(f"Failed to transfer call: {str(e)}")
            return {
                "success": False,
                "message": "There was an error transferring the call",
                "error": str(e),
                "action": "apologize_and_continue"
            }


class EndCallTool:
    """Tool for ending calls gracefully."""
    
    @property
    def name(self) -> str:
        return "end_call"
    
    @property
    def description(self) -> str:
        return "End the call when the conversation is complete or customer wants to hang up"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute call termination."""
        try:
            reason = kwargs.get("reason", "conversation_complete")
            logger.info(f"Ending call {context.session_id} - reason: {reason}")
            
            return {
                "success": True,
                "message": "Thank you for your time. Have a great day!",
                "reason": reason,
                "action": "end_call"
            }
            
        except Exception as e:
            logger.error(f"Failed to end call: {str(e)}")
            return {
                "success": False,
                "message": "There was an error ending the call",
                "error": str(e),
                "action": "continue_conversation"
            }


class DetectedAnsweringMachineTool:
    """Tool for handling answering machine detection."""
    
    @property
    def name(self) -> str:
        return "detected_answering_machine"
    
    @property
    def description(self) -> str:
        return "Handle detection of answering machine or voicemail"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute answering machine handling."""
        try:
            logger.info(f"Answering machine detected for call {context.session_id}")
            voicemail_message = kwargs.get("voicemail_message", "")
            
            return {
                "success": True,
                "message": voicemail_message or "Hello, this is Hero365 calling. We'll try to reach you again later.",
                "detected_at": datetime.utcnow().isoformat(),
                "action": "leave_voicemail_and_hangup"
            }
            
        except Exception as e:
            logger.error(f"Failed to handle answering machine: {str(e)}")
            return {
                "success": False,
                "message": "Error handling voicemail",
                "error": str(e),
                "action": "hangup"
            }


class LookupAvailabilityTool:
    """Tool for looking up appointment availability."""
    
    @property
    def name(self) -> str:
        return "look_up_availability"
    
    @property
    def description(self) -> str:
        return "Look up available appointment times for scheduling"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute availability lookup."""
        try:
            date = kwargs.get("date", "")
            logger.info(f"Looking up availability for {context.business_id} on {date}")
            
            # In a real implementation, this would query the scheduling system
            return {
                "success": True,
                "date": date,
                "available_times": ["9:00 AM", "11:00 AM", "2:00 PM", "4:00 PM"],
                "message": f"We have availability on {date} at 9 AM, 11 AM, 2 PM, and 4 PM"
            }
            
        except Exception as e:
            logger.error(f"Failed to lookup availability: {str(e)}")
            return {
                "success": False,
                "message": "I'm having trouble checking our schedule right now",
                "error": str(e)
            }


class ConfirmAppointmentTool:
    """Tool for confirming appointments."""
    
    @property
    def name(self) -> str:
        return "confirm_appointment"
    
    @property
    def description(self) -> str:
        return "Confirm an appointment when customer agrees to a specific date and time"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute appointment confirmation."""
        try:
            date = kwargs.get("date", "")
            time = kwargs.get("time", "")
            logger.info(f"Confirming appointment for {context.business_id} on {date} at {time}")
            
            return {
                "success": True,
                "date": date,
                "time": time,
                "message": f"Perfect! I've confirmed your appointment for {date} at {time}",
                "confirmation_number": f"CONF-{uuid.uuid4().hex[:8].upper()}"
            }
            
        except Exception as e:
            logger.error(f"Failed to confirm appointment: {str(e)}")
            return {
                "success": False,
                "message": "I'm having trouble confirming that appointment right now",
                "error": str(e)
            }


class LeadQualificationTool:
    """Tool for qualifying leads during outbound calls."""
    
    @property
    def name(self) -> str:
        return "lead_qualification"
    
    @property
    def description(self) -> str:
        return "Qualify leads by asking relevant questions and scoring responses"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute lead qualification."""
        try:
            responses = kwargs.get("responses", {})
            logger.info(f"Qualifying lead for {context.business_id}")
            
            # Simple scoring based on responses
            score = 0
            if responses.get("interested", False):
                score += 30
            if responses.get("timeline", "").lower() in ["immediate", "asap", "soon"]:
                score += 25
            if responses.get("budget_confirmed", False):
                score += 25
            if responses.get("decision_maker", False):
                score += 20
            
            qualification_level = "cold"
            if score >= 70:
                qualification_level = "hot"
            elif score >= 50:
                qualification_level = "warm"
            
            return {
                "success": True,
                "qualification_score": score,
                "qualification_level": qualification_level,
                "responses": responses,
                "message": f"Lead qualified as {qualification_level} with score {score}/100"
            }
            
        except Exception as e:
            logger.error(f"Failed to qualify lead: {str(e)}")
            return {
                "success": False,
                "message": "Error processing lead qualification",
                "error": str(e)
            }


class CallOutcomeLoggingTool:
    """Tool for logging call outcomes."""
    
    @property
    def name(self) -> str:
        return "call_outcome_logging"
    
    @property
    def description(self) -> str:
        return "Log the outcome of the call for tracking and follow-up"
    
    async def execute(self, context: VoiceAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute call outcome logging."""
        try:
            outcome = kwargs.get("outcome", "unknown")
            notes = kwargs.get("notes", "")
            follow_up_required = kwargs.get("follow_up_required", False)
            
            logger.info(f"Logging call outcome for {context.session_id}: {outcome}")
            
            return {
                "success": True,
                "outcome": outcome,
                "notes": notes,
                "follow_up_required": follow_up_required,
                "logged_at": datetime.utcnow().isoformat(),
                "message": "Call outcome logged successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to log call outcome: {str(e)}")
            return {
                "success": False,
                "message": "Error logging call outcome",
                "error": str(e)
            }


# =============================================================================
# AGENT CONFIGURATIONS
# =============================================================================

@dataclass
class AgentConfiguration:
    """Configuration for different agent types."""
    name: str
    description: str
    instructions: str
    tools: List[VoiceAgentTool]
    max_duration_minutes: int
    voice_settings: Dict[str, Any]


class LiveKitAgentConfigurations:
    """Predefined configurations for different agent types."""
    
    @staticmethod
    def get_personal_assistant_config() -> AgentConfiguration:
        """Get Personal Assistant configuration."""
        return AgentConfiguration(
            name="Hero365 Personal Assistant",
            description="AI assistant for hands-free business management",
            instructions="""You are Hero365's Personal Assistant, specialized in helping contractors and 
            home service professionals manage their business hands-free.
            
            PRIMARY CAPABILITIES:
            - Schedule and manage jobs and appointments
            - Update job statuses and field notes via voice
            - Check daily schedule and business metrics
            - Navigate to job locations with route optimization
            - Emergency scheduling and priority job handling
            - Voice-to-text field notes and photo tagging
            - Inventory checks and low-stock alerts
            - Client communication and follow-ups
            
            SAFETY & USABILITY:
            - Always prioritize safety for driving scenarios
            - Use voice-only interactions, avoid visual confirmations
            - Keep responses concise and actionable
            - Speak clearly and confirm important information
            - Handle emergency situations with highest priority
            
            Always ask clarifying questions if information is unclear.""",
            tools=[
                EndCallTool(),
                LookupAvailabilityTool(),
                ConfirmAppointmentTool()
            ],
            max_duration_minutes=30,
            voice_settings={
                "voice_id": "professional_male",
                "speaking_rate": 1.0,
                "pitch": 0.0,
                "stability": 0.75,
                "clarity": 0.85
            }
        )
    
    @staticmethod
    def get_outbound_caller_config() -> AgentConfiguration:
        """Get Outbound Caller configuration."""
        return AgentConfiguration(
            name="Hero365 Outbound Caller",
            description="AI agent for automated business calling and lead generation",
            instructions="""You are Hero365's Outbound Caller, designed to make professional automated calls 
            for lead generation, client communications, and business development.
            
            PRIMARY CAPABILITIES:
            - Lead qualification and nurturing calls
            - Appointment scheduling and confirmations
            - Client check-ins and satisfaction surveys
            - Follow-up calls for completed jobs
            - Payment reminders and collection calls
            - Campaign management and outcome tracking
            
            COMMUNICATION STYLE:
            - Professional, courteous, and friendly tone
            - Represent the business with integrity
            - Listen actively and respond appropriately
            - Handle objections gracefully
            - Follow call scripts when provided
            
            CALL MANAGEMENT:
            - Track call outcomes and schedule follow-ups
            - Handle voicemail professionally
            - Transfer to human when appropriate
            - Maintain detailed call records
            
            Always be honest about being an AI assistant and offer to connect
            with a human representative when requested.""",
            tools=[
                TransferCallTool(),
                EndCallTool(),
                DetectedAnsweringMachineTool(),
                LookupAvailabilityTool(),
                ConfirmAppointmentTool(),
                LeadQualificationTool(),
                CallOutcomeLoggingTool()
            ],
            max_duration_minutes=15,
            voice_settings={
                "voice_id": "professional_female",
                "speaking_rate": 0.9,
                "pitch": 0.1,
                "stability": 0.8,
                "clarity": 0.9
            }
        )
    
    @staticmethod
    def get_sales_agent_config() -> AgentConfiguration:
        """Get Sales Agent configuration."""
        return AgentConfiguration(
            name="Hero365 Sales Agent",
            description="AI agent for sales calls and lead conversion",
            instructions="""You are Hero365's Sales Agent, specialized in converting leads and closing sales.
            
            PRIMARY CAPABILITIES:
            - Lead qualification and conversion
            - Quote presentation and negotiation
            - Objection handling and closing techniques
            - Upselling and cross-selling opportunities
            - Sales pipeline management
            
            Always be professional, build rapport, and focus on solving customer problems.""",
            tools=[
                TransferCallTool(),
                EndCallTool(),
                DetectedAnsweringMachineTool(),
                LeadQualificationTool(),
                CallOutcomeLoggingTool()
            ],
            max_duration_minutes=20,
            voice_settings={
                "voice_id": "professional_female",
                "speaking_rate": 0.95,
                "pitch": 0.05,
                "stability": 0.85,
                "clarity": 0.9
            }
        )


# =============================================================================
# MAIN LIVEKIT VOICE AGENT SERVICE
# =============================================================================

class LiveKitVoiceAgentService(VoiceAgentServicePort):
    """
    Complete LiveKit voice agent service implementation.
    
    Handles voice sessions, outbound calls, tool management, and agent configurations
    all in one cohesive service.
    """
    
    def __init__(self, 
                 use_case_container: Any = None,
                 livekit_url: Optional[str] = None,
                 livekit_api_key: Optional[str] = None,
                 livekit_api_secret: Optional[str] = None,
                 openai_api_key: Optional[str] = None):
        
        if not LIVEKIT_AVAILABLE:
            raise ImportError("LiveKit packages are required. Install with: pip install livekit livekit-agents")
        
        # Store use case container for dependency injection
        self.use_case_container = use_case_container
        
        # LiveKit configuration
        self.livekit_url = livekit_url or settings.LIVEKIT_URL or "ws://localhost:7880"
        self.livekit_api_key = livekit_api_key or settings.LIVEKIT_API_KEY
        self.livekit_api_secret = livekit_api_secret or settings.LIVEKIT_API_SECRET
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not all([self.livekit_url, self.livekit_api_key, self.livekit_api_secret]):
            raise ValueError("LiveKit URL, API key, and secret must be provided")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for LLM functionality")
        
        # Initialize LiveKit API client
        self.livekit_api = api.LiveKitAPI(
            url=self.livekit_url,
            api_key=self.livekit_api_key,
            api_secret=self.livekit_api_secret
        )
        
        # Active sessions tracking
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize tool factory and advanced tools
        if self.use_case_container:
            self.tool_factory = VoiceAgentToolFactory(self.use_case_container)
            self.advanced_tools = self.tool_factory.create_all_tools()
        else:
            self.tool_factory = None
            self.advanced_tools = []
        
        # Agent configurations with enhanced tools
        self.agent_configs = {
            AgentType.PERSONAL_ASSISTANT: self._get_enhanced_personal_assistant_config(),
            AgentType.OUTBOUND_CALLER: self._get_enhanced_outbound_caller_config(),
            AgentType.SALES_AGENT: self._get_enhanced_sales_agent_config()
        }
        
        # Tool registry
        self.tools: Dict[str, VoiceAgentTool] = {}
        self.agent_tools: Dict[AgentType, Set[str]] = {
            AgentType.PERSONAL_ASSISTANT: set(),
            AgentType.OUTBOUND_CALLER: set(),
            AgentType.SALES_AGENT: set(),
            AgentType.EMERGENCY_RESPONSE: set()
        }
        
        # Register default tools
        self._register_default_tools()
        
        logger.info(f"LiveKit Voice Agent Service initialized with URL: {self.livekit_url}")
        if self.use_case_container:
            logger.info(f"Advanced tools registered: {len(self.advanced_tools)}")
    
    def _get_enhanced_personal_assistant_config(self) -> AgentConfiguration:
        """Get enhanced Personal Assistant configuration with advanced tools."""
        # Get base configuration
        base_config = LiveKitAgentConfigurations.get_personal_assistant_config()
        
        # Add advanced tools if available
        enhanced_tools = []
        enhanced_tools.extend(base_config.tools)  # Keep basic tools
        
        if self.advanced_tools:
            # Add specific advanced tools for personal assistant
            tool_names = [
                "advanced_availability_lookup",
                "intelligent_appointment_booking",
                "calendar_availability_check",
                "appointment_rescheduling",
                "customer_lookup",
                "emergency_scheduling"
            ]
            
            for tool in self.advanced_tools:
                if tool.name in tool_names:
                    enhanced_tools.append(tool)
        
        return AgentConfiguration(
            name=base_config.name,
            description=base_config.description,
            instructions=base_config.instructions,
            tools=enhanced_tools,
            max_duration_minutes=base_config.max_duration_minutes,
            voice_settings=base_config.voice_settings
        )
    
    def _get_enhanced_outbound_caller_config(self) -> AgentConfiguration:
        """Get enhanced Outbound Caller configuration with advanced tools."""
        # Get base configuration
        base_config = LiveKitAgentConfigurations.get_outbound_caller_config()
        
        # Add advanced tools if available
        enhanced_tools = []
        enhanced_tools.extend(base_config.tools)  # Keep basic tools
        
        if self.advanced_tools:
            # Add specific advanced tools for outbound caller
            tool_names = [
                "advanced_availability_lookup",
                "intelligent_appointment_booking",
                "customer_lookup",
                "intelligent_quote_generation"
            ]
            
            for tool in self.advanced_tools:
                if tool.name in tool_names:
                    enhanced_tools.append(tool)
        
        return AgentConfiguration(
            name=base_config.name,
            description=base_config.description,
            instructions=base_config.instructions,
            tools=enhanced_tools,
            max_duration_minutes=base_config.max_duration_minutes,
            voice_settings=base_config.voice_settings
        )
    
    def _get_enhanced_sales_agent_config(self) -> AgentConfiguration:
        """Get enhanced Sales Agent configuration with advanced tools."""
        # Get base configuration
        base_config = LiveKitAgentConfigurations.get_sales_agent_config()
        
        # Add advanced tools if available
        enhanced_tools = []
        enhanced_tools.extend(base_config.tools)  # Keep basic tools
        
        if self.advanced_tools:
            # Add specific advanced tools for sales agent
            tool_names = [
                "customer_lookup",
                "intelligent_quote_generation",
                "estimate_to_invoice_conversion",
                "advanced_availability_lookup",
                "intelligent_appointment_booking"
            ]
            
            for tool in self.advanced_tools:
                if tool.name in tool_names:
                    enhanced_tools.append(tool)
        
        return AgentConfiguration(
            name=base_config.name,
            description=base_config.description,
            instructions=base_config.instructions,
            tools=enhanced_tools,
            max_duration_minutes=base_config.max_duration_minutes,
            voice_settings=base_config.voice_settings
        )
    
    def _register_default_tools(self):
        """Register default tools for each agent type."""
        # Register tools from configurations
        for agent_type, config in self.agent_configs.items():
            for tool in config.tools:
                # Handle both old simple tools and new advanced tools
                tool_name = tool.name if hasattr(tool, 'name') else getattr(tool, '__class__').__name__
                self.tools[tool_name] = tool
                self.agent_tools[agent_type].add(tool_name)
        
        # Register advanced tools separately for easier access
        if self.advanced_tools:
            for tool in self.advanced_tools:
                self.tools[tool.name] = tool
    
    async def create_voice_session(self, config: VoiceSessionConfig) -> VoiceAgentResult:
        """Create a new voice session."""
        try:
            session_id = uuid.uuid4()
            room_name = f"voice_session_{session_id}"
            
            # Get agent configuration
            agent_config = self.agent_configs.get(config.agent_type)
            if not agent_config:
                raise ValueError(f"No configuration found for agent type: {config.agent_type}")
            
            # Create LiveKit room configuration
            room_config = LiveKitRoomConfig(
                room_name=room_name,
                participant_identity=str(config.user_id),
                participant_name=f"User_{config.user_id}",
                participant_metadata={
                    "user_id": str(config.user_id),
                    "business_id": str(config.business_id),
                    "agent_type": config.agent_type.value,
                    "session_id": str(session_id)
                },
                room_metadata={
                    "session_type": "voice_assistant",
                    "agent_type": config.agent_type.value,
                    "business_id": str(config.business_id),
                    "language": config.language,
                    "emergency_mode": str(config.emergency_mode)
                }
            )
            
            # Create room and get join token
            join_token = await self.create_room_token(room_config)
            
            # Get available tools for agent
            available_tools = await self.get_available_tools(config.agent_type)
            
            # Store session information
            session_info = {
                "session_id": session_id,
                "room_name": room_name,
                "agent_type": config.agent_type,
                "business_id": config.business_id,
                "user_id": config.user_id,
                "language": config.language,
                "emergency_mode": config.emergency_mode,
                "tools": available_tools,
                "created_at": datetime.utcnow(),
                "status": VoiceSessionStatus.INITIALIZING.value
            }
            
            self.active_sessions[str(session_id)] = session_info
            
            # Start agent worker (this would be handled by the worker process)
            await self._start_agent_worker(session_info, config)
            
            return VoiceAgentResult(
                success=True,
                session_id=session_id,
                room_name=room_name,
                join_token=join_token,
                metadata={
                    "agent_type": config.agent_type.value,
                    "available_tools": available_tools,
                    "emergency_mode": config.emergency_mode,
                    "agent_name": agent_config.name
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create voice session: {str(e)}")
            return VoiceAgentResult(
                success=False,
                error_message=str(e),
                error_code="SESSION_CREATION_FAILED"
            )
    
    async def create_outbound_call(self, config: OutboundCallConfig) -> VoiceAgentResult:
        """Create a new outbound call session."""
        try:
            call_id = uuid.uuid4()
            room_name = f"outbound_call_{call_id}"
            participant_identity = f"caller_{call_id}"
            
            # Create LiveKit room for outbound call
            room_config = LiveKitRoomConfig(
                room_name=room_name,
                participant_identity=participant_identity,
                participant_name=f"Caller_{config.business_id}",
                participant_metadata={
                    "business_id": str(config.business_id),
                    "agent_type": AgentType.OUTBOUND_CALLER.value,
                    "call_id": str(call_id),
                    "recipient_phone": config.recipient_phone,
                    "recipient_name": config.recipient_name,
                    "sip_trunk_id": config.sip_trunk_id,
                    "dial_info": config.dial_info
                },
                room_metadata={
                    "session_type": "outbound_call",
                    "agent_type": AgentType.OUTBOUND_CALLER.value,
                    "business_id": str(config.business_id),
                    "campaign_id": str(config.campaign_id) if config.campaign_id else None,
                    "priority": str(config.priority),
                    "sip_trunk_id": config.sip_trunk_id,
                    "transfer_to": config.transfer_to
                }
            )
            
            # Create room and get join token
            join_token = await self.create_room_token(room_config)
            
            # Get available tools for outbound caller
            available_tools = await self.get_available_tools(AgentType.OUTBOUND_CALLER)
            
            # Store call information
            call_info = {
                "call_id": call_id,
                "room_name": room_name,
                "participant_identity": participant_identity,
                "agent_type": AgentType.OUTBOUND_CALLER,
                "business_id": config.business_id,
                "recipient_phone": config.recipient_phone,
                "recipient_name": config.recipient_name,
                "campaign_id": config.campaign_id,
                "priority": config.priority,
                "tools": available_tools,
                "created_at": datetime.utcnow(),
                "status": CallStatus.SCHEDULED.value,
                "sip_trunk_id": config.sip_trunk_id,
                "transfer_to": config.transfer_to,
                "wait_until_answered": config.wait_until_answered,
                "max_attempts": config.max_attempts,
                "agent_instructions": config.agent_instructions,
                "dial_info": config.dial_info
            }
            
            self.active_sessions[str(call_id)] = call_info
            
            # Start outbound call agent worker
            await self._start_outbound_call_worker(call_info, config)
            
            return VoiceAgentResult(
                success=True,
                session_id=call_id,
                room_name=room_name,
                join_token=join_token,
                metadata={
                    "agent_type": AgentType.OUTBOUND_CALLER.value,
                    "recipient_phone": config.recipient_phone,
                    "recipient_name": config.recipient_name,
                    "available_tools": available_tools,
                    "priority": config.priority,
                    "sip_trunk_id": config.sip_trunk_id,
                    "transfer_to": config.transfer_to,
                    "dial_info": config.dial_info
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create outbound call: {str(e)}")
            return VoiceAgentResult(
                success=False,
                error_message=str(e),
                error_code="OUTBOUND_CALL_CREATION_FAILED"
            )
    
    async def end_voice_session(self, session_id: uuid.UUID) -> VoiceAgentResult:
        """End an active voice session."""
        try:
            session_key = str(session_id)
            
            if session_key not in self.active_sessions:
                return VoiceAgentResult(
                    success=False,
                    error_message="Session not found",
                    error_code="SESSION_NOT_FOUND"
                )
            
            session_info = self.active_sessions[session_key]
            room_name = session_info["room_name"]
            
            # End the LiveKit room
            await self.livekit_api.room.delete_room(
                api.DeleteRoomRequest(room=room_name)
            )
            
            # Update session status
            session_info["status"] = VoiceSessionStatus.ENDED.value
            session_info["ended_at"] = datetime.utcnow()
            
            # Remove from active sessions
            del self.active_sessions[session_key]
            
            return VoiceAgentResult(
                success=True,
                session_id=session_id,
                metadata={
                    "ended_at": session_info["ended_at"].isoformat(),
                    "duration_seconds": (session_info["ended_at"] - session_info["created_at"]).total_seconds()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to end voice session: {str(e)}")
            return VoiceAgentResult(
                success=False,
                error_message=str(e),
                error_code="SESSION_END_FAILED"
            )
    
    async def get_session_status(self, session_id: uuid.UUID) -> VoiceAgentResult:
        """Get current status of a voice session."""
        try:
            session_key = str(session_id)
            
            if session_key not in self.active_sessions:
                return VoiceAgentResult(
                    success=False,
                    error_message="Session not found",
                    error_code="SESSION_NOT_FOUND"
                )
            
            session_info = self.active_sessions[session_key]
            
            return VoiceAgentResult(
                success=True,
                session_id=session_id,
                metadata={
                    "status": session_info["status"],
                    "agent_type": session_info["agent_type"].value if hasattr(session_info["agent_type"], 'value') else session_info["agent_type"],
                    "created_at": session_info["created_at"].isoformat(),
                    "room_name": session_info["room_name"],
                    "emergency_mode": session_info.get("emergency_mode", False)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get session status: {str(e)}")
            return VoiceAgentResult(
                success=False,
                error_message=str(e),
                error_code="SESSION_STATUS_FAILED"
            )
    
    async def transfer_call(self, session_id: uuid.UUID, transfer_to: str) -> VoiceAgentResult:
        """Transfer an active call to another number."""
        try:
            session_key = str(session_id)
            
            if session_key not in self.active_sessions:
                return VoiceAgentResult(
                    success=False,
                    error_message="Session not found",
                    error_code="SESSION_NOT_FOUND"
                )
            
            session_info = self.active_sessions[session_key]
            room_name = session_info["room_name"]
            participant_identity = session_info.get("participant_identity", f"caller_{session_id}")
            transfer_number = f"tel:{transfer_to}"
            
            logger.info(f"Transferring call {session_id} to {transfer_to}")
            
            # Use LiveKit SIP API to transfer the call
            await self.livekit_api.sip.transfer_sip_participant(
                api.TransferSIPParticipantRequest(
                    room_name=room_name,
                    participant_identity=participant_identity,
                    transfer_to=transfer_number
                )
            )
            
            # Update session status
            session_info["status"] = "transferred"
            session_info["transferred_to"] = transfer_to
            session_info["transferred_at"] = datetime.utcnow()
            
            logger.info(f"Successfully transferred call {session_id} to {transfer_to}")
            
            return VoiceAgentResult(
                success=True,
                session_id=session_id,
                metadata={
                    "transferred_to": transfer_to,
                    "transferred_at": session_info["transferred_at"].isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to transfer call: {str(e)}")
            return VoiceAgentResult(
                success=False,
                error_message=str(e),
                error_code="CALL_TRANSFER_FAILED"
            )
    
    async def hangup_call(self, session_id: uuid.UUID) -> VoiceAgentResult:
        """Hang up an active call."""
        try:
            session_key = str(session_id)
            
            if session_key not in self.active_sessions:
                return VoiceAgentResult(
                    success=False,
                    error_message="Session not found",
                    error_code="SESSION_NOT_FOUND"
                )
            
            session_info = self.active_sessions[session_key]
            room_name = session_info["room_name"]
            
            logger.info(f"Hanging up call {session_id}")
            
            # Delete the LiveKit room to end the call
            await self.livekit_api.room.delete_room(
                api.DeleteRoomRequest(room=room_name)
            )
            
            # Update session status
            session_info["status"] = "ended"
            session_info["ended_at"] = datetime.utcnow()
            
            # Remove from active sessions
            del self.active_sessions[session_key]
            
            logger.info(f"Successfully hung up call {session_id}")
            
            return VoiceAgentResult(
                success=True,
                session_id=session_id,
                metadata={
                    "ended_at": session_info["ended_at"].isoformat(),
                    "reason": "hangup"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to hang up call: {str(e)}")
            return VoiceAgentResult(
                success=False,
                error_message=str(e),
                error_code="CALL_HANGUP_FAILED"
            )
    
    async def handle_answering_machine(self, session_id: uuid.UUID) -> VoiceAgentResult:
        """Handle detection of answering machine/voicemail."""
        try:
            session_key = str(session_id)
            
            if session_key not in self.active_sessions:
                return VoiceAgentResult(
                    success=False,
                    error_message="Session not found",
                    error_code="SESSION_NOT_FOUND"
                )
            
            session_info = self.active_sessions[session_key]
            
            logger.info(f"Detected answering machine for call {session_id}")
            
            # Update session status
            session_info["status"] = "voicemail_detected"
            session_info["voicemail_detected_at"] = datetime.utcnow()
            
            # Log the answering machine detection
            outcome_note = f"Answering machine detected at {datetime.utcnow().isoformat()}"
            session_info["outcome_notes"] = session_info.get("outcome_notes", [])
            session_info["outcome_notes"].append(outcome_note)
            
            # Hang up the call after detection
            hangup_result = await self.hangup_call(session_id)
            
            return VoiceAgentResult(
                success=True,
                session_id=session_id,
                metadata={
                    "voicemail_detected": True,
                    "detected_at": session_info["voicemail_detected_at"].isoformat(),
                    "call_ended": hangup_result.success,
                    "outcome": "voicemail"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to handle answering machine: {str(e)}")
            return VoiceAgentResult(
                success=False,
                error_message=str(e),
                error_code="ANSWERING_MACHINE_HANDLING_FAILED"
            )
    
    async def register_voice_tool(self, tool: VoiceAgentTool, agent_types: List[AgentType]) -> bool:
        """Register a voice tool for use by agents."""
        try:
            self.tools[tool.name] = tool
            
            for agent_type in agent_types:
                if agent_type not in self.agent_tools:
                    self.agent_tools[agent_type] = set()
                self.agent_tools[agent_type].add(tool.name)
            
            logger.info(f"Registered voice tool '{tool.name}' for agent types: {[at.value for at in agent_types]}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register voice tool '{tool.name}': {str(e)}")
            return False
    
    async def unregister_voice_tool(self, tool_name: str) -> bool:
        """Unregister a voice tool."""
        try:
            if tool_name in self.tools:
                del self.tools[tool_name]
                
                # Remove from all agent types
                for agent_type in self.agent_tools:
                    self.agent_tools[agent_type].discard(tool_name)
                
                logger.info(f"Unregistered voice tool '{tool_name}'")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister voice tool '{tool_name}': {str(e)}")
            return False
    
    async def get_available_tools(self, agent_type: AgentType) -> List[str]:
        """Get list of available tools for an agent type."""
        if agent_type not in self.agent_tools:
            return []
        
        tool_names = self.agent_tools[agent_type]
        return [name for name in tool_names if name in self.tools]
    
    async def create_room_token(self, room_config: LiveKitRoomConfig) -> str:
        """Create a join token for a LiveKit room."""
        try:
            # Create access token
            token = api.AccessToken(
                api_key=self.livekit_api_key,
                api_secret=self.livekit_api_secret
            )
            
            # Set token permissions
            token.with_identity(room_config.participant_identity)
            token.with_name(room_config.participant_name)
            token.with_metadata(json.dumps(room_config.participant_metadata))
            
            # Add room permissions
            token.with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_config.room_name,
                    can_publish=True,
                    can_subscribe=True
                )
            )
            
            # Set token expiration (24 hours)
            token.with_ttl(timedelta(hours=24))
            
            return token.to_jwt()
            
        except Exception as e:
            logger.error(f"Failed to create room token: {str(e)}")
            raise
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Check if the voice agent service is healthy."""
        try:
            # Try to list rooms to check connectivity
            rooms = await self.livekit_api.room.list_rooms(api.ListRoomsRequest())
            
            return {
                "status": "healthy",
                "service": "livekit_voice_agent",
                "livekit_url": self.livekit_url,
                "active_sessions": len(self.active_sessions),
                "rooms_count": len(rooms.rooms) if rooms.rooms else 0,
                "available_agent_types": [at.value for at in self.agent_configs.keys()],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Voice agent service health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "service": "livekit_voice_agent",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _start_agent_worker(self, session_info: Dict[str, Any], config: VoiceSessionConfig):
        """Start the agent worker for a voice session."""
        logger.info(f"Starting agent worker for session {session_info['session_id']}")
        session_info["status"] = VoiceSessionStatus.ACTIVE.value
        
        # In a real implementation, this would:
        # 1. Connect to the LiveKit room
        # 2. Initialize the voice assistant with appropriate tools
        # 3. Set up STT/TTS/LLM pipeline
        # 4. Handle voice interactions
    
    async def _start_outbound_call_worker(self, call_info: Dict[str, Any], config: OutboundCallConfig):
        """Start the outbound call worker."""
        logger.info(f"Starting outbound call worker for call {call_info['call_id']}")
        call_info["status"] = CallStatus.DIALING.value
        
        # In a real implementation, this would:
        # 1. Initiate SIP call to recipient using config.sip_trunk_id
        # 2. Connect to LiveKit room when call is answered
        # 3. Start voice assistant with call script
        # 4. Handle call flow and outcome tracking
    
    def create_outbound_call_config(self,
                                  business_id: str,
                                  recipient_phone: str,
                                  recipient_name: str,
                                  call_purpose: str,
                                  campaign_id: Optional[str] = None,
                                  script_instructions: Optional[str] = None,
                                  priority: int = 1,
                                  sip_trunk_id: Optional[str] = None,
                                  transfer_to: Optional[str] = None,
                                  wait_until_answered: bool = True,
                                  max_attempts: int = 3) -> OutboundCallConfig:
        """Create configuration for an outbound call session."""
        
        # Create call-specific script instructions
        full_script_instructions = f"Call Purpose: {call_purpose}\n"
        if script_instructions:
            full_script_instructions += f"Script Instructions: {script_instructions}\n"
        
        # Create agent instructions based on call purpose
        agent_instructions = f"""
        You are making an outbound call for {call_purpose}.
        
        Recipient: {recipient_name}
        Phone: {recipient_phone}
        Business: {business_id}
        
        CALL MANAGEMENT:
        - Be professional and courteous at all times
        - Clearly identify yourself and your purpose
        - Listen actively and respond appropriately
        - If requested, transfer to human using the transfer_call tool
        - Handle objections gracefully
        - End call politely when appropriate
        
        AVAILABLE ACTIONS:
        - transfer_call: Transfer to human agent when requested
        - end_call: End the call when conversation is complete
        - detected_answering_machine: Handle voicemail detection
        
        {full_script_instructions}
        """
        
        return OutboundCallConfig(
            business_id=business_id,
            recipient_phone=recipient_phone,
            recipient_name=recipient_name,
            campaign_id=campaign_id,
            script_instructions=full_script_instructions,
            agent_instructions=agent_instructions,
            max_duration_minutes=15,  # Default for outbound calls
            priority=priority,
            max_attempts=max_attempts,
            tools=["transfer_call", "end_call", "detected_answering_machine", "lead_qualification"],
            sip_trunk_id=sip_trunk_id or settings.SIP_OUTBOUND_TRUNK_ID,
            transfer_to=transfer_to or settings.SIP_DEFAULT_TRANSFER_NUMBER,
            wait_until_answered=wait_until_answered
        )


# Factory function for dependency injection
def create_livekit_voice_agent_service(use_case_container: Any = None) -> LiveKitVoiceAgentService:
    """Create LiveKit voice agent service instance with dependency injection."""
    return LiveKitVoiceAgentService(use_case_container=use_case_container) 