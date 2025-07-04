"""
Voice Agent Factory

Factory for creating and managing different types of voice agents.
Handles the creation of Personal Assistant and Outbound Caller agents with appropriate configurations.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass

from ...application.ports.voice_agent_service import (
    VoiceAgentTool, VoiceSessionConfig, OutboundCallConfig
)
from ...domain.enums import AgentType
from .livekit_voice_agent_adapter import LiveKitVoiceAgentAdapter

logger = logging.getLogger(__name__)


@dataclass
class VoiceAgentConfiguration:
    """Configuration for voice agent creation."""
    agent_type: AgentType
    name: str
    description: str
    instructions: str
    default_tools: List[str]
    max_session_duration: int  # minutes
    language_models: Dict[str, str]
    voice_settings: Dict[str, Any]


class VoiceAgentFactory:
    """
    Factory for creating and configuring voice agents.
    
    Manages the creation of different types of voice agents with appropriate
    configurations, tools, and settings for each agent type.
    """
    
    def __init__(self, voice_agent_adapter: LiveKitVoiceAgentAdapter):
        self.voice_agent_adapter = voice_agent_adapter
        self.agent_configurations = self._initialize_agent_configurations()
        
        logger.info("Voice Agent Factory initialized")
    
    def _initialize_agent_configurations(self) -> Dict[AgentType, VoiceAgentConfiguration]:
        """Initialize predefined configurations for different agent types."""
        return {
            AgentType.PERSONAL_ASSISTANT: VoiceAgentConfiguration(
                agent_type=AgentType.PERSONAL_ASSISTANT,
                name="Hero365 Personal Assistant",
                description="AI assistant for hands-free business management while driving or working",
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
                
                BUSINESS CONTEXT:
                - Understand home services industry terminology
                - Prioritize urgent jobs and client satisfaction
                - Track time and materials for accurate billing
                - Suggest efficient routing and scheduling
                - Maintain professional communication standards
                
                Always ask clarifying questions if information is unclear and confirm
                actions that have significant business impact.""",
                default_tools=[
                    "schedule_job",
                    "update_job_status",
                    "get_daily_schedule",
                    "navigate_to_job",
                    "add_voice_note",
                    "check_inventory",
                    "emergency_scheduling",
                    "client_communication",
                    "route_optimization",
                    "business_metrics"
                ],
                max_session_duration=30,
                language_models={
                    "primary": "gpt-4",
                    "fallback": "gpt-3.5-turbo"
                },
                voice_settings={
                    "voice_id": "professional_male",
                    "speaking_rate": 1.0,
                    "pitch": 0.0,
                    "stability": 0.75,
                    "clarity": 0.85
                }
            ),
            
            AgentType.OUTBOUND_CALLER: VoiceAgentConfiguration(
                agent_type=AgentType.OUTBOUND_CALLER,
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
                - Supplier communications and quote requests
                - Campaign management and outcome tracking
                - Emergency notifications and scheduling
                
                COMMUNICATION STYLE:
                - Professional, courteous, and friendly tone
                - Represent the business with integrity
                - Listen actively and respond appropriately
                - Handle objections gracefully
                - Follow call scripts when provided
                - Adapt naturally to conversation flow
                
                CALL MANAGEMENT:
                - Track call outcomes and schedule follow-ups
                - Respect do-not-call lists and preferences
                - Handle voicemail professionally
                - Transfer to human when appropriate
                - Maintain detailed call records
                
                BUSINESS OBJECTIVES:
                - Generate qualified leads
                - Improve client retention and satisfaction
                - Increase job conversion rates
                - Streamline business communications
                - Build positive brand reputation
                
                Always be honest about being an AI assistant and offer to connect
                with a human representative when requested.""",
                default_tools=[
                    "lead_qualification",
                    "schedule_appointment",
                    "client_follow_up",
                    "payment_reminder",
                    "supplier_communication",
                    "campaign_tracking",
                    "call_outcome_logging",
                    "voicemail_handling",
                    "human_transfer",
                    "satisfaction_survey"
                ],
                max_session_duration=15,
                language_models={
                    "primary": "gpt-4",
                    "fallback": "gpt-3.5-turbo"
                },
                voice_settings={
                    "voice_id": "professional_female",
                    "speaking_rate": 0.9,
                    "pitch": 0.1,
                    "stability": 0.8,
                    "clarity": 0.9
                }
            )
        }
    
    def create_personal_assistant_config(self, 
                                       business_id: str,
                                       user_id: str,
                                       language: str = "en-US",
                                       emergency_mode: bool = False,
                                       custom_tools: Optional[List[str]] = None,
                                       custom_instructions: Optional[str] = None) -> VoiceSessionConfig:
        """
        Create configuration for a personal assistant voice session.
        
        Args:
            business_id: Business identifier
            user_id: User identifier
            language: Language code (default: en-US)
            emergency_mode: Whether to enable emergency mode
            custom_tools: Optional list of custom tools to include
            custom_instructions: Optional custom instructions to append
            
        Returns:
            VoiceSessionConfig for personal assistant
        """
        config = self.agent_configurations[AgentType.PERSONAL_ASSISTANT]
        
        # Combine default tools with custom tools
        tools = config.default_tools.copy()
        if custom_tools:
            tools.extend(custom_tools)
        
        # Combine default instructions with custom instructions
        instructions = config.instructions
        if custom_instructions:
            instructions += f"\n\nADDITIONAL INSTRUCTIONS:\n{custom_instructions}"
        
        return VoiceSessionConfig(
            agent_type=AgentType.PERSONAL_ASSISTANT,
            business_id=business_id,
            user_id=user_id,
            language=language,
            max_duration_minutes=config.max_session_duration,
            emergency_mode=emergency_mode,
            tools=tools,
            custom_instructions=instructions
        )
    
    def create_outbound_caller_config(self,
                                    business_id: str,
                                    recipient_phone: str,
                                    recipient_name: str,
                                    call_purpose: str,
                                    campaign_id: Optional[str] = None,
                                    script_instructions: Optional[str] = None,
                                    priority: int = 1,
                                    custom_tools: Optional[List[str]] = None) -> OutboundCallConfig:
        """
        Create configuration for an outbound call session.
        
        Args:
            business_id: Business identifier
            recipient_phone: Phone number to call
            recipient_name: Name of the recipient
            call_purpose: Purpose of the call (lead generation, follow-up, etc.)
            campaign_id: Optional campaign identifier
            script_instructions: Optional script instructions
            priority: Call priority (1-5, 5 being highest)
            custom_tools: Optional list of custom tools to include
            
        Returns:
            OutboundCallConfig for outbound caller
        """
        config = self.agent_configurations[AgentType.OUTBOUND_CALLER]
        
        # Combine default tools with custom tools
        tools = config.default_tools.copy()
        if custom_tools:
            tools.extend(custom_tools)
        
        # Create call-specific script instructions
        full_script_instructions = f"Call Purpose: {call_purpose}\n"
        if script_instructions:
            full_script_instructions += f"Script Instructions: {script_instructions}\n"
        
        return OutboundCallConfig(
            business_id=business_id,
            recipient_phone=recipient_phone,
            recipient_name=recipient_name,
            campaign_id=campaign_id,
            script_instructions=full_script_instructions,
            max_duration_minutes=config.max_session_duration,
            priority=priority,
            tools=tools
        )
    
    async def register_custom_tool(self, 
                                 tool: VoiceAgentTool, 
                                 agent_types: List[AgentType]) -> bool:
        """
        Register a custom voice tool for specific agent types.
        
        Args:
            tool: The voice tool to register
            agent_types: List of agent types that can use this tool
            
        Returns:
            True if registration successful
        """
        try:
            success = await self.voice_agent_adapter.register_voice_tool(tool, agent_types)
            
            if success:
                # Update default tools for agent configurations
                for agent_type in agent_types:
                    if agent_type in self.agent_configurations:
                        config = self.agent_configurations[agent_type]
                        if tool.name not in config.default_tools:
                            config.default_tools.append(tool.name)
                
                logger.info(f"Successfully registered custom tool '{tool.name}' for agents: {[at.value for at in agent_types]}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to register custom tool '{tool.name}': {str(e)}")
            return False
    
    async def unregister_custom_tool(self, tool_name: str) -> bool:
        """
        Unregister a custom voice tool.
        
        Args:
            tool_name: Name of the tool to unregister
            
        Returns:
            True if unregistration successful
        """
        try:
            success = await self.voice_agent_adapter.unregister_voice_tool(tool_name)
            
            if success:
                # Remove from default tools for all agent configurations
                for config in self.agent_configurations.values():
                    if tool_name in config.default_tools:
                        config.default_tools.remove(tool_name)
                
                logger.info(f"Successfully unregistered custom tool '{tool_name}'")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to unregister custom tool '{tool_name}': {str(e)}")
            return False
    
    def get_agent_configuration(self, agent_type: AgentType) -> Optional[VoiceAgentConfiguration]:
        """
        Get configuration for a specific agent type.
        
        Args:
            agent_type: Type of agent
            
        Returns:
            VoiceAgentConfiguration or None if not found
        """
        return self.agent_configurations.get(agent_type)
    
    def get_available_tools(self, agent_type: AgentType) -> List[str]:
        """
        Get list of available tools for an agent type.
        
        Args:
            agent_type: Type of agent
            
        Returns:
            List of available tool names
        """
        config = self.agent_configurations.get(agent_type)
        if config:
            return config.default_tools.copy()
        return []
    
    def update_agent_configuration(self, 
                                 agent_type: AgentType,
                                 **kwargs) -> bool:
        """
        Update configuration for an agent type.
        
        Args:
            agent_type: Type of agent to update
            **kwargs: Configuration parameters to update
            
        Returns:
            True if update successful
        """
        try:
            if agent_type not in self.agent_configurations:
                logger.error(f"Agent type {agent_type.value} not found")
                return False
            
            config = self.agent_configurations[agent_type]
            
            # Update allowed fields
            allowed_fields = {
                'name', 'description', 'instructions', 'default_tools',
                'max_session_duration', 'language_models', 'voice_settings'
            }
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(config, field):
                    setattr(config, field, value)
                    logger.info(f"Updated {field} for agent type {agent_type.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update agent configuration: {str(e)}")
            return False
    
    async def validate_agent_health(self) -> Dict[str, Any]:
        """
        Validate the health of the voice agent system.
        
        Returns:
            Health status dictionary
        """
        try:
            # Check voice agent adapter health
            adapter_health = await self.voice_agent_adapter.get_service_health()
            
            # Check agent configurations
            config_status = {
                "personal_assistant": AgentType.PERSONAL_ASSISTANT in self.agent_configurations,
                "outbound_caller": AgentType.OUTBOUND_CALLER in self.agent_configurations
            }
            
            # Check available tools
            tools_status = {}
            for agent_type in [AgentType.PERSONAL_ASSISTANT, AgentType.OUTBOUND_CALLER]:
                available_tools = await self.voice_agent_adapter.get_available_tools(agent_type)
                tools_status[agent_type.value] = {
                    "count": len(available_tools),
                    "tools": available_tools
                }
            
            return {
                "factory_status": "healthy",
                "adapter_health": adapter_health,
                "agent_configurations": config_status,
                "available_tools": tools_status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Voice agent health check failed: {str(e)}")
            return {
                "factory_status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Factory function for dependency injection
def create_voice_agent_factory(voice_agent_adapter: LiveKitVoiceAgentAdapter) -> VoiceAgentFactory:
    """Create voice agent factory instance."""
    return VoiceAgentFactory(voice_agent_adapter) 