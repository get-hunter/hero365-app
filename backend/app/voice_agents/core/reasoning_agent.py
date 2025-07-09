"""
Reasoning Agent for Hero365

This module provides advanced reasoning capabilities for voice agents,
implementing a Plan-Act-Verify loop for complex multi-tool workflows.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from livekit.agents import function_tool
from pydantic import BaseModel, Field

from app.voice_agents.core.base_agent import BaseVoiceAgent

logger = logging.getLogger(__name__)


class ActionType(str, Enum):
    """Types of actions the agent can perform"""
    DIRECT_RESPONSE = "direct_response"
    SINGLE_TOOL = "single_tool"
    MULTI_TOOL_SEQUENCE = "multi_tool_sequence"
    MULTI_TOOL_PARALLEL = "multi_tool_parallel"


class ExecutionStatus(str, Enum):
    """Status of plan execution"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVISION = "needs_revision"


@dataclass
class ToolCall:
    """Represents a planned tool call"""
    tool_name: str
    parameters: Dict[str, Any]
    expected_outcome: str
    depends_on: Optional[List[str]] = None  # Tool names this depends on
    execution_status: ExecutionStatus = ExecutionStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class ExecutionPlan:
    """Represents the agent's execution plan"""
    goal: str
    action_type: ActionType
    reasoning: str
    tool_calls: List[ToolCall]
    success_criteria: List[str]
    fallback_plan: Optional[str] = None
    execution_status: ExecutionStatus = ExecutionStatus.PENDING


class PlanningResponse(BaseModel):
    """Structured response from the planning phase"""
    goal: str = Field(description="The main objective to achieve")
    action_type: ActionType = Field(description="Type of action to perform")
    reasoning: str = Field(description="Reasoning behind the chosen approach")
    tool_calls: List[Dict[str, Any]] = Field(description="List of tool calls to make")
    success_criteria: List[str] = Field(description="How to measure success")
    fallback_plan: Optional[str] = Field(description="What to do if the plan fails")


class VerificationResponse(BaseModel):
    """Structured response from the verification phase"""
    goal_achieved: bool = Field(description="Whether the goal was achieved")
    success_criteria_met: List[bool] = Field(description="Which success criteria were met")
    confidence_score: float = Field(description="Confidence in the result (0-1)")
    issues_found: List[str] = Field(description="Any issues or problems identified")
    next_action: str = Field(description="What should happen next")
    requires_revision: bool = Field(description="Whether the plan needs revision")


