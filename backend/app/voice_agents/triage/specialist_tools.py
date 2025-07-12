"""
Specialist Agent Tools for Triage System

Convert specialized agents into callable tools for the triage agent using the agent-as-tool pattern.
"""

from typing import Dict, Any, List, Optional
import asyncio
from ..core.base_agent import BaseVoiceAgent
from .context_manager import ContextManager
from .agent_registry import AgentRegistry, default_registry


class SpecialistAgentTools:
    """Convert specialized agents into callable tools for triage agent"""
    
    def __init__(self, context_manager: ContextManager, registry: AgentRegistry = None):
        """
        Initialize specialist tools
        
        Args:
            context_manager: Context manager for business and user context
            registry: Agent registry for managing specialized agents
        """
        self.context_manager = context_manager
        self.registry = registry or default_registry
        self._agent_cache: Dict[str, BaseVoiceAgent] = {}
    
    def get_all_tools(self) -> List[Any]:
        """Get all specialist tools available to the triage agent"""
        return [
            self.route_to_scheduling,
            self.route_to_job_management,
            self.route_to_invoice_management,
            self.route_to_estimate_management,
            self.route_to_contact_management,
            self.route_to_project_management,
            self.route_to_payment_processing,
            self.route_to_customer_service,
            self.route_to_inventory_management,
            self.execute_parallel_specialists,
            self.get_specialist_capabilities,
            self.escalate_to_human
        ]
    
    async def execute_specialist(self, agent_name: str, request: str) -> str:
        """
        Execute a specialist agent with the given request
        
        Args:
            agent_name: Name of the specialist agent
            request: User request to process
            
        Returns:
            Response from the specialist agent
        """
        try:
            # Check if agent is cached
            if agent_name in self._agent_cache:
                agent = self._agent_cache[agent_name]
            else:
                # Create new agent instance
                agent = self.registry.create_agent(
                    agent_name,
                    self.context_manager.business_context,
                    self.context_manager.user_context
                )
                self._agent_cache[agent_name] = agent
            
            # Execute the agent with the request
            from agents import Runner
            result = await Runner.run(agent.create_agent(), request)
            
            return result.final_output if hasattr(result, 'final_output') else str(result)
            
        except Exception as e:
            return f"Error executing {agent_name}: {str(e)}"
    
    async def route_to_scheduling(self, request: str) -> str:
        """
        Route request to scheduling specialist for calendar management, appointments, and scheduling.
        
        Use this for:
        - Scheduling appointments or meetings
        - Checking availability
        - Rescheduling existing appointments
        - Managing calendar events
        - Blocking time slots
        
        Args:
            request: The scheduling-related request from the user
        """
        return await self.execute_specialist("scheduling", request)
    
    async def route_to_job_management(self, request: str) -> str:
        """
        Route request to job management specialist for job creation, tracking, and management.
        
        Use this for:
        - Creating new jobs or work orders
        - Updating job status and progress
        - Tracking job completion
        - Managing job assignments
        - Scheduling job activities
        
        Args:
            request: The job-related request from the user
        """
        return await self.execute_specialist("job_management", request)
    
    async def route_to_invoice_management(self, request: str) -> str:
        """
        Route request to invoice management specialist for billing, invoicing, and payment tracking.
        
        Use this for:
        - Creating invoices
        - Tracking payment status
        - Sending payment reminders
        - Processing billing information
        - Managing accounts receivable
        
        Args:
            request: The invoice-related request from the user
        """
        return await self.execute_specialist("invoice_management", request)
    
    async def route_to_estimate_management(self, request: str) -> str:
        """
        Route request to estimate management specialist for quote creation and estimate management.
        
        Use this for:
        - Creating estimates or quotes
        - Converting estimates to invoices
        - Tracking estimate status
        - Updating pricing information
        - Managing proposal workflows
        
        Args:
            request: The estimate-related request from the user
        """
        return await self.execute_specialist("estimate_management", request)
    
    async def route_to_contact_management(self, request: str) -> str:
        """
        Route request to contact management specialist for client and contact management.
        
        Use this for:
        - Managing client information
        - Recording client interactions
        - Scheduling follow-ups
        - Searching contacts
        - Updating contact details
        
        Args:
            request: The contact-related request from the user
        """
        return await self.execute_specialist("contact_management", request)
    
    async def route_to_project_management(self, request: str) -> str:
        """
        Route request to project management specialist for project tracking and milestone management.
        
        Use this for:
        - Tracking project progress
        - Managing milestones
        - Updating project status
        - Monitoring timelines
        - Coordinating project resources
        
        Args:
            request: The project-related request from the user
        """
        return await self.execute_specialist("project_management", request)
    
    async def route_to_payment_processing(self, request: str) -> str:
        """
        Route request to payment processing specialist for payment transactions and financial operations.
        
        Use this for:
        - Processing payments
        - Handling refunds
        - Managing payment methods
        - Tracking financial transactions
        - Generating payment reports
        
        Args:
            request: The payment-related request from the user
        """
        # Note: This would route to a PaymentAgent when implemented
        return "Payment processing specialist not yet implemented. Please contact support for payment-related requests."
    
    async def route_to_customer_service(self, request: str) -> str:
        """
        Route request to customer service specialist for support and issue resolution.
        
        Use this for:
        - Handling customer complaints
        - Resolving service issues
        - Managing support tickets
        - Providing customer assistance
        - Escalating complex problems
        
        Args:
            request: The customer service request from the user
        """
        # Note: This would route to a CustomerServiceAgent when implemented
        return "Customer service specialist not yet implemented. Please contact support for service-related requests."
    
    async def route_to_inventory_management(self, request: str) -> str:
        """
        Route request to inventory management specialist for stock management and product tracking.
        
        Use this for:
        - Managing inventory levels
        - Tracking product stock
        - Processing reorders
        - Managing suppliers
        - Updating product information
        
        Args:
            request: The inventory-related request from the user
        """
        # Note: This would route to an InventoryAgent when implemented
        return "Inventory management specialist not yet implemented. Please contact support for inventory-related requests."
    
    async def execute_parallel_specialists(self, requests: List[Dict[str, str]]) -> str:
        """
        Execute multiple specialist agents in parallel for complex multi-domain requests.
        
        Use this for requests that span multiple business domains and can be handled simultaneously.
        
        Args:
            requests: List of dictionaries with 'agent' and 'request' keys
                     Example: [{"agent": "job_management", "request": "Create job for Smith"}, 
                              {"agent": "scheduling", "request": "Schedule follow-up"}]
        """
        try:
            # Create tasks for parallel execution
            tasks = []
            for req in requests:
                agent_name = req.get("agent")
                request_text = req.get("request")
                
                if agent_name and request_text:
                    task = self.execute_specialist(agent_name, request_text)
                    tasks.append((agent_name, task))
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*[task for _, task in tasks])
            
            # Format combined response
            response_parts = []
            for i, (agent_name, _) in enumerate(tasks):
                response_parts.append(f"**{agent_name.title()}**: {results[i]}")
            
            return "\n\n".join(response_parts)
            
        except Exception as e:
            return f"Error executing parallel specialists: {str(e)}"
    
    async def get_specialist_capabilities(self, specialist_name: Optional[str] = None) -> str:
        """
        Get information about specialist capabilities and available services.
        
        Args:
            specialist_name: Name of specific specialist to get info about (optional)
        """
        if specialist_name:
            config = self.registry.get_agent_by_name(specialist_name)
            if config:
                capabilities = "\n".join(f"- {cap}" for cap in config.capabilities)
                return f"**{config.name.title()}** - {config.description}\n\nCapabilities:\n{capabilities}"
            else:
                return f"Specialist '{specialist_name}' not found."
        else:
            # Return summary of all specialists
            summary = "Available Specialists:\n\n"
            for config in self.registry.get_all_agents():
                capabilities = ", ".join(config.capabilities[:3])
                summary += f"**{config.name.title()}**: {config.description}\n"
                summary += f"Key capabilities: {capabilities}\n\n"
            return summary
    
    async def escalate_to_human(self, issue_description: str, urgency: str = "medium") -> str:
        """
        Escalate complex issues to human support when AI cannot adequately handle the request.
        
        Use this for:
        - Complex technical issues
        - Legal or compliance matters
        - High-value client concerns
        - Situations requiring human judgment
        
        Args:
            issue_description: Description of the issue that needs human attention
            urgency: Urgency level (low, medium, high, critical)
        """
        # In a real implementation, this would create a support ticket
        # and notify human operators
        
        ticket_id = f"ESCALATION-{hash(issue_description) % 10000:04d}"
        
        return f"""
Issue escalated to human support.

Ticket ID: {ticket_id}
Urgency: {urgency.upper()}
Description: {issue_description}

A human support representative will be notified and will contact you within:
- Critical: 15 minutes
- High: 1 hour  
- Medium: 4 hours
- Low: 24 hours

You will receive updates via email and/or phone.
        """.strip()
    
    def get_routing_suggestions(self, user_request: str) -> List[Dict[str, Any]]:
        """
        Get routing suggestions for a user request
        
        Args:
            user_request: The user's request text
            
        Returns:
            List of routing suggestions with confidence scores
        """
        return self.registry.get_routing_suggestions(
            user_request,
            self.context_manager.business_context,
            self.context_manager.user_context
        )
    
    def clear_agent_cache(self):
        """Clear the agent cache to force fresh agent creation"""
        self._agent_cache.clear()
    
    def get_cached_agents(self) -> List[str]:
        """Get list of currently cached agent names"""
        return list(self._agent_cache.keys()) 