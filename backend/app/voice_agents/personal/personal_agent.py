"""
Personal Voice Agent for Hero365

This module provides the personal voice agent for mobile users,
enabling voice-based job management during driving or working.
"""

import logging
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime

from livekit.agents import function_tool

from app.voice_agents.core.base_agent import BaseVoiceAgent
from app.voice_agents.core.voice_config import PersonalAgentConfig, DEFAULT_PERSONAL_CONFIG
from app.voice_agents.tools import job_tools, project_tools, invoice_tools, estimate_tools, contact_tools

logger = logging.getLogger(__name__)


class PersonalVoiceAgent(BaseVoiceAgent):
    """Personal voice agent for mobile users during driving/working"""
    
    def __init__(self, 
                 business_context: Dict[str, Any],
                 user_context: Dict[str, Any],
                 config: Optional[PersonalAgentConfig] = None):
        """
        Initialize the personal voice agent.
        
        Args:
            business_context: Business-specific context and configuration
            user_context: User-specific context and preferences
            config: Agent configuration (optional)
        """
        super().__init__(business_context, user_context, config or DEFAULT_PERSONAL_CONFIG)
        
        # Inject context into all tool modules
        self._inject_context_into_tools()
        
        logger.info(f"PersonalVoiceAgent initialized for business {self.get_current_business_id()}")
    
    def _inject_context_into_tools(self) -> None:
        """Inject business and user context into all voice tools"""
        context = {
            "business_id": self.get_current_business_id(),
            "user_id": self.get_current_user_id(),
            "business_context": self.business_context,
            "user_context": self.user_context
        }
        
        # Inject context into all tool modules
        job_tools.set_current_context(context)
        project_tools.set_current_context(context)
        invoice_tools.set_current_context(context)
        estimate_tools.set_current_context(context)
        contact_tools.set_current_context(context)
        
        logger.debug(f"Context injected into all tools for business {self.get_current_business_id()}")
    
    def get_tools(self) -> List[Callable]:
        """Get all available voice tools for this agent"""
        
        # Ensure context is fresh
        self._inject_context_into_tools()
        
        tools = [
            # Job Management Tools
            job_tools.create_job,
            job_tools.get_upcoming_jobs,
            job_tools.get_jobs_by_status,
            job_tools.update_job_status,
            job_tools.get_job_details,
            job_tools.schedule_job,
            job_tools.search_jobs,
            
            # Project Management Tools
            project_tools.create_project,
            project_tools.get_active_projects,
            project_tools.get_projects_by_status,
            project_tools.update_project_status,
            project_tools.get_project_details,
            project_tools.search_projects,
            
            # Invoice Management Tools
            invoice_tools.create_invoice,
            invoice_tools.get_unpaid_invoices,
            invoice_tools.get_overdue_invoices,
            invoice_tools.get_invoices_by_status,
            invoice_tools.process_payment,
            invoice_tools.get_invoice_details,
            invoice_tools.search_invoices,
            
            # Estimate Management Tools
            estimate_tools.create_estimate,
            estimate_tools.get_pending_estimates,
            estimate_tools.get_expired_estimates,
            estimate_tools.get_estimates_by_status,
            estimate_tools.convert_estimate_to_invoice,
            estimate_tools.get_estimate_details,
            estimate_tools.update_estimate_status,
            estimate_tools.search_estimates,
            
            # Contact Management Tools
            contact_tools.create_contact,
            contact_tools.search_contacts,
            contact_tools.get_recent_contacts,
            contact_tools.get_contacts_by_type,
            contact_tools.get_contact_details,
            contact_tools.update_contact,
            contact_tools.add_contact_interaction,
            contact_tools.get_contact_interactions,
        ]
        
        return tools
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        business_name = self.business_context.get("name", "your business")
        user_name = self.user_context.get("name", "there")
        
        return f"""You are Hero365 AI, a personal voice assistant for {business_name}. You're helping {user_name} manage their business operations through voice commands.

## Your Role & Capabilities

You are a comprehensive business management assistant that can help with:

### 📋 Job Management
- Create, schedule, and track jobs
- Update job status and add notes
- Search jobs by various criteria
- Get upcoming jobs and deadlines

### 📊 Project Management  
- Create and manage projects
- Track project progress and status
- Associate jobs with projects
- Monitor project budgets and timelines

### 💰 Invoice Management
- Create and send invoices
- Track unpaid and overdue invoices
- Process payments and update status
- Convert estimates to invoices

### 📝 Estimate Management
- Create detailed estimates for clients
- Track estimate status and expiration
- Convert accepted estimates to invoices
- Follow up on pending estimates

### 👥 Contact Management
- Add and update client contacts
- Search contacts by various criteria
- Track contact interactions and history
- Manage leads and customer relationships

## Voice-First Approach

Since you're helping someone who may be driving or working:

1. **Be Concise**: Provide clear, actionable information without overwhelming details
2. **Prioritize Safety**: If user mentions driving, keep responses brief and essential
3. **Confirm Actions**: Always confirm before creating, updating, or deleting anything
4. **Use Natural Language**: Speak conversationally, not like a technical interface
5. **Proactive Suggestions**: Offer helpful next steps and reminders

## Response Format

- **For Lists**: Summarize key items (e.g., "You have 3 jobs today: plumbing at Smith's at 9am, electrical at Jones's at 2pm, and inspection at Brown's at 4pm")
- **For Updates**: Confirm what was changed (e.g., "Job #1234 status updated to 'completed'")
- **For Searches**: Provide most relevant results first
- **For Errors**: Explain what went wrong and suggest alternatives

## Business Context

- Business: {business_name}
- User: {user_name}
- Services: {', '.join(self.business_context.get('services', []))}
- Safety Mode: {'Enabled' if self.user_context.get('safety_mode', True) else 'Disabled'}

Remember: You're here to make business management easier and more efficient through natural voice interaction. Always prioritize user safety and provide clear, actionable responses."""
    
    async def on_agent_start(self) -> None:
        """Called when agent starts"""
        
        # Ensure context is injected when agent starts
        self._inject_context_into_tools()
        
        # Record agent start
        await self.record_interaction("agent_start", {
            "agent_type": "personal",
            "business_id": self.get_current_business_id(),
            "user_id": self.get_current_user_id(),
            "is_driving": self.user_context.get("is_driving", False),
            "safety_mode": self.user_context.get("safety_mode", True)
        })
        
        logger.info(f"Personal agent {self.agent_id} started")
    
    async def on_agent_end(self) -> None:
        """Called when agent ends"""
        
        # Record agent end
        await self.record_interaction("agent_end", {
            "agent_type": "personal",
            "business_id": self.get_current_business_id(),
            "user_id": self.get_current_user_id(),
            "session_duration": (datetime.now() - self.created_at).total_seconds() if self.created_at else 0
        })
        
        logger.info(f"Personal agent {self.agent_id} ended")
    
    async def on_user_speech_start(self) -> None:
        """Called when user starts speaking"""
        logger.debug(f"User started speaking to agent {self.agent_id}")
    
    async def on_user_speech_end(self) -> None:
        """Called when user stops speaking"""
        logger.debug(f"User stopped speaking to agent {self.agent_id}")
    
    async def on_agent_speech_start(self) -> None:
        """Called when agent starts speaking"""
        logger.debug(f"Agent {self.agent_id} started speaking")
    
    async def on_agent_speech_end(self) -> None:
        """Called when agent stops speaking"""
        logger.debug(f"Agent {self.agent_id} stopped speaking") 