class ReasoningVoiceAgent(BaseVoiceAgent):
    """Advanced voice agent with reasoning capabilities"""
    
    def __init__(self, 
                 business_context: Dict[str, Any],
                 user_context: Dict[str, Any],
                 config: Optional[Dict[str, Any]] = None,
                 max_reasoning_iterations: int = 3):
        """
        Initialize the reasoning voice agent.
        
        Args:
            business_context: Business-specific context and configuration
            user_context: User-specific context and preferences
            config: Agent configuration (optional)
            max_reasoning_iterations: Maximum number of Plan-Act-Verify cycles
        """
        super().__init__(business_context, user_context, config)
        
        self.max_reasoning_iterations = max_reasoning_iterations
        self.current_plan: Optional[ExecutionPlan] = None
        self.execution_history: List[ExecutionPlan] = []
        self.available_tools: Dict[str, Callable] = {}
        self.reasoning_iteration = 0
        
        # Initialize tools
        self._initialize_tools()
        
        logger.info(f"ReasoningVoiceAgent initialized with {len(self.available_tools)} tools")
    
    def _initialize_tools(self) -> None:
        """Initialize and catalog all available tools"""
        # This will be populated by the implementing class
        pass
    
    def get_tools(self) -> List[Callable]:
        """Get all available voice tools including reasoning tools"""
        reasoning_tools = [
            self.execute_reasoning_workflow,
            self.revise_current_plan,
            self.explain_reasoning,
        ]
        
        # Add all registered tools
        return reasoning_tools + list(self.available_tools.values())
    
    @function_tool
    async def execute_reasoning_workflow(self, user_request: str) -> str:
        """
        Execute a complete reasoning workflow for complex requests.
        
        Args:
            user_request: The user's request requiring reasoning
            
        Returns:
            str: The final response after reasoning and execution
        """
        logger.info(f"Starting reasoning workflow for: {user_request}")
        
        self.reasoning_iteration = 0
        
        while self.reasoning_iteration < self.max_reasoning_iterations:
            self.reasoning_iteration += 1
            
            # PLAN Phase
            plan = await self._plan_phase(user_request)
            if not plan:
                return "I apologize, but I couldn't create a plan for your request. Could you please rephrase it?"
            
            self.current_plan = plan
            
            # ACT Phase
            execution_result = await self._act_phase(plan)
            
            # VERIFY Phase
            verification = await self._verify_phase(plan, execution_result)
            
            # Check if we're done
            if verification.goal_achieved and not verification.requires_revision:
                return self._generate_final_response(plan, execution_result, verification)
            
            # If revision is needed and we have iterations left, continue
            if verification.requires_revision and self.reasoning_iteration < self.max_reasoning_iterations:
                logger.info(f"Plan revision needed. Iteration {self.reasoning_iteration}/{self.max_reasoning_iterations}")
                user_request = f"Previous attempt: {user_request}\nIssues found: {', '.join(verification.issues_found)}\nRevision needed: {verification.next_action}"
                continue
            
            # If we can't revise or ran out of iterations, return what we have
            return self._generate_partial_response(plan, execution_result, verification)
        
        return "I've reached my reasoning limit. Let me provide what I was able to accomplish."
    
    async def _plan_phase(self, user_request: str) -> Optional[ExecutionPlan]:
        """
        Planning phase: Analyze the request and create an execution plan
        
        Args:
            user_request: The user's request
            
        Returns:
            ExecutionPlan: The created plan, or None if planning failed
        """
        logger.info("Entering PLAN phase")
        
        # Get available tools description
        tool_descriptions = self._get_tool_descriptions()
        
        # Create planning prompt
        planning_prompt = self._create_planning_prompt(user_request, tool_descriptions)
        
        try:
            # Use LLM to create plan (this would be integrated with your LLM)
            # For now, simulating the planning logic
            planning_response = await self._call_planning_llm(planning_prompt)
            
            # Convert to ExecutionPlan
            plan = self._convert_to_execution_plan(planning_response)
            
            logger.info(f"Plan created: {plan.action_type.value} with {len(plan.tool_calls)} tool calls")
            return plan
            
        except Exception as e:
            logger.error(f"Planning failed: {str(e)}")
            return None
    
    async def _act_phase(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Acting phase: Execute the planned actions
        
        Args:
            plan: The execution plan
            
        Returns:
            Dict[str, Any]: Results of the execution
        """
        logger.info("Entering ACT phase")
        
        plan.execution_status = ExecutionStatus.IN_PROGRESS
        results = {}
        
        if plan.action_type == ActionType.DIRECT_RESPONSE:
            # No tools needed, just respond
            results["response"] = "Direct response generated"
            
        elif plan.action_type == ActionType.SINGLE_TOOL:
            # Execute single tool
            if plan.tool_calls:
                tool_call = plan.tool_calls[0]
                result = await self._execute_tool_call(tool_call)
                results[tool_call.tool_name] = result
                
        elif plan.action_type == ActionType.MULTI_TOOL_SEQUENCE:
            # Execute tools in sequence
            for tool_call in plan.tool_calls:
                # Check dependencies
                if await self._check_dependencies(tool_call, results):
                    result = await self._execute_tool_call(tool_call)
                    results[tool_call.tool_name] = result
                else:
                    tool_call.execution_status = ExecutionStatus.FAILED
                    tool_call.error = "Dependencies not met"
                    
        elif plan.action_type == ActionType.MULTI_TOOL_PARALLEL:
            # Execute tools in parallel (simplified - in practice you'd use asyncio.gather)
            for tool_call in plan.tool_calls:
                if not tool_call.depends_on:  # Only execute tools without dependencies in parallel
                    result = await self._execute_tool_call(tool_call)
                    results[tool_call.tool_name] = result
        
        plan.execution_status = ExecutionStatus.COMPLETED
        return results
    
    async def _verify_phase(self, plan: ExecutionPlan, execution_result: Dict[str, Any]) -> VerificationResponse:
        """
        Verification phase: Check if the execution achieved the goal
        
        Args:
            plan: The execution plan
            execution_result: Results from the execution
            
        Returns:
            VerificationResponse: Verification results
        """
        logger.info("Entering VERIFY phase")
        
        # Create verification prompt
        verification_prompt = self._create_verification_prompt(plan, execution_result)
        
        try:
            # Use LLM to verify results
            verification = await self._call_verification_llm(verification_prompt)
            
            logger.info(f"Verification complete: Goal achieved = {verification.goal_achieved}")
            return verification
            
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return VerificationResponse(
                goal_achieved=False,
                success_criteria_met=[False] * len(plan.success_criteria),
                confidence_score=0.0,
                issues_found=[f"Verification error: {str(e)}"],
                next_action="Retry with simpler approach",
                requires_revision=True
            )
    
    async def _execute_tool_call(self, tool_call: ToolCall) -> Any:
        """Execute a single tool call"""
        try:
            tool_call.execution_status = ExecutionStatus.IN_PROGRESS
            
            if tool_call.tool_name in self.available_tools:
                tool_func = self.available_tools[tool_call.tool_name]
                result = await tool_func(**tool_call.parameters)
                
                tool_call.execution_status = ExecutionStatus.COMPLETED
                tool_call.result = result
                return result
            else:
                raise ValueError(f"Tool {tool_call.tool_name} not found")
                
        except Exception as e:
            tool_call.execution_status = ExecutionStatus.FAILED
            tool_call.error = str(e)
            logger.error(f"Tool execution failed: {tool_call.tool_name} - {str(e)}")
            return None
    
    async def _check_dependencies(self, tool_call: ToolCall, results: Dict[str, Any]) -> bool:
        """Check if tool dependencies are satisfied"""
        if not tool_call.depends_on:
            return True
        
        for dependency in tool_call.depends_on:
            if dependency not in results or results[dependency] is None:
                return False
        
        return True
    
    def _get_tool_descriptions(self) -> str:
        """Get descriptions of all available tools"""
        descriptions = []
        for tool_name, tool_func in self.available_tools.items():
            doc = tool_func.__doc__ or "No description available"
            descriptions.append(f"- {tool_name}: {doc.strip()}")
        
        return "\n".join(descriptions)
    
    def _create_planning_prompt(self, user_request: str, tool_descriptions: str) -> str:
        """Create the planning prompt for the LLM"""
        return f"""You are an AI assistant that creates execution plans for business management tasks.

USER REQUEST: {user_request}

AVAILABLE TOOLS:
{tool_descriptions}

BUSINESS CONTEXT:
- Business: {self.business_context.get('name', 'Unknown')}
- Services: {', '.join(self.business_context.get('services', []))}

Create a detailed execution plan that includes:
1. Goal: What we're trying to achieve
2. Action type: How to approach this (direct_response, single_tool, multi_tool_sequence, multi_tool_parallel)
3. Reasoning: Why this approach is best
4. Tool calls: Which tools to use and how
5. Success criteria: How to measure success
6. Fallback plan: What to do if this fails

Respond in the exact JSON format specified by the PlanningResponse schema."""
    
    def _create_verification_prompt(self, plan: ExecutionPlan, execution_result: Dict[str, Any]) -> str:
        """Create the verification prompt for the LLM"""
        return f"""You are verifying if an execution plan achieved its goal.

ORIGINAL GOAL: {plan.goal}
SUCCESS CRITERIA: {plan.success_criteria}
EXECUTION RESULTS: {json.dumps(execution_result, indent=2)}

Please evaluate:
1. Was the goal achieved?
2. Which success criteria were met?
3. What's your confidence level (0-1)?
4. What issues were found?
5. What should happen next?
6. Does the plan need revision?

Respond in the exact JSON format specified by the VerificationResponse schema."""
    
    async def _call_planning_llm(self, prompt: str) -> PlanningResponse:
        """Call LLM for planning (placeholder - integrate with your LLM)"""
        # This would be integrated with your actual LLM service
        # For now, returning a mock response
        return PlanningResponse(
            goal="Mock goal",
            action_type=ActionType.DIRECT_RESPONSE,
            reasoning="Mock reasoning",
            tool_calls=[],
            success_criteria=["Mock success criteria"],
            fallback_plan="Mock fallback"
        )
    
    async def _call_verification_llm(self, prompt: str) -> VerificationResponse:
        """Call LLM for verification (placeholder - integrate with your LLM)"""
        # This would be integrated with your actual LLM service
        # For now, returning a mock response
        return VerificationResponse(
            goal_achieved=True,
            success_criteria_met=[True],
            confidence_score=0.8,
            issues_found=[],
            next_action="Task completed successfully",
            requires_revision=False
        )
    
    def _convert_to_execution_plan(self, planning_response: PlanningResponse) -> ExecutionPlan:
        """Convert PlanningResponse to ExecutionPlan"""
        tool_calls = []
        for tool_call_data in planning_response.tool_calls:
            tool_calls.append(ToolCall(
                tool_name=tool_call_data.get("tool_name", ""),
                parameters=tool_call_data.get("parameters", {}),
                expected_outcome=tool_call_data.get("expected_outcome", ""),
                depends_on=tool_call_data.get("depends_on", [])
            ))
        
        return ExecutionPlan(
            goal=planning_response.goal,
            action_type=planning_response.action_type,
            reasoning=planning_response.reasoning,
            tool_calls=tool_calls,
            success_criteria=planning_response.success_criteria,
            fallback_plan=planning_response.fallback_plan
        )
    
    def _generate_final_response(self, plan: ExecutionPlan, execution_result: Dict[str, Any], verification: VerificationResponse) -> str:
        """Generate the final response to the user"""
        return f"I've successfully completed your request: {plan.goal}. {verification.next_action}"
    
    def _generate_partial_response(self, plan: ExecutionPlan, execution_result: Dict[str, Any], verification: VerificationResponse) -> str:
        """Generate response when plan couldn't be fully completed"""
        return f"I made progress on your request but encountered some issues: {', '.join(verification.issues_found)}. Here's what I was able to accomplish: {verification.next_action}"
    
    @function_tool
    async def revise_current_plan(self, revision_request: str) -> str:
        """
        Revise the current execution plan based on feedback.
        
        Args:
            revision_request: How to revise the plan
            
        Returns:
            str: Status of the revision
        """
        if not self.current_plan:
            return "No current plan to revise."
        
        # Implementation for plan revision
        return f"Plan revised based on: {revision_request}"
    
    @function_tool
    async def explain_reasoning(self) -> str:
        """
        Explain the agent's reasoning process for the current task.
        
        Returns:
            str: Explanation of the reasoning
        """
        if not self.current_plan:
            return "No active reasoning process to explain."
        
        return f"""Here's my reasoning process:

Goal: {self.current_plan.goal}
Approach: {self.current_plan.action_type.value}
Reasoning: {self.current_plan.reasoning}

Tools I planned to use:
{chr(10).join([f"- {tc.tool_name}: {tc.expected_outcome}" for tc in self.current_plan.tool_calls])}

Success criteria:
{chr(10).join([f"- {criteria}" for criteria in self.current_plan.success_criteria])}

Current status: {self.current_plan.execution_status.value}
Iteration: {self.reasoning_iteration}/{self.max_reasoning_iterations}"""
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the reasoning agent"""
        base_prompt = super().get_system_prompt()
        
        reasoning_addition = """

## Advanced Reasoning Capabilities

I have advanced reasoning capabilities that allow me to:

🧠 **Plan Complex Tasks**: Break down complex requests into logical steps
🔄 **Multi-Tool Coordination**: Use multiple tools in sequence or parallel
✅ **Verify Results**: Check if tasks were completed successfully
🔧 **Adapt and Revise**: Adjust plans based on results and feedback

When you give me a complex request, I will:
1. **Plan**: Analyze your request and create an execution plan
2. **Act**: Execute the plan using appropriate tools
3. **Verify**: Check if the goal was achieved
4. **Revise**: Adjust the plan if needed and try again

This means I can handle requests like:
- "Create a project for the kitchen renovation, add all the electrical and plumbing jobs, and send estimates to the client"
- "Find all overdue invoices, contact the clients, and create follow-up tasks"
- "Check inventory levels, create purchase orders for low stock items, and schedule deliveries"

I'll keep you informed of my reasoning process and can explain my thinking at any time."""
        
        return base_prompt + reasoning_addition 