"""
Triage agent that routes user requests to appropriate specialist agents using OpenAI Agents SDK.
"""

from typing import Dict, Any, Optional, List
from agents import Agent, Runner, function_tool
from ..core.base_agent import BaseVoiceAgent
from ..core.context_manager import ContextManager
from ...core.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)


class TriageAgent(BaseVoiceAgent):
    """Main triage agent that intelligently routes to specialist agents using OpenAI Agents SDK"""
    
    # Consolidated instructions for the triage agent
    TRIAGE_INSTRUCTIONS = """
    You are the Hero365 triage agent. You help users with their business needs by using 
    specialized tools to handle different types of business operations.
    
    You have access to specialized tools for:
    - Contact management: Creating, updating, searching contacts
    - Job management: Creating, tracking, updating jobs
    - Estimate management: Creating, managing estimates and quotes
    - Scheduling: Booking appointments, checking availability
    - General business questions and support
    
    When a user asks for help, analyze their request and use the appropriate tool to handle it.
    The tools will automatically handle conversation flow and parameter collection.
    
    INSTRUCTIONS:
    - Listen to what the user wants to accomplish
    - Use the most appropriate tool for their request:
      * contact_management for contact-related tasks
      * job_management for job-related tasks
      * estimate_management for estimate/quote-related tasks
      * scheduling_management for appointment/calendar-related tasks
    - If the request is general or you're not sure, provide general help first
    - Be friendly, helpful, and professional in all interactions
    - Let the specialist tools handle the detailed interactions
    
    All specialist tools are now fully functional and ready to help users.
    """
    
    def __init__(self, context_manager: ContextManager, specialist_agents: Dict[str, Any]):
        """
        Initialize triage agent with specialist agents.
        
        Args:
            context_manager: Shared context manager
            specialist_agents: Dictionary of specialist agent instances
        """
        super().__init__(
            name="Triage Agent",
            instructions=self.TRIAGE_INSTRUCTIONS,
            context_manager=context_manager,
            tools=[]
        )
        
        self.specialist_agents = specialist_agents
        self.context_manager = context_manager
        
        # Create the OpenAI Agents SDK triage agent (no handoffs, just routing tools)
        self.sdk_agent = self._create_sdk_agent()

    def _create_sdk_agent(self) -> Agent:
        """Create the OpenAI Agents SDK agent with specialist agent tools"""
        try:
            from agents import Agent
            import os
            
            # Ensure OpenAI API key is available for the agents SDK
            if settings.OPENAI_API_KEY:
                os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
                logger.info("✅ OpenAI API key configured for agents SDK")
            else:
                logger.error("❌ OpenAI API key not found in settings")
                raise ValueError("OpenAI API key is required for voice agents")
            
            # Create tools list starting with general tools
            tools = [
                self._get_business_info_tool,
                self._get_general_help_tool,
            ]
            
            # Add specialist agents as tools
            if 'contact' in self.specialist_agents:
                contact_tool = self.specialist_agents['contact'].sdk_agent.as_tool(
                    tool_name="contact_management",
                    tool_description="Handle contact management tasks including creating, updating, searching, and managing contacts"
                )
                tools.append(contact_tool)
                logger.info("✅ Added contact management tool")
            
            if 'job' in self.specialist_agents:
                job_tool = self.specialist_agents['job'].sdk_agent.as_tool(
                    tool_name="job_management",
                    tool_description="Handle job management tasks including creating, updating, and tracking jobs"
                )
                tools.append(job_tool)
                logger.info("✅ Added job management tool")
            
            if 'estimate' in self.specialist_agents:
                estimate_tool = self.specialist_agents['estimate'].sdk_agent.as_tool(
                    tool_name="estimate_management",
                    tool_description="Handle estimate management tasks including creating, updating, and managing estimates"
                )
                tools.append(estimate_tool)
                logger.info("✅ Added estimate management tool")
            
            if 'scheduling' in self.specialist_agents:
                scheduling_tool = self.specialist_agents['scheduling'].sdk_agent.as_tool(
                    tool_name="scheduling_management",
                    tool_description="Handle scheduling tasks including booking appointments and managing availability"
                )
                tools.append(scheduling_tool)
                logger.info("✅ Added scheduling management tool")
            
            # Create the main triage agent with specialist agent tools
            triage_agent = Agent(
                name="Hero365 Triage Agent",
                instructions=self.TRIAGE_INSTRUCTIONS,
                tools=tools
            )
            
            return triage_agent
            
        except Exception as e:
            logger.error(f"❌ Error creating SDK agent: {e}")
            raise
    
    @staticmethod
    @function_tool
    def _get_business_info_tool() -> str:
        """Get general business information"""
        return """
        Hero365 is your AI-native ERP for home services. I can help you with:
        - Managing contacts and customer information
        - Creating and tracking jobs
        - Creating estimates and quotes
        - Scheduling appointments
        - General business operations
        
        What would you like help with today?
        """
    
    @staticmethod
    @function_tool
    def _get_general_help_tool() -> str:
        """Provide general help information"""
        return """
        I'm here to help you with your Hero365 business operations. I can assist with:
        
        📞 Contact Management: Create, update, search contacts
        🔧 Job Management: Create, track, update jobs
        📊 Estimate Management: Create, manage estimates and quotes
        📅 Scheduling: Book appointments, check availability
        
        Just tell me what you need help with, and I'll connect you with the right specialist!
        """
    

    
    async def process_user_request(self, text_input: str) -> str:
        """
        Process user request using OpenAI Agents SDK with proper conversation management.
        
        Args:
            text_input: User's input text
            
        Returns:
            Response from the appropriate specialist agent
        """
        try:
            logger.info(f"🎯 Processing user request with OpenAI Agents SDK: {text_input}")
            
            # Get current context to understand conversation state
            context = await self.context_manager.get_current_context()
            
            # Build input for the SDK - either fresh or with conversation history
            sdk_input = await self._build_sdk_input(text_input, context)
            
            # Update context with user input
            await self.context_manager.update_context({
                "conversation": {
                    "agent": "user",
                    "action": "text_input",
                    "message": text_input
                }
            })
            
            # Use the OpenAI Agents SDK to process the request
            result = await Runner.run(
                starting_agent=self.sdk_agent,
                input=sdk_input
            )
            
            # Store the full result in context for next conversation turn
            await self.context_manager.update_context({
                "last_agent_result": result.to_dict() if hasattr(result, 'to_dict') else None,
                "conversation_history": result.to_input_list()
            })
            
            # Get the final response
            response = result.final_output
            
            logger.info(f"✅ OpenAI Agents SDK response: {response}")
            
            # Update context with the response
            await self.context_manager.update_context({
                "conversation": {
                    "agent": "assistant",
                    "action": "text_response",
                    "message": response
                }
            })
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing user request with OpenAI Agents SDK: {e}")
            return f"I'm sorry, I encountered an error processing your request. Please try again or be more specific about what you need help with."
    
    async def _build_sdk_input(self, text_input: str, context: Dict[str, Any]):
        """Build input for OpenAI Agents SDK with conversation history if available"""
        
        # Check if we have conversation history from previous interactions
        conversation_history = context.get("conversation_history", [])
        
        if conversation_history:
            # We have conversation history - append new user message
            logger.info(f"📝 Using conversation history with {len(conversation_history)} previous messages")
            return conversation_history + [{"role": "user", "content": text_input}]
        else:
            # Fresh conversation - just the user input
            logger.info(f"📝 Starting fresh conversation")
            return text_input
    
    async def get_response(self, text_input: str) -> str:
        """
        Get response from the triage agent (compatibility method).
        
        Args:
            text_input: User's input text
            
        Returns:
            Response from the agent
        """
        return await self.process_user_request(text_input)
    
    def get_agent_capabilities(self) -> List[str]:
        """Get list of capabilities for this agent"""
        return [
            "Intelligent request routing using OpenAI Agents SDK",
            "Delegation to specialist agents",
            "Contact management routing",
            "Job management routing", 
            "Estimate management routing",
            "Scheduling management routing",
            "General business information",
            "Context-aware agent selection",
            "Natural language understanding",
            "Business operation assistance"
        ] 