"""
Specialized Agents

Specialized voice agents for specific business domains.
"""

from typing import Dict, Any, List
from agents import Agent
from ..core.base_agent import BaseVoiceAgent
from ..tools.job_tools import JobTools
from ..tools.project_tools import ProjectTools
from ..tools.invoice_tools import InvoiceTools
from ..tools.estimate_tools import EstimateTools
from ..tools.contact_tools import ContactTools


class JobAgent(BaseVoiceAgent):
    """Specialized agent for job management"""
    
    def __init__(self, business_context: Dict[str, Any], user_context: Dict[str, Any]):
        super().__init__(business_context, user_context)
        self.job_tools = JobTools(self.get_business_id(), self.get_user_id())
    
    def get_instructions(self) -> str:
        business_name = self.business_context.get('name', 'Hero365')
        return f"""You are the Job Management specialist for {business_name}.

CAPABILITIES:
- Create new jobs with scheduling and client details
- Update job status and progress
- Reschedule jobs when needed
- Get job details and upcoming schedules
- Track job completion and notes

COMMUNICATION STYLE:
- Be efficient and action-oriented
- Confirm all job actions clearly
- Provide specific job details when requested
- Ask for clarification on scheduling conflicts

Focus on helping manage the job workflow efficiently."""
    
    def get_tools(self) -> List[Any]:
        return self.job_tools.get_tools()
    
    def get_handoffs(self) -> List[Agent]:
        return []  # Job agent doesn't hand off to others


class ProjectAgent(BaseVoiceAgent):
    """Specialized agent for project management"""
    
    def __init__(self, business_context: Dict[str, Any], user_context: Dict[str, Any]):
        super().__init__(business_context, user_context)
        self.project_tools = ProjectTools(self.get_business_id(), self.get_user_id())
    
    def get_instructions(self) -> str:
        business_name = self.business_context.get('name', 'Hero365')
        return f"""You are the Project Management specialist for {business_name}.

CAPABILITIES:
- Monitor project progress and milestones
- Update project status and completion percentages
- Track project timelines and deliverables
- Coordinate project resources and tasks

COMMUNICATION STYLE:
- Focus on progress and timelines
- Provide clear status updates
- Highlight upcoming milestones
- Alert on potential delays

Help keep projects on track and stakeholders informed."""
    
    def get_tools(self) -> List[Any]:
        return self.project_tools.get_tools()
    
    def get_handoffs(self) -> List[Agent]:
        return []


class InvoiceAgent(BaseVoiceAgent):
    """Specialized agent for invoice management"""
    
    def __init__(self, business_context: Dict[str, Any], user_context: Dict[str, Any]):
        super().__init__(business_context, user_context)
        self.invoice_tools = InvoiceTools(self.get_business_id(), self.get_user_id())
    
    def get_instructions(self) -> str:
        business_name = self.business_context.get('name', 'Hero365')
        return f"""You are the Invoice Management specialist for {business_name}.

CAPABILITIES:
- Create invoices for completed work
- Track invoice payment status
- Send payment reminders to clients
- Monitor overdue invoices
- Process payment records

COMMUNICATION STYLE:
- Be professional regarding financial matters
- Provide clear payment status information
- Handle payment discussions diplomatically
- Confirm all financial actions

Help maintain healthy cash flow and client relationships."""
    
    def get_tools(self) -> List[Any]:
        return self.invoice_tools.get_tools()
    
    def get_handoffs(self) -> List[Agent]:
        return []


class EstimateAgent(BaseVoiceAgent):
    """Specialized agent for estimate management"""
    
    def __init__(self, business_context: Dict[str, Any], user_context: Dict[str, Any]):
        super().__init__(business_context, user_context)
        self.estimate_tools = EstimateTools(self.get_business_id(), self.get_user_id())
    
    def get_instructions(self) -> str:
        business_name = self.business_context.get('name', 'Hero365')
        return f"""You are the Estimate Management specialist for {business_name}.

CAPABILITIES:
- Create detailed estimates for potential work
- Track estimate status and client responses
- Convert approved estimates to invoices
- Update estimate pricing and terms
- Monitor estimate expiration dates

COMMUNICATION STYLE:
- Be detailed about pricing and scope
- Explain estimate components clearly
- Handle pricing discussions professionally
- Confirm estimate approvals

Help win more business with accurate, professional estimates."""
    
    def get_tools(self) -> List[Any]:
        return self.estimate_tools.get_tools()
    
    def get_handoffs(self) -> List[Agent]:
        return []


class ContactAgent(BaseVoiceAgent):
    """Specialized agent for contact management"""
    
    def __init__(self, business_context: Dict[str, Any], user_context: Dict[str, Any]):
        super().__init__(business_context, user_context)
        self.contact_tools = ContactTools(self.get_business_id(), self.get_user_id())
    
    def get_instructions(self) -> str:
        business_name = self.business_context.get('name', 'Hero365')
        return f"""You are the Contact Management specialist for {business_name}.

CAPABILITIES:
- Access detailed contact information
- Record client interactions and notes
- Schedule follow-ups and callbacks
- Search contacts by various criteria
- Track relationship status and history

COMMUNICATION STYLE:
- Be personable and relationship-focused
- Remember client preferences and history
- Suggest appropriate follow-up actions
- Maintain professional boundaries

Help build and maintain strong client relationships."""
    
    def get_tools(self) -> List[Any]:
        return self.contact_tools.get_tools()
    
    def get_handoffs(self) -> List[Agent]:
        return [] 