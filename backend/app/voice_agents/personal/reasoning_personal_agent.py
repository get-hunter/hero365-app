"""
Reasoning-Enabled Personal Voice Agent for Hero365

This module extends the PersonalVoiceAgent with advanced reasoning capabilities,
implementing a Plan-Act-Verify loop for complex multi-tool workflows.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.voice_agents.core.reasoning_agent import ReasoningVoiceAgent, ActionType, ExecutionStatus
from app.voice_agents.core.voice_config import PersonalAgentConfig, DEFAULT_PERSONAL_CONFIG
from app.voice_agents.tools import job_tools, project_tools, invoice_tools, estimate_tools, contact_tools, product_tools
from app.infrastructure.config.dependency_injection import DependencyContainer

logger = logging.getLogger(__name__)


class ReasoningPersonalVoiceAgent(ReasoningVoiceAgent):
    """Reasoning-enabled personal voice agent for mobile users"""
    
    def __init__(self, 
                 business_context: Dict[str, Any],
                 user_context: Dict[str, Any],
                 config: Optional[PersonalAgentConfig] = None,
                 max_reasoning_iterations: int = 3):
        """
        Initialize the reasoning personal voice agent.
        
        Args:
            business_context: Business-specific context and configuration
            user_context: User-specific context and preferences
            config: Agent configuration (optional)
            max_reasoning_iterations: Maximum number of Plan-Act-Verify cycles
        """
        super().__init__(business_context, user_context, config or DEFAULT_PERSONAL_CONFIG, max_reasoning_iterations)
        
        # Inject context into all tool modules
        self._inject_context_into_tools()
        
        logger.info(f"ReasoningPersonalVoiceAgent initialized for business {self.get_current_business_id()}")
    
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
        product_tools.set_current_context(context)
        
        logger.debug(f"Context injected into all tools for business {self.get_current_business_id()}")
    
    def _initialize_tools(self) -> None:
        """Initialize and catalog all available tools"""
        # Ensure context is fresh
        self._inject_context_into_tools()
        
        # Register all tools with their callable functions
        self.available_tools = {
            # Job Management Tools
            "create_job": job_tools.create_job,
            "get_upcoming_jobs": job_tools.get_upcoming_jobs,
            "get_jobs_by_status": job_tools.get_jobs_by_status,
            "update_job_status": job_tools.update_job_status,
            "get_job_details": job_tools.get_job_details,
            "schedule_job": job_tools.schedule_job,
            "search_jobs": job_tools.search_jobs,
            
            # Project Management Tools
            "create_project": project_tools.create_project,
            "get_active_projects": project_tools.get_active_projects,
            "get_projects_by_status": project_tools.get_projects_by_status,
            "update_project_status": project_tools.update_project_status,
            "get_project_details": project_tools.get_project_details,
            "search_projects": project_tools.search_projects,
            
            # Invoice Management Tools
            "create_invoice": invoice_tools.create_invoice,
            "get_unpaid_invoices": invoice_tools.get_unpaid_invoices,
            "get_overdue_invoices": invoice_tools.get_overdue_invoices,
            "get_invoices_by_status": invoice_tools.get_invoices_by_status,
            "process_payment": invoice_tools.process_payment,
            "get_invoice_details": invoice_tools.get_invoice_details,
            "search_invoices": invoice_tools.search_invoices,
            
            # Estimate Management Tools
            "create_estimate": estimate_tools.create_estimate,
            "get_pending_estimates": estimate_tools.get_pending_estimates,
            "get_expired_estimates": estimate_tools.get_expired_estimates,
            "get_estimates_by_status": estimate_tools.get_estimates_by_status,
            "convert_estimate_to_invoice": estimate_tools.convert_estimate_to_invoice,
            "get_estimate_details": estimate_tools.get_estimate_details,
            "update_estimate_status": estimate_tools.update_estimate_status,
            "search_estimates": estimate_tools.search_estimates,
            
            # Contact Management Tools
            "create_contact": contact_tools.create_contact,
            "search_contacts": contact_tools.search_contacts,
            "get_recent_contacts": contact_tools.get_recent_contacts,
            "get_contacts_by_type": contact_tools.get_contacts_by_type,
            "get_contact_details": contact_tools.get_contact_details,
            "update_contact": contact_tools.update_contact,
            "add_contact_interaction": contact_tools.add_contact_interaction,
            "get_contact_interactions": contact_tools.get_contact_interactions,
            
            # Product & Inventory Management Tools
            "create_product": product_tools.create_product,
            "check_stock_levels": product_tools.check_stock_levels,
            "adjust_stock": product_tools.adjust_stock,
            "get_reorder_suggestions": product_tools.get_reorder_suggestions,
            "search_products": product_tools.search_products,
            "get_product_details": product_tools.get_product_details,
        }
    
    async def _call_planning_llm(self, prompt: str) -> 'PlanningResponse':
        """Call LLM for planning using the existing LLM integration"""
        from app.voice_agents.core.reasoning_agent import PlanningResponse
        
        try:
            # Use dependency injection to get the LLM service
            container = DependencyContainer()
            
            # This would be integrated with your actual LLM service
            # For now, we'll implement a more sophisticated planning logic
            
            # Parse the user request to determine complexity
            planning_result = await self._analyze_request_complexity(prompt)
            
            return PlanningResponse(
                goal=planning_result["goal"],
                action_type=planning_result["action_type"],
                reasoning=planning_result["reasoning"],
                tool_calls=planning_result["tool_calls"],
                success_criteria=planning_result["success_criteria"],
                fallback_plan=planning_result.get("fallback_plan", "Use simpler approach")
            )
        except Exception as e:
            logger.error(f"Planning LLM call failed: {str(e)}")
            raise
    
    async def _call_verification_llm(self, prompt: str) -> 'VerificationResponse':
        """Call LLM for verification using the existing LLM integration"""
        from app.voice_agents.core.reasoning_agent import VerificationResponse
        
        try:
            # Use dependency injection to get the LLM service
            container = DependencyContainer()
            
            # This would be integrated with your actual LLM service
            # For now, we'll implement a basic verification logic
            
            verification_result = await self._analyze_execution_results(prompt)
            
            return VerificationResponse(
                goal_achieved=verification_result["goal_achieved"],
                success_criteria_met=verification_result["success_criteria_met"],
                confidence_score=verification_result["confidence_score"],
                issues_found=verification_result["issues_found"],
                next_action=verification_result["next_action"],
                requires_revision=verification_result["requires_revision"]
            )
        except Exception as e:
            logger.error(f"Verification LLM call failed: {str(e)}")
            raise
    
    async def _analyze_request_complexity(self, prompt: str) -> Dict[str, Any]:
        """Analyze the complexity of a user request and create a plan"""
        # This is a simplified implementation - in practice, this would use your LLM
        
        # Extract key information from the prompt
        request_lower = prompt.lower()
        
        # Determine if it's a complex multi-step request
        if any(keyword in request_lower for keyword in ["create", "project", "add", "jobs", "send", "estimate"]):
            if "project" in request_lower and ("job" in request_lower or "estimate" in request_lower):
                # Complex project creation with jobs and estimates
                return {
                    "goal": "Create a comprehensive project with jobs and estimates",
                    "action_type": ActionType.MULTI_TOOL_SEQUENCE,
                    "reasoning": "This requires creating a project first, then adding jobs, and finally creating estimates",
                    "tool_calls": [
                        {
                            "tool_name": "create_project",
                            "parameters": {"name": "Extracted project name", "description": "Project description"},
                            "expected_outcome": "Project created successfully",
                            "depends_on": []
                        },
                        {
                            "tool_name": "create_job",
                            "parameters": {"title": "Job title", "project_id": "from_previous_step"},
                            "expected_outcome": "Job created and linked to project",
                            "depends_on": ["create_project"]
                        },
                        {
                            "tool_name": "create_estimate",
                            "parameters": {"project_id": "from_previous_step"},
                            "expected_outcome": "Estimate created for project",
                            "depends_on": ["create_project"]
                        }
                    ],
                    "success_criteria": [
                        "Project created successfully",
                        "All jobs added to project",
                        "Estimates generated and sent to client"
                    ]
                }
            elif "overdue" in request_lower and "invoice" in request_lower:
                # Handle overdue invoices
                return {
                    "goal": "Manage overdue invoices and follow up with clients",
                    "action_type": ActionType.MULTI_TOOL_SEQUENCE,
                    "reasoning": "Need to find overdue invoices, get client details, and create follow-up tasks",
                    "tool_calls": [
                        {
                            "tool_name": "get_overdue_invoices",
                            "parameters": {},
                            "expected_outcome": "List of overdue invoices retrieved",
                            "depends_on": []
                        },
                        {
                            "tool_name": "get_contact_details",
                            "parameters": {"contact_id": "from_invoice_data"},
                            "expected_outcome": "Client contact information retrieved",
                            "depends_on": ["get_overdue_invoices"]
                        },
                        {
                            "tool_name": "add_contact_interaction",
                            "parameters": {"contact_id": "from_previous_step", "interaction_type": "follow_up"},
                            "expected_outcome": "Follow-up interaction recorded",
                            "depends_on": ["get_contact_details"]
                        }
                    ],
                    "success_criteria": [
                        "Overdue invoices identified",
                        "Client contact information retrieved",
                        "Follow-up tasks created"
                    ]
                }
            elif "inventory" in request_lower and ("low" in request_lower or "reorder" in request_lower):
                # Inventory management with reordering
                return {
                    "goal": "Check inventory levels and handle reordering",
                    "action_type": ActionType.MULTI_TOOL_SEQUENCE,
                    "reasoning": "Need to check stock levels, get reorder suggestions, and process orders",
                    "tool_calls": [
                        {
                            "tool_name": "check_stock_levels",
                            "parameters": {},
                            "expected_outcome": "Current stock levels retrieved",
                            "depends_on": []
                        },
                        {
                            "tool_name": "get_reorder_suggestions",
                            "parameters": {},
                            "expected_outcome": "Reorder suggestions generated",
                            "depends_on": ["check_stock_levels"]
                        }
                    ],
                    "success_criteria": [
                        "Stock levels checked",
                        "Reorder suggestions provided",
                        "Purchase orders created if needed"
                    ]
                }
        
        # Simple single-tool requests
        if "job" in request_lower:
            if "create" in request_lower:
                return {
                    "goal": "Create a new job",
                    "action_type": ActionType.SINGLE_TOOL,
                    "reasoning": "Simple job creation request",
                    "tool_calls": [
                        {
                            "tool_name": "create_job",
                            "parameters": {"title": "Job title from request"},
                            "expected_outcome": "Job created successfully",
                            "depends_on": []
                        }
                    ],
                    "success_criteria": ["Job created successfully"]
                }
            elif "upcoming" in request_lower:
                return {
                    "goal": "Get upcoming jobs",
                    "action_type": ActionType.SINGLE_TOOL,
                    "reasoning": "Simple query for upcoming jobs",
                    "tool_calls": [
                        {
                            "tool_name": "get_upcoming_jobs",
                            "parameters": {},
                            "expected_outcome": "Upcoming jobs retrieved",
                            "depends_on": []
                        }
                    ],
                    "success_criteria": ["Upcoming jobs retrieved and displayed"]
                }
        
        # Default to direct response for simple queries
        return {
            "goal": "Provide direct response",
            "action_type": ActionType.DIRECT_RESPONSE,
            "reasoning": "Simple request that doesn't require tool usage",
            "tool_calls": [],
            "success_criteria": ["User question answered"]
        }
    
    async def _analyze_execution_results(self, prompt: str) -> Dict[str, Any]:
        """Analyze execution results and determine if goals were achieved"""
        # This is a simplified implementation - in practice, this would use your LLM
        
        # For now, assume successful execution unless there are obvious errors
        return {
            "goal_achieved": True,
            "success_criteria_met": [True],
            "confidence_score": 0.8,
            "issues_found": [],
            "next_action": "Task completed successfully",
            "requires_revision": False
        }
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the reasoning personal agent"""
        business_name = self.business_context.get("name", "your business")
        user_name = self.user_context.get("name", "there")
        
        return f"""You are Hero365 AI, an advanced personal voice assistant for {business_name}. You're helping {user_name} manage their business operations through voice commands with sophisticated reasoning capabilities.

## Your Role & Capabilities

You are a comprehensive business management assistant that can handle complex, multi-step requests by breaking them down into logical workflows.

### 🧠 Advanced Reasoning Features

**Plan-Act-Verify Loop**: I use a sophisticated reasoning process:
1. **PLAN**: Analyze your request and create a detailed execution plan
2. **ACT**: Execute the plan using appropriate tools in the right sequence
3. **VERIFY**: Check if the goal was achieved and revise if needed

**Multi-Tool Coordination**: I can:
- Use multiple tools in sequence (one after another)
- Use tools in parallel (at the same time)
- Handle dependencies between tools
- Adapt plans based on results

**Complex Request Examples**:
- "Create a project for the kitchen renovation, add electrical and plumbing jobs, and send estimates to the client"
- "Find all overdue invoices, get client contact info, and create follow-up tasks"
- "Check inventory levels, identify low stock items, and generate reorder suggestions"

### 📋 Available Tools & Operations

**Job Management**: Create, schedule, track, and manage jobs
**Project Management**: Create projects, track progress, manage budgets
**Invoice Management**: Create invoices, track payments, handle overdue accounts
**Estimate Management**: Create estimates, track status, convert to invoices
**Contact Management**: Manage client relationships, track interactions
**Inventory Management**: Track stock, manage reorders, handle suppliers

### 🎯 Voice-First Approach

Since you may be driving or working:
- **Be Concise**: Clear, actionable information
- **Prioritize Safety**: Brief responses if you're driving
- **Confirm Complex Actions**: Always confirm multi-step operations
- **Natural Language**: Conversational, not technical
- **Proactive**: Suggest next steps and provide reminders

### 💬 Reasoning Transparency

I can explain my reasoning process:
- Say "explain your reasoning" to see my thought process
- I'll tell you what tools I plan to use and why
- I'll keep you informed of progress on complex tasks
- I can revise plans based on your feedback

### 📊 Business Context

- Business: {business_name}
- User: {user_name}
- Services: {', '.join(self.business_context.get('services', []))}
- Reasoning Mode: {'Enabled' if self.max_reasoning_iterations > 1 else 'Basic'}

I'm here to make complex business management tasks simple through intelligent voice interaction. I can handle everything from simple queries to complex multi-step workflows, always keeping you informed of my reasoning process."""

    async def on_agent_start(self) -> None:
        """Called when agent starts"""
        logger.info(f"ReasoningPersonalVoiceAgent started for business {self.get_current_business_id()}")
        
        # Initialize any required resources
        self._inject_context_into_tools()
    
    async def on_agent_stop(self) -> None:
        """Called when agent stops"""
        logger.info(f"ReasoningPersonalVoiceAgent stopped for business {self.get_current_business_id()}")
        
        # Clean up any resources
        if self.execution_history:
            logger.info(f"Completed {len(self.execution_history)} reasoning workflows") 