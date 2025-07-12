"""
Agent Orchestrator

Main orchestrator for managing and routing between specialized voice agents.
"""

from typing import Dict, Any, List, Optional
from agents import Agent
from ..core.base_agent import BaseVoiceAgent
from ..personal.openai_personal_agent import OpenAIPersonalAgent
from .specialized_agents import JobAgent, ProjectAgent, InvoiceAgent, EstimateAgent, ContactAgent


class AgentOrchestrator(BaseVoiceAgent):
    """Main orchestrator agent that routes to specialized agents"""
    
    def __init__(self, 
                 business_context: Dict[str, Any],
                 user_context: Dict[str, Any]):
        """
        Initialize agent orchestrator
        
        Args:
            business_context: Business information and context
            user_context: User information and preferences
        """
        super().__init__(business_context, user_context)
        
        # Initialize specialized agents
        self.job_agent = JobAgent(business_context, user_context)
        self.project_agent = ProjectAgent(business_context, user_context)
        self.invoice_agent = InvoiceAgent(business_context, user_context)
        self.estimate_agent = EstimateAgent(business_context, user_context)
        self.contact_agent = ContactAgent(business_context, user_context)
        
        # Create agent instances
        self.specialized_agents = {
            "job_management": self.job_agent.create_agent(),
            "project_management": self.project_agent.create_agent(),
            "invoice_management": self.invoice_agent.create_agent(),
            "estimate_management": self.estimate_agent.create_agent(),
            "contact_management": self.contact_agent.create_agent()
        }
    
    def get_instructions(self) -> str:
        """Get system instructions for the orchestrator agent"""
        business_name = self.business_context.get('name', 'Hero365')
        user_name = self.user_context.get('name', 'User')
        
        return f"""You are the main AI assistant orchestrator for {business_name}.

Your role is to understand {user_name}'s requests and route them to the most appropriate specialized agent:

AVAILABLE SPECIALIZED AGENTS:
1. Job Management Agent - For creating, updating, scheduling, and tracking jobs
2. Project Management Agent - For monitoring project progress and milestones  
3. Invoice Management Agent - For creating invoices, tracking payments, sending reminders
4. Estimate Management Agent - For creating estimates and converting to invoices
5. Contact Management Agent - For managing client contacts and interactions

ROUTING GUIDELINES:
- Listen carefully to understand the user's intent
- Route to the most appropriate specialized agent based on the request
- For complex requests involving multiple areas, handle them step by step
- Always provide a brief explanation of what agent you're routing to and why

COMMUNICATION STYLE:
- Be professional and efficient
- Acknowledge the user's request clearly
- Explain the handoff process briefly
- Ensure smooth transitions between agents

Remember: Your job is to be an intelligent router that ensures {user_name} gets connected to the right specialist for their specific business needs."""
    
    def get_tools(self) -> List[Any]:
        """Get tools for the orchestrator (mainly routing tools)"""
        return []  # Orchestrator uses handoffs, not direct tools
    
    def get_handoffs(self) -> List[Agent]:
        """Get list of specialized agents for handoffs"""
        return list(self.specialized_agents.values())
    
    def get_agent_name(self) -> str:
        """Get orchestrator agent name"""
        business_name = self.business_context.get('name', 'Hero365')
        return f"{business_name} Assistant"
    
    def get_specialized_agent(self, agent_type: str) -> Optional[Agent]:
        """
        Get a specific specialized agent
        
        Args:
            agent_type: Type of agent to retrieve
            
        Returns:
            Agent instance or None if not found
        """
        return self.specialized_agents.get(agent_type)
    
    def create_orchestrated_workflow(self) -> Agent:
        """Create the main orchestrated workflow with all specialized agents"""
        return Agent(
            name=self.get_agent_name(),
            instructions=self.get_instructions(),
            tools=self.get_tools(),
            handoffs=self.get_handoffs(),
            model_config={
                "temperature": 0.7,
                "max_tokens": 200
            }
        ) 