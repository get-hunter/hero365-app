"""
LiveKit Voice Agent Service Adapter with Multi-Agent Handoff

Implementation of VoiceAgentServicePort using LiveKit Agents 1.0.
Provides voice session management, agent creation, and tool integration
with support for multi-agent handoff and specialized agent roles.
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
from ...domain.entities.voice_session import VoiceSession
from ...domain.entities.outbound_call import OutboundCall
from ...core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class AgentHandoffContext:
    """Context information for agent handoff."""
    from_agent: AgentType
    to_agent: AgentType
    reason: str
    conversation_summary: str
    business_context: Dict[str, Any]
    user_intent: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentCapabilities:
    """Defines what an agent can handle."""
    name: str
    description: str
    primary_skills: List[str]
    handoff_triggers: List[str]
    confidence_threshold: float = 0.7


class Hero365BaseAgent(ABC):
    """Abstract base class for Hero365 specialized agents."""
    
    def __init__(self, agent_type: AgentType, capabilities: AgentCapabilities):
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.is_active = False
        self.conversation_context: Dict[str, Any] = {}
    
    @abstractmethod
    async def can_handle_request(self, intent: str, context: Dict[str, Any]) -> float:
        """Return confidence score (0-1) for handling the request."""
        pass
    
    @abstractmethod
    async def should_handoff(self, intent: str, context: Dict[str, Any]) -> Optional[AgentType]:
        """Determine if request should be handed off to another agent."""
        pass
    
    @abstractmethod
    async def prepare_handoff(self, to_agent: AgentType, context: Dict[str, Any]) -> AgentHandoffContext:
        """Prepare context for handoff to another agent."""
        pass
    
    @abstractmethod
    async def receive_handoff(self, handoff_context: AgentHandoffContext) -> Dict[str, Any]:
        """Process handoff from another agent."""
        pass


class Hero365PersonalAssistant(Hero365BaseAgent):
    """Personal Assistant Agent for daily business management."""
    
    def __init__(self):
        capabilities = AgentCapabilities(
            name="Personal Assistant",
            description="Handles daily business management, scheduling, and hands-free operations",
            primary_skills=[
                "schedule_management", "job_updates", "navigation", "emergency_handling",
                "voice_notes", "inventory_check", "business_metrics"
            ],
            handoff_triggers=[
                "outbound_call", "lead_generation", "campaign_management",
                "advanced_analytics", "financial_reporting"
            ]
        )
        super().__init__(AgentType.PERSONAL_ASSISTANT, capabilities)
    
    async def can_handle_request(self, intent: str, context: Dict[str, Any]) -> float:
        """Evaluate if this agent can handle the request."""
        personal_assistant_intents = {
            "schedule_job": 0.9,
            "update_job_status": 0.9,
            "get_schedule": 0.9,
            "navigate_to_job": 0.9,
            "add_note": 0.9,
            "check_inventory": 0.8,
            "emergency_schedule": 0.95,
            "voice_memo": 0.9,
            "business_metrics": 0.7,
            "client_communication": 0.6,
            "general_query": 0.7
        }
        
        return personal_assistant_intents.get(intent, 0.3)
    
    async def should_handoff(self, intent: str, context: Dict[str, Any]) -> Optional[AgentType]:
        """Determine if request should be handed off."""
        outbound_call_intents = [
            "make_call", "schedule_call", "lead_generation", "client_follow_up",
            "campaign_management", "bulk_calling", "supplier_communication"
        ]
        
        if intent in outbound_call_intents:
            return AgentType.OUTBOUND_CALLER
        
        # Check for emergency situations that need immediate response
        if intent == "emergency_schedule" and context.get("severity") == "critical":
            return AgentType.EMERGENCY_RESPONSE
        
        return None
    
    async def prepare_handoff(self, to_agent: AgentType, context: Dict[str, Any]) -> AgentHandoffContext:
        """Prepare handoff context."""
        summary = f"User was working on {context.get('current_task', 'general business management')}"
        
        return AgentHandoffContext(
            from_agent=self.agent_type,
            to_agent=to_agent,
            reason=f"Request requires {to_agent.value} capabilities",
            conversation_summary=summary,
            business_context=context.get("business_context", {}),
            user_intent=context.get("intent", "unknown")
        )
    
    async def receive_handoff(self, handoff_context: AgentHandoffContext) -> Dict[str, Any]:
        """Process handoff from another agent."""
        self.conversation_context.update(handoff_context.business_context)
        
        return {
            "handoff_received": True,
            "previous_agent": handoff_context.from_agent.value,
            "context_summary": handoff_context.conversation_summary,
            "greeting": f"I'm back to help you with your daily business management. {handoff_context.conversation_summary}"
        }


class Hero365OutboundCaller(Hero365BaseAgent):
    """Outbound Caller Agent for automated business calling."""
    
    def __init__(self):
        capabilities = AgentCapabilities(
            name="Outbound Caller",
            description="Handles automated calling, lead generation, and client communication",
            primary_skills=[
                "lead_generation", "appointment_scheduling", "client_follow_up",
                "supplier_communication", "payment_reminders", "campaign_management"
            ],
            handoff_triggers=[
                "schedule_management", "emergency_situation", "technical_support",
                "detailed_analysis", "hands_free_operation"
            ]
        )
        super().__init__(AgentType.OUTBOUND_CALLER, capabilities)
    
    async def can_handle_request(self, intent: str, context: Dict[str, Any]) -> float:
        """Evaluate if this agent can handle the request."""
        outbound_call_intents = {
            "make_call": 0.95,
            "schedule_call": 0.9,
            "lead_generation": 0.95,
            "client_follow_up": 0.9,
            "campaign_management": 0.9,
            "bulk_calling": 0.95,
            "supplier_communication": 0.8,
            "payment_reminders": 0.9,
            "appointment_scheduling": 0.8,
            "client_communication": 0.8
        }
        
        return outbound_call_intents.get(intent, 0.2)
    
    async def should_handoff(self, intent: str, context: Dict[str, Any]) -> Optional[AgentType]:
        """Determine if request should be handed off."""
        personal_assistant_intents = [
            "schedule_job", "update_job_status", "navigate_to_job",
            "add_note", "check_inventory", "voice_memo"
        ]
        
        if intent in personal_assistant_intents:
            return AgentType.PERSONAL_ASSISTANT
        
        # Emergency situations should be handled by emergency response
        if "emergency" in intent or context.get("priority") == "urgent":
            return AgentType.EMERGENCY_RESPONSE
        
        return None
    
    async def prepare_handoff(self, to_agent: AgentType, context: Dict[str, Any]) -> AgentHandoffContext:
        """Prepare handoff context."""
        summary = f"User was managing outbound calls and campaigns"
        
        return AgentHandoffContext(
            from_agent=self.agent_type,
            to_agent=to_agent,
            reason=f"Request requires {to_agent.value} capabilities",
            conversation_summary=summary,
            business_context=context.get("business_context", {}),
            user_intent=context.get("intent", "unknown")
        )
    
    async def receive_handoff(self, handoff_context: AgentHandoffContext) -> Dict[str, Any]:
        """Process handoff from another agent."""
        self.conversation_context.update(handoff_context.business_context)
        
        return {
            "handoff_received": True,
            "previous_agent": handoff_context.from_agent.value,
            "context_summary": handoff_context.conversation_summary,
            "greeting": f"I'm ready to help with your calling and communication needs. {handoff_context.conversation_summary}"
        }


class Hero365EmergencyResponse(Hero365BaseAgent):
    """Emergency Response Agent for urgent situations."""
    
    def __init__(self):
        capabilities = AgentCapabilities(
            name="Emergency Response",
            description="Handles urgent situations, emergency scheduling, and crisis management",
            primary_skills=[
                "emergency_scheduling", "crisis_management", "urgent_communication",
                "safety_protocols", "rapid_response", "priority_routing"
            ],
            handoff_triggers=[
                "routine_tasks", "non_urgent_requests", "standard_operations"
            ]
        )
        super().__init__(AgentType.EMERGENCY_RESPONSE, capabilities)
    
    async def can_handle_request(self, intent: str, context: Dict[str, Any]) -> float:
        """Evaluate if this agent can handle the request."""
        emergency_intents = {
            "emergency_schedule": 0.95,
            "crisis_management": 0.95,
            "urgent_communication": 0.9,
            "safety_incident": 0.95,
            "equipment_failure": 0.9,
            "client_emergency": 0.9,
            "weather_emergency": 0.9
        }
        
        # Check for emergency keywords in context
        if context.get("priority") == "urgent" or context.get("severity") == "critical":
            return 0.9
        
        return emergency_intents.get(intent, 0.1)
    
    async def should_handoff(self, intent: str, context: Dict[str, Any]) -> Optional[AgentType]:
        """Determine if request should be handed off."""
        # After handling emergency, hand back to appropriate agent
        if context.get("emergency_resolved", False):
            if "call" in intent or "communication" in intent:
                return AgentType.OUTBOUND_CALLER
            else:
                return AgentType.PERSONAL_ASSISTANT
        
        return None
    
    async def prepare_handoff(self, to_agent: AgentType, context: Dict[str, Any]) -> AgentHandoffContext:
        """Prepare handoff context."""
        summary = f"Emergency situation handled: {context.get('emergency_type', 'unknown')}"
        
        return AgentHandoffContext(
            from_agent=self.agent_type,
            to_agent=to_agent,
            reason="Emergency resolved, returning to normal operations",
            conversation_summary=summary,
            business_context=context.get("business_context", {}),
            user_intent=context.get("intent", "unknown")
        )
    
    async def receive_handoff(self, handoff_context: AgentHandoffContext) -> Dict[str, Any]:
        """Process handoff from another agent."""
        self.conversation_context.update(handoff_context.business_context)
        
        return {
            "handoff_received": True,
            "previous_agent": handoff_context.from_agent.value,
            "context_summary": handoff_context.conversation_summary,
            "greeting": "I'm here to handle this urgent situation immediately. What's the emergency?"
        }


class AgentHandoffOrchestrator:
    """Enhanced orchestrator with sophisticated agent triage system."""
    
    def __init__(self):
        self.agents = {
            AgentType.PERSONAL_ASSISTANT: Hero365PersonalAssistant(),
            AgentType.OUTBOUND_CALLER: Hero365OutboundCaller(),
            AgentType.EMERGENCY_RESPONSE: Hero365EmergencyResponse()
        }
        self.current_agent: Optional[AgentType] = None
        self.handoff_history: List[AgentHandoffContext] = []
        
        # Enhanced triage configuration
        self.confidence_threshold = 0.7  # Minimum confidence to handle request
        self.disambiguation_threshold = 0.1  # Maximum score difference for disambiguation
        self.context_weights = {
            "priority": 0.3,
            "user_role": 0.2,
            "conversation_history": 0.2,
            "business_context": 0.15,
            "time_of_day": 0.1,
            "agent_performance": 0.05
        }
        
        # Agent performance tracking for learning
        self.agent_performance = {
            AgentType.PERSONAL_ASSISTANT: {"success_rate": 0.9, "avg_response_time": 2.5, "user_satisfaction": 0.85},
            AgentType.OUTBOUND_CALLER: {"success_rate": 0.88, "avg_response_time": 3.0, "user_satisfaction": 0.82},
            AgentType.EMERGENCY_RESPONSE: {"success_rate": 0.95, "avg_response_time": 1.5, "user_satisfaction": 0.9}
        }
    
    async def select_best_agent(self, intent: str, context: Dict[str, Any]) -> AgentType:
        """Enhanced agent selection with sophisticated triage logic."""
        # Emergency override - always prioritize emergency response for urgent situations
        if self._is_emergency_situation(intent, context):
            return AgentType.EMERGENCY_RESPONSE
        
        # Get base confidence scores from all agents
        agent_scores = {}
        for agent_type, agent in self.agents.items():
            base_score = await agent.can_handle_request(intent, context)
            
            # Apply context weighting and performance adjustments
            enhanced_score = await self._calculate_enhanced_score(agent_type, base_score, intent, context)
            agent_scores[agent_type] = enhanced_score
        
        # Apply sophisticated selection logic
        selected_agent = await self._apply_selection_logic(agent_scores, intent, context)
        
        # Log decision for learning
        await self._log_triage_decision(selected_agent, agent_scores, intent, context)
        
        return selected_agent
    
    def _is_emergency_situation(self, intent: str, context: Dict[str, Any]) -> bool:
        """Detect emergency situations with multiple criteria."""
        emergency_indicators = [
            # Priority/severity indicators
            context.get("priority") == "urgent",
            context.get("severity") == "critical",
            context.get("emergency_mode", False),
            
            # Intent-based indicators
            "emergency" in intent.lower(),
            "urgent" in intent.lower(),
            "crisis" in intent.lower(),
            "safety" in intent.lower(),
            "immediate" in intent.lower(),
            
            # Context-based indicators
            context.get("safety_incident", False),
            context.get("equipment_failure", False),
            context.get("client_emergency", False),
            
            # Time-sensitive indicators
            context.get("response_time_required", 0) < 300,  # Less than 5 minutes
        ]
        
        # Return True if any emergency indicator is present
        return any(emergency_indicators)
    
    async def _calculate_enhanced_score(self, agent_type: AgentType, base_score: float, 
                                      intent: str, context: Dict[str, Any]) -> float:
        """Calculate enhanced confidence score with context weighting."""
        if base_score <= 0.1:  # Skip enhancement for very low base scores
            return base_score
        
        enhanced_score = base_score
        
        # Apply context weighting
        context_multiplier = 1.0
        
        # Priority context weighting
        priority = context.get("priority", "medium")
        if agent_type == AgentType.EMERGENCY_RESPONSE and priority in ["urgent", "high"]:
            context_multiplier += 0.2
        elif agent_type != AgentType.EMERGENCY_RESPONSE and priority in ["low", "medium"]:
            context_multiplier += 0.1
        
        # User role context weighting
        user_role = context.get("user_role", "user")
        if user_role in ["admin", "manager"] and agent_type == AgentType.PERSONAL_ASSISTANT:
            context_multiplier += 0.1
        elif user_role == "sales" and agent_type == AgentType.OUTBOUND_CALLER:
            context_multiplier += 0.15
        
        # Conversation history weighting
        if self.current_agent == agent_type and context.get("conversation_continuity", False):
            context_multiplier += 0.1  # Slight preference for conversation continuity
        
        # Time of day weighting
        hour = context.get("hour_of_day", 12)
        if agent_type == AgentType.OUTBOUND_CALLER and 9 <= hour <= 17:  # Business hours
            context_multiplier += 0.05
        elif agent_type == AgentType.EMERGENCY_RESPONSE and (hour < 8 or hour > 18):  # Off hours
            context_multiplier += 0.1
        
        # Agent performance weighting
        perf = self.agent_performance.get(agent_type, {})
        performance_factor = (
            perf.get("success_rate", 0.8) * 0.4 +
            (1 - min(perf.get("avg_response_time", 3.0) / 5.0, 1.0)) * 0.3 +
            perf.get("user_satisfaction", 0.8) * 0.3
        )
        context_multiplier += (performance_factor - 0.8) * 0.1  # Adjust based on performance
        
        # Apply multiplier and ensure score stays within bounds
        enhanced_score = min(base_score * context_multiplier, 1.0)
        
        return enhanced_score
    
    async def _apply_selection_logic(self, agent_scores: Dict[AgentType, float], 
                                   intent: str, context: Dict[str, Any]) -> AgentType:
        """Apply sophisticated selection logic with fallbacks and disambiguation."""
        # Sort agents by score
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        best_agent, best_score = sorted_agents[0]
        second_agent, second_score = sorted_agents[1] if len(sorted_agents) > 1 else (None, 0)
        
        # Check if best agent meets confidence threshold
        if best_score < self.confidence_threshold:
            return await self._handle_low_confidence_scenario(agent_scores, intent, context)
        
        # Check for disambiguation scenario (scores are very close)
        if (second_agent and 
            abs(best_score - second_score) <= self.disambiguation_threshold and 
            second_score >= self.confidence_threshold):
            return await self._disambiguate_agents(best_agent, second_agent, agent_scores, intent, context)
        
        # Standard case: clear winner with high confidence
        return best_agent
    
    async def _handle_low_confidence_scenario(self, agent_scores: Dict[AgentType, float], 
                                            intent: str, context: Dict[str, Any]) -> AgentType:
        """Handle scenarios where no agent has high confidence."""
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        best_agent, best_score = sorted_agents[0]
        
        # If it's a complete unknown, default to Personal Assistant with escalation warning
        if best_score < 0.3:
            context["triage_warning"] = "Low confidence for all agents - defaulting to Personal Assistant"
            context["escalation_suggested"] = True
            return AgentType.PERSONAL_ASSISTANT
        
        # If moderate confidence (0.3-0.7), use contextual fallback rules
        if "call" in intent or "contact" in intent or "campaign" in intent:
            return AgentType.OUTBOUND_CALLER
        elif "schedule" in intent or "job" in intent or "navigate" in intent:
            return AgentType.PERSONAL_ASSISTANT
        else:
            # Default to best scoring agent even if below threshold
            context["triage_warning"] = f"Below confidence threshold ({best_score:.2f}) but proceeding"
            return best_agent
    
    async def _disambiguate_agents(self, agent1: AgentType, agent2: AgentType, 
                                 agent_scores: Dict[AgentType, float], 
                                 intent: str, context: Dict[str, Any]) -> AgentType:
        """Disambiguate between two agents with similar scores."""
        # Use conversation continuity as tiebreaker
        if self.current_agent in [agent1, agent2]:
            return self.current_agent
        
        # Use user preference if available
        user_preference = context.get("preferred_agent")
        if user_preference in [agent1, agent2]:
            return user_preference
        
        # Use agent performance as tiebreaker
        perf1 = self.agent_performance.get(agent1, {}).get("success_rate", 0.8)
        perf2 = self.agent_performance.get(agent2, {}).get("success_rate", 0.8)
        
        if abs(perf1 - perf2) > 0.05:  # Significant performance difference
            return agent1 if perf1 > perf2 else agent2
        
        # Use domain-specific tiebreakers
        business_hours = 9 <= context.get("hour_of_day", 12) <= 17
        
        if agent1 == AgentType.OUTBOUND_CALLER and business_hours:
            return agent1
        elif agent2 == AgentType.OUTBOUND_CALLER and business_hours:
            return agent2
        
        # Default to agent with slightly higher score
        return agent1 if agent_scores[agent1] >= agent_scores[agent2] else agent2
    
    async def _log_triage_decision(self, selected_agent: AgentType, 
                                 agent_scores: Dict[AgentType, float], 
                                 intent: str, context: Dict[str, Any]):
        """Log triage decision for learning and improvement."""
        decision_log = {
            "timestamp": datetime.utcnow(),
            "selected_agent": selected_agent.value,
            "agent_scores": {k.value: v for k, v in agent_scores.items()},
            "intent": intent,
            "context_factors": {
                "priority": context.get("priority"),
                "user_role": context.get("user_role"),
                "emergency_indicators": self._is_emergency_situation(intent, context),
                "confidence_threshold_met": max(agent_scores.values()) >= self.confidence_threshold
            }
        }
        
        # In production, this would be sent to analytics/learning system
        logger.info(f"Agent triage decision: {decision_log}")
    
    async def update_agent_performance(self, agent_type: AgentType, 
                                     success: bool, response_time: float, 
                                     user_satisfaction: Optional[float] = None):
        """Update agent performance metrics for learning."""
        if agent_type not in self.agent_performance:
            return
        
        perf = self.agent_performance[agent_type]
        
        # Update success rate (exponential moving average)
        alpha = 0.1  # Learning rate
        current_success = 1.0 if success else 0.0
        perf["success_rate"] = (1 - alpha) * perf["success_rate"] + alpha * current_success
        
        # Update average response time
        perf["avg_response_time"] = (1 - alpha) * perf["avg_response_time"] + alpha * response_time
        
        # Update user satisfaction if provided
        if user_satisfaction is not None:
            perf["user_satisfaction"] = (1 - alpha) * perf["user_satisfaction"] + alpha * user_satisfaction
        
        logger.info(f"Updated performance for {agent_type.value}: {perf}")
    
    async def should_handoff(self, intent: str, context: Dict[str, Any]) -> Optional[AgentType]:
        """Determine if current agent should hand off to another."""
        if not self.current_agent:
            return None
        
        current_agent = self.agents[self.current_agent]
        return await current_agent.should_handoff(intent, context)
    
    async def execute_handoff(self, to_agent: AgentType, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute handoff from current agent to target agent."""
        if not self.current_agent:
            # First agent selection
            self.current_agent = to_agent
            target_agent = self.agents[to_agent]
            await target_agent.receive_handoff(AgentHandoffContext(
                from_agent=AgentType.PERSONAL_ASSISTANT,  # Default
                to_agent=to_agent,
                reason="Initial agent selection",
                conversation_summary="Starting new conversation",
                business_context=context.get("business_context", {}),
                user_intent=context.get("intent", "unknown")
            ))
            return {"handoff_executed": True, "new_agent": to_agent.value}
        
        # Execute handoff
        from_agent = self.agents[self.current_agent]
        to_agent_instance = self.agents[to_agent]
        
        # Prepare handoff context
        handoff_context = await from_agent.prepare_handoff(to_agent, context)
        
        # Execute handoff
        handoff_result = await to_agent_instance.receive_handoff(handoff_context)
        
        # Update state
        self.current_agent = to_agent
        self.handoff_history.append(handoff_context)
        
        logger.info(f"Agent handoff executed: {handoff_context.from_agent.value} -> {handoff_context.to_agent.value}")
        
        return {
            "handoff_executed": True,
            "previous_agent": handoff_context.from_agent.value,
            "new_agent": handoff_context.to_agent.value,
            "handoff_reason": handoff_context.reason,
            "greeting": handoff_result.get("greeting", "")
        }
    
    async def get_current_agent_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of current agent."""
        if not self.current_agent:
            return {}
        
        agent = self.agents[self.current_agent]
        return {
            "agent_type": self.current_agent.value,
            "name": agent.capabilities.name,
            "description": agent.capabilities.description,
            "primary_skills": agent.capabilities.primary_skills,
            "handoff_triggers": agent.capabilities.handoff_triggers
        }


class LiveKitVoiceAgentAdapter(VoiceAgentServicePort):
    """
    LiveKit Agents 1.0 implementation with multi-agent handoff support.
    
    Provides voice session management, agent creation, and tool integration
    using LiveKit's real-time voice infrastructure with specialized agents.
    """
    
    def __init__(self, 
                 livekit_url: Optional[str] = None,
                 livekit_api_key: Optional[str] = None,
                 livekit_api_secret: Optional[str] = None,
                 openai_api_key: Optional[str] = None,
                 elevenlabs_api_key: Optional[str] = None,
                 deepgram_api_key: Optional[str] = None):
        
        if not LIVEKIT_AVAILABLE:
            raise ImportError("LiveKit packages are required. Install with: pip install livekit livekit-agents")
        
        # LiveKit configuration
        self.livekit_url = livekit_url or os.getenv("LIVEKIT_URL", "ws://localhost:7880")
        self.livekit_api_key = livekit_api_key or os.getenv("LIVEKIT_API_KEY")
        self.livekit_api_secret = livekit_api_secret or os.getenv("LIVEKIT_API_SECRET")
        
        # AI service configurations
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.elevenlabs_api_key = elevenlabs_api_key or os.getenv("ELEVENLABS_API_KEY")
        self.deepgram_api_key = deepgram_api_key or os.getenv("DEEPGRAM_API_KEY")
        
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
        
        # Multi-agent handoff orchestrator
        self.orchestrator = AgentHandoffOrchestrator()
        
        # Active sessions tracking with orchestrator per session
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_orchestrators: Dict[str, AgentHandoffOrchestrator] = {}
        
        # Tool registry
        self.tool_registry = InMemoryVoiceToolRegistry()
        
        # Voice command processor with multi-agent support
        self.command_processor = MultiAgentVoiceCommandProcessor(self.openai_api_key)
        
        # Enhanced agent configurations
        self.agent_configs = {
            AgentType.PERSONAL_ASSISTANT: {
                "name": "Hero365 Personal Assistant",
                "description": "AI assistant for hands-free business management",
                "instructions": """You are Hero365's Personal Assistant, designed to help contractors and 
                home service professionals manage their business hands-free while driving or working.
                
                Key capabilities:
                - Schedule and manage jobs and appointments
                - Update job statuses and notes
                - Check business metrics and reports
                - Navigate to job locations
                - Emergency scheduling and routing
                - Voice-to-text field notes
                - Photo tagging and organization
                
                MULTI-AGENT COORDINATION:
                - If user requests outbound calling, lead generation, or campaign management, 
                  hand off to Outbound Caller agent
                - For emergency situations, immediately hand off to Emergency Response agent
                - Always maintain conversation context during handoffs
                
                Always be concise, professional, and safety-focused. For driving scenarios, 
                prioritize voice-only interactions and avoid requesting visual confirmations.""",
                "handoff_phrases": [
                    "Let me connect you with our outbound calling specialist",
                    "I'm transferring you to our emergency response team",
                    "Our calling expert will handle this for you"
                ]
            },
            AgentType.OUTBOUND_CALLER: {
                "name": "Hero365 Outbound Caller",
                "description": "AI agent for automated business calling",
                "instructions": """You are Hero365's Outbound Caller, designed to make automated calls 
                for lead generation, client notifications, and business communications.
                
                Key capabilities:
                - Lead qualification and nurturing
                - Appointment scheduling and reminders
                - Client check-ins and follow-ups
                - Supplier communications
                - Payment reminders and collection
                - Campaign management and tracking
                
                MULTI-AGENT COORDINATION:
                - If user needs daily scheduling or job management, hand off to Personal Assistant
                - For emergency situations, immediately hand off to Emergency Response agent
                - Always maintain conversation context during handoffs
                
                Always be professional, courteous, and represent the business well. 
                Follow call scripts when provided, but adapt naturally to conversation flow.""",
                "handoff_phrases": [
                    "Let me connect you with our personal assistant for scheduling",
                    "I'm transferring you to our emergency response team",
                    "Our business assistant will help you with that"
                ]
            },
            AgentType.EMERGENCY_RESPONSE: {
                "name": "Hero365 Emergency Response",
                "description": "AI agent for urgent situations and crisis management",
                "instructions": """You are Hero365's Emergency Response Agent, designed to handle 
                urgent situations, emergency scheduling, and crisis management.
                
                Key capabilities:
                - Emergency job scheduling and routing
                - Crisis communication and coordination
                - Safety incident management
                - Urgent client communication
                - Equipment failure response
                - Weather emergency protocols
                
                MULTI-AGENT COORDINATION:
                - After resolving emergency, hand back to appropriate agent
                - For follow-up calls, hand off to Outbound Caller
                - For routine tasks post-emergency, hand off to Personal Assistant
                - Always maintain urgency and context during handoffs
                
                Always prioritize safety and urgency. Get critical information first, 
                then coordinate response. Be calm, professional, and decisive.""",
                "handoff_phrases": [
                    "Emergency handled. Connecting you back to your assistant",
                    "I'm transferring you to our calling specialist for follow-up",
                    "Returning you to normal operations"
                ]
            }
        }
        
        logger.info(f"LiveKit Multi-Agent Voice Adapter initialized with URL: {self.livekit_url}")
    
    async def create_voice_session(self, config: VoiceSessionConfig) -> VoiceAgentResult:
        """Create a new voice session with personal assistant."""
        try:
            # Generate session identifiers
            session_id = uuid.uuid4()
            room_name = f"voice_session_{session_id}"
            
            # Create LiveKit room
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
            
            # Create dedicated orchestrator for this session
            session_orchestrator = AgentHandoffOrchestrator()
            self.session_orchestrators[str(session_id)] = session_orchestrator
            
            # Store session information with multi-agent context
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
                "status": VoiceSessionStatus.INITIALIZING.value,
                "orchestrator_id": str(session_id)
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
                    "emergency_mode": config.emergency_mode
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
            # Generate call identifiers
            call_id = uuid.uuid4()
            room_name = f"outbound_call_{call_id}"
            
            # Create LiveKit room for outbound call
            room_config = LiveKitRoomConfig(
                room_name=room_name,
                participant_identity=f"caller_{call_id}",
                participant_name=f"Caller_{config.business_id}",
                participant_metadata={
                    "business_id": str(config.business_id),
                    "agent_type": AgentType.OUTBOUND_CALLER.value,
                    "call_id": str(call_id),
                    "recipient_phone": config.recipient_phone,
                    "recipient_name": config.recipient_name
                },
                room_metadata={
                    "session_type": "outbound_call",
                    "agent_type": AgentType.OUTBOUND_CALLER.value,
                    "business_id": str(config.business_id),
                    "campaign_id": str(config.campaign_id) if config.campaign_id else None,
                    "priority": str(config.priority)
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
                "agent_type": AgentType.OUTBOUND_CALLER,
                "business_id": config.business_id,
                "recipient_phone": config.recipient_phone,
                "recipient_name": config.recipient_name,
                "campaign_id": config.campaign_id,
                "priority": config.priority,
                "tools": available_tools,
                "created_at": datetime.utcnow(),
                "status": CallStatus.SCHEDULED.value
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
                    "priority": config.priority
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
            
            # Remove from active sessions and cleanup orchestrator
            del self.active_sessions[session_key]
            if session_key in self.session_orchestrators:
                del self.session_orchestrators[session_key]
            
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
    
    async def register_voice_tool(self, tool: VoiceAgentTool, agent_types: List[AgentType]) -> bool:
        """Register a voice tool for use by agents."""
        return await self.tool_registry.register_tool(tool, agent_types)
    
    async def unregister_voice_tool(self, tool_name: str) -> bool:
        """Unregister a voice tool."""
        return await self.tool_registry.unregister_tool(tool_name)
    
    async def get_available_tools(self, agent_type: AgentType) -> List[str]:
        """Get list of available tools for an agent type."""
        tools = await self.tool_registry.get_tools_for_agent(agent_type)
        return [tool.name for tool in tools]
    
    async def execute_agent_handoff(self, session_id: uuid.UUID, intent: str, context: Dict[str, Any]) -> VoiceAgentResult:
        """Execute agent handoff for a voice session."""
        try:
            session_key = str(session_id)
            
            if session_key not in self.active_sessions:
                return VoiceAgentResult(
                    success=False,
                    error_message="Session not found",
                    error_code="SESSION_NOT_FOUND"
                )
            
            if session_key not in self.session_orchestrators:
                return VoiceAgentResult(
                    success=False,
                    error_message="Session orchestrator not found",
                    error_code="ORCHESTRATOR_NOT_FOUND"
                )
            
            orchestrator = self.session_orchestrators[session_key]
            session_info = self.active_sessions[session_key]
            
            # Add business context to handoff context
            handoff_context = {
                "intent": intent,
                "business_context": {
                    "business_id": session_info["business_id"],
                    "user_id": session_info["user_id"],
                    "language": session_info["language"],
                    "emergency_mode": session_info["emergency_mode"]
                },
                **context
            }
            
            # Check if handoff is needed
            target_agent = await orchestrator.should_handoff(intent, handoff_context)
            
            if target_agent:
                # Execute handoff
                handoff_result = await orchestrator.execute_handoff(target_agent, handoff_context)
                
                # Update session info with new agent
                session_info["agent_type"] = target_agent
                session_info["last_handoff"] = datetime.utcnow()
                
                return VoiceAgentResult(
                    success=True,
                    session_id=session_id,
                    metadata=handoff_result
                )
            else:
                # No handoff needed, select best agent for initial request
                best_agent = await orchestrator.select_best_agent(intent, handoff_context)
                
                if best_agent != orchestrator.current_agent:
                    handoff_result = await orchestrator.execute_handoff(best_agent, handoff_context)
                    
                    # Update session info with new agent
                    session_info["agent_type"] = best_agent
                    session_info["last_handoff"] = datetime.utcnow()
                    
                    return VoiceAgentResult(
                        success=True,
                        session_id=session_id,
                        metadata=handoff_result
                    )
            
            return VoiceAgentResult(
                success=True,
                session_id=session_id,
                metadata={"handoff_needed": False, "current_agent": orchestrator.current_agent.value if orchestrator.current_agent else "none"}
            )
            
        except Exception as e:
            logger.error(f"Failed to execute agent handoff: {str(e)}")
            return VoiceAgentResult(
                success=False,
                error_message=str(e),
                error_code="HANDOFF_EXECUTION_FAILED"
            )
    
    async def get_current_agent_info(self, session_id: uuid.UUID) -> VoiceAgentResult:
        """Get current agent information for a session."""
        try:
            session_key = str(session_id)
            
            if session_key not in self.session_orchestrators:
                return VoiceAgentResult(
                    success=False,
                    error_message="Session orchestrator not found",
                    error_code="ORCHESTRATOR_NOT_FOUND"
                )
            
            orchestrator = self.session_orchestrators[session_key]
            capabilities = await orchestrator.get_current_agent_capabilities()
            
            return VoiceAgentResult(
                success=True,
                session_id=session_id,
                metadata=capabilities
            )
            
        except Exception as e:
            logger.error(f"Failed to get current agent info: {str(e)}")
            return VoiceAgentResult(
                success=False,
                error_message=str(e),
                error_code="AGENT_INFO_FAILED"
            )
    
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
        # This would typically be handled by a separate worker process
        # For now, we'll just log the initialization
        logger.info(f"Starting agent worker for session {session_info['session_id']}")
        
        # Update session status
        session_info["status"] = VoiceSessionStatus.ACTIVE.value
        
        # In a real implementation, this would:
        # 1. Connect to the LiveKit room
        # 2. Initialize the voice assistant with appropriate tools
        # 3. Set up STT/TTS/LLM pipeline
        # 4. Handle voice interactions
    
    async def _start_outbound_call_worker(self, call_info: Dict[str, Any], config: OutboundCallConfig):
        """Start the outbound call worker."""
        # This would typically initiate the actual outbound call
        # For now, we'll just log the initialization
        logger.info(f"Starting outbound call worker for call {call_info['call_id']}")
        
        # Update call status
        call_info["status"] = CallStatus.DIALING.value
        
        # In a real implementation, this would:
        # 1. Initiate SIP call to recipient
        # 2. Connect to LiveKit room when call is answered
        # 3. Start voice assistant with call script
        # 4. Handle call flow and outcome tracking


class InMemoryVoiceToolRegistry(VoiceToolRegistry):
    """In-memory implementation of voice tool registry."""
    
    def __init__(self):
        self.tools: Dict[str, VoiceAgentTool] = {}
        self.agent_tools: Dict[AgentType, Set[str]] = {
            AgentType.PERSONAL_ASSISTANT: set(),
            AgentType.OUTBOUND_CALLER: set(),
            AgentType.EMERGENCY_RESPONSE: set()
        }
    
    async def register_tool(self, tool: VoiceAgentTool, agent_types: List[AgentType]) -> bool:
        """Register a voice tool for specific agent types."""
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
    
    async def unregister_tool(self, tool_name: str) -> bool:
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
    
    async def get_tools_for_agent(self, agent_type: AgentType) -> List[VoiceAgentTool]:
        """Get all tools available for an agent type."""
        if agent_type not in self.agent_tools:
            return []
        
        tool_names = self.agent_tools[agent_type]
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    async def get_tool_by_name(self, tool_name: str) -> Optional[VoiceAgentTool]:
        """Get a specific tool by name."""
        return self.tools.get(tool_name)


class MultiAgentVoiceCommandProcessor(VoiceCommandProcessor):
    """Multi-agent voice command processor with handoff decision support."""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        try:
            import openai
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
        except ImportError:
            raise ImportError("OpenAI package is required. Install with: pip install openai")
        
        # Conversation context management
        self.conversation_memory = {}  # Per session conversation history
        self.active_topics = {}        # Current conversation topics per session
        self.pending_actions = {}      # Actions waiting for confirmation/clarification
    
    async def process_conversational_input(self, 
                                         voice_input: str, 
                                         session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process conversational voice input with context and memory."""
        session_id = session_context.get("session_id", "default")
        
        # Get conversation history for this session
        conversation_history = self.conversation_memory.get(session_id, [])
        active_topic = self.active_topics.get(session_id, None)
        pending_action = self.pending_actions.get(session_id, None)
        
        try:
            # Build conversational context for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": self._build_conversational_system_prompt(session_context)
                }
            ]
            
            # Add conversation history (last 10 exchanges)
            messages.extend(conversation_history[-20:])  # Last 10 exchanges (user + assistant)
            
            # Add current input
            messages.append({
                "role": "user",
                "content": voice_input
            })
            
            # Process with OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Better for conversations
                messages=messages,
                temperature=0.3,  # Slightly more natural but still focused
                max_tokens=500
            )
            
            # Parse the conversational response
            result = json.loads(response.choices[0].message.content)
            
            # Update conversation memory
            self._update_conversation_memory(session_id, voice_input, result)
            
            # Handle conversational flow
            return await self._handle_conversational_flow(result, session_context)
            
        except Exception as e:
            logger.error(f"Failed to process conversational input: {str(e)}")
            return {
                "conversation_type": "error",
                "response": "I'm having trouble understanding right now. Could you repeat that?",
                "agent_action": "clarification_needed",
                "original_input": voice_input,
                "error": str(e)
            }
    
    def _build_conversational_system_prompt(self, session_context: Dict[str, Any]) -> str:
        """Build system prompt for conversational interaction."""
        user_name = session_context.get("user_name", "there")
        business_name = session_context.get("business_name", "your business")
        current_agent = session_context.get("current_agent", "personal_assistant")
        
        return f"""You are Hero365's voice assistant helping {user_name} manage {business_name}. 
        You're currently in {current_agent} mode and having a natural conversation.

        CONVERSATION STYLE:
        - Be natural, friendly, and conversational (not robotic commands)
        - Ask follow-up questions when you need clarification
        - Confirm actions before executing them
        - Maintain conversation context and remember what was discussed
        - Be proactive and suggest helpful next steps
        
        AVAILABLE AGENTS & WHEN TO HANDOFF:
        1. PERSONAL_ASSISTANT - Daily scheduling, job management, navigation, business operations
        2. OUTBOUND_CALLER - Making calls, lead generation, client communication, campaigns
        3. EMERGENCY_RESPONSE - Urgent situations, safety incidents, crisis management
        
        CONVERSATION TYPES:
        - "question" - User asking for information
        - "request" - User asking to do something
        - "clarification" - User providing more details/clarification
        - "confirmation" - User confirming or denying an action
        - "chat" - General conversation/small talk
        - "handoff_needed" - Need to switch to different agent
        
        RESPONSE FORMAT (JSON):
        {{
            "conversation_type": "question|request|clarification|confirmation|chat|handoff_needed",
            "response": "Natural conversational response to user",
            "agent_action": "none|execute_action|need_clarification|suggest_handoff|emergency_escalation",
            "action_details": {{"action": "action_name", "parameters": {{}}, "confidence": 0.0-1.0}},
            "recommended_agent": "PERSONAL_ASSISTANT|OUTBOUND_CALLER|EMERGENCY_RESPONSE",
            "handoff_reason": "Why handoff is needed",
            "needs_confirmation": true/false,
            "follow_up_questions": ["question1", "question2"],
            "conversation_context": {{"topic": "current_topic", "status": "ongoing|completed"}}
        }}
        
        EXAMPLES:
        User: "What's my schedule today?"
        Response: {{"conversation_type": "question", "response": "Let me check your schedule for today...", "agent_action": "execute_action"}}
        
        User: "Can you call Johnson about tomorrow?"
        Response: {{"conversation_type": "handoff_needed", "response": "I'll connect you with our calling specialist to handle that call", "recommended_agent": "OUTBOUND_CALLER"}}
        
        User: "Emergency at the Peterson site!"
        Response: {{"conversation_type": "handoff_needed", "response": "I'm immediately connecting you to emergency response", "recommended_agent": "EMERGENCY_RESPONSE", "agent_action": "emergency_escalation"}}
        """
    
    def _update_conversation_memory(self, session_id: str, user_input: str, ai_response: Dict[str, Any]):
        """Update conversation memory for context."""
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = []
        
        # Add user input
        self.conversation_memory[session_id].append({
            "role": "user",
            "content": user_input
        })
        
        # Add AI response
        self.conversation_memory[session_id].append({
            "role": "assistant", 
            "content": ai_response.get("response", "")
        })
        
        # Keep only last 50 messages (25 exchanges) to manage memory
        if len(self.conversation_memory[session_id]) > 50:
            self.conversation_memory[session_id] = self.conversation_memory[session_id][-50:]
        
        # Update active topic
        context = ai_response.get("conversation_context", {})
        if context.get("topic"):
            self.active_topics[session_id] = context["topic"]
        
        # Update pending actions
        if ai_response.get("needs_confirmation"):
            self.pending_actions[session_id] = ai_response.get("action_details")
        elif ai_response.get("conversation_type") == "confirmation":
            self.pending_actions.pop(session_id, None)
    
    async def _handle_conversational_flow(self, ai_response: Dict[str, Any], 
                                        session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle different types of conversational flows."""
        conversation_type = ai_response.get("conversation_type")
        agent_action = ai_response.get("agent_action", "none")
        
        # Enhance response with conversational metadata
        enhanced_response = {
            **ai_response,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_context.get("session_id"),
            "conversation_flow": True,  # Indicates this is conversational, not command-based
        }
        
        # Handle agent handoffs in conversational context
        if conversation_type == "handoff_needed":
            enhanced_response["handoff_required"] = True
            enhanced_response["handoff_context"] = {
                "reason": ai_response.get("handoff_reason"),
                "conversation_summary": self._generate_conversation_summary(session_context.get("session_id")),
                "active_topic": self.active_topics.get(session_context.get("session_id"))
            }
        
        # Handle emergency escalations
        if agent_action == "emergency_escalation":
            enhanced_response["priority"] = "urgent"
            enhanced_response["emergency_detected"] = True
        
        # Add proactive suggestions
        if conversation_type in ["question", "request"] and agent_action == "execute_action":
            enhanced_response["proactive_suggestions"] = self._generate_proactive_suggestions(
                ai_response, session_context
            )
        
        return enhanced_response
    
    def _generate_conversation_summary(self, session_id: str) -> str:
        """Generate a summary of the current conversation for handoff context."""
        if not session_id or session_id not in self.conversation_memory:
            return "Starting new conversation"
        
        recent_messages = self.conversation_memory[session_id][-6:]  # Last 3 exchanges
        
        if not recent_messages:
            return "Starting new conversation"
        
        # Extract key topics from recent conversation
        user_messages = [msg["content"] for msg in recent_messages if msg["role"] == "user"]
        
        if user_messages:
            last_user_message = user_messages[-1]
            active_topic = self.active_topics.get(session_id, "general business management")
            return f"User was discussing {active_topic}. Last mentioned: {last_user_message[:100]}..."
        
        return "Ongoing conversation about business operations"
    
    def _generate_proactive_suggestions(self, ai_response: Dict[str, Any], 
                                      session_context: Dict[str, Any]) -> List[str]:
        """Generate proactive suggestions based on conversation context."""
        suggestions = []
        action_details = ai_response.get("action_details", {})
        action_name = action_details.get("action", "")
        
        # Context-aware suggestions
        if "schedule" in action_name.lower():
            suggestions.extend([
                "Would you like me to send a reminder to the client?",
                "Should I check for any conflicts with this appointment?",
                "Would you like me to add travel time to your calendar?"
            ])
        
        elif "call" in action_name.lower():
            suggestions.extend([
                "Should I prepare talking points for this call?",
                "Would you like me to check their recent service history first?",
                "Should I schedule a follow-up reminder?"
            ])
        
        elif "job" in action_name.lower():
            suggestions.extend([
                "Would you like me to check inventory for this job?",
                "Should I send the client a confirmation message?",
                "Would you like directions to the job site?"
            ])
        
        return suggestions[:2]  # Limit to 2 suggestions to avoid overwhelming
    
    # Legacy method for backward compatibility
    async def process_voice_command(self, command_text: str, session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy method - redirects to conversational processor."""
        return await self.process_conversational_input(command_text, session_context)


# Factory function for dependency injection
def create_livekit_voice_agent_adapter() -> LiveKitVoiceAgentAdapter:
    """Create LiveKit voice agent adapter instance."""
    return LiveKitVoiceAgentAdapter() 