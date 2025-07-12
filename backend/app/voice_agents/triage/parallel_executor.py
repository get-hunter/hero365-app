"""
Parallel Executor for Triage-Based Voice Agent System

Execute multiple specialized agents in parallel for complex multi-domain requests.
"""

import asyncio
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import logging
from ..core.base_agent import BaseVoiceAgent
from .context_manager import ContextManager
from .agent_registry import AgentRegistry, default_registry

logger = logging.getLogger(__name__)


class ParallelExecutor:
    """Execute multiple specialized agents in parallel for complex requests"""
    
    def __init__(self, 
                 context_manager: ContextManager,
                 registry: AgentRegistry = None,
                 max_concurrent_agents: int = 5,
                 timeout_seconds: int = 30):
        """
        Initialize parallel executor
        
        Args:
            context_manager: Context manager for business and user context
            registry: Agent registry for managing specialists
            max_concurrent_agents: Maximum number of agents to run concurrently
            timeout_seconds: Timeout for agent execution
        """
        self.context_manager = context_manager
        self.registry = registry or default_registry
        self.max_concurrent_agents = max_concurrent_agents
        self.timeout_seconds = timeout_seconds
        self._agent_cache: Dict[str, BaseVoiceAgent] = {}
        
    async def execute_parallel_agents(self, 
                                    agent_requests: List[Tuple[str, str]],
                                    return_partial_results: bool = True) -> Dict[str, Any]:
        """
        Execute multiple specialist agents concurrently
        
        Args:
            agent_requests: List of (agent_name, request) tuples
            return_partial_results: Whether to return partial results if some agents fail
            
        Returns:
            Dict mapping agent names to their responses, plus metadata
        """
        if not agent_requests:
            return {"results": {}, "metadata": {"error": "No agent requests provided"}}
        
        # Limit concurrent agents
        if len(agent_requests) > self.max_concurrent_agents:
            logger.warning(f"Limiting concurrent agents from {len(agent_requests)} to {self.max_concurrent_agents}")
            agent_requests = agent_requests[:self.max_concurrent_agents]
        
        start_time = datetime.now()
        results = {}
        errors = {}
        
        try:
            # Create tasks for parallel execution
            tasks = []
            agent_names = []
            
            for agent_name, request in agent_requests:
                # Validate agent exists and user has permission
                if not self._validate_agent_request(agent_name, request):
                    errors[agent_name] = "Agent not available or insufficient permissions"
                    continue
                
                task = self._execute_agent_with_timeout(agent_name, request)
                tasks.append(task)
                agent_names.append(agent_name)
            
            if not tasks:
                return {
                    "results": {},
                    "metadata": {
                        "error": "No valid agent requests to execute",
                        "errors": errors
                    }
                }
            
            # Execute all tasks in parallel with timeout
            try:
                results_list = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=self.timeout_seconds
                )
                
                # Process results
                for i, result in enumerate(results_list):
                    agent_name = agent_names[i]
                    
                    if isinstance(result, Exception):
                        errors[agent_name] = str(result)
                        if return_partial_results:
                            results[agent_name] = f"Error: {str(result)}"
                    else:
                        results[agent_name] = result
                        
            except asyncio.TimeoutError:
                logger.error(f"Parallel execution timed out after {self.timeout_seconds} seconds")
                return {
                    "results": {},
                    "metadata": {
                        "error": f"Execution timed out after {self.timeout_seconds} seconds",
                        "errors": errors
                    }
                }
            
            # Calculate execution metadata
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            metadata = {
                "execution_time_seconds": execution_time,
                "agents_executed": len(results),
                "agents_failed": len(errors),
                "total_agents_requested": len(agent_requests),
                "timestamp": end_time.isoformat()
            }
            
            if errors:
                metadata["errors"] = errors
                
            return {
                "results": results,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Unexpected error in parallel execution: {str(e)}")
            return {
                "results": {},
                "metadata": {
                    "error": f"Unexpected error: {str(e)}",
                    "execution_time_seconds": (datetime.now() - start_time).total_seconds()
                }
            }
    
    async def _execute_agent_with_timeout(self, agent_name: str, request: str) -> str:
        """Execute a single agent with timeout and error handling"""
        try:
            # Get or create agent
            if agent_name in self._agent_cache:
                agent = self._agent_cache[agent_name]
            else:
                agent = self.registry.create_agent(
                    agent_name,
                    self.context_manager.business_context,
                    self.context_manager.user_context
                )
                self._agent_cache[agent_name] = agent
            
            # Execute with timeout
            from agents import Runner
            result = await asyncio.wait_for(
                Runner.run(agent.create_agent(), request),
                timeout=self.timeout_seconds
            )
            
            return result.final_output if hasattr(result, 'final_output') else str(result)
            
        except asyncio.TimeoutError:
            raise Exception(f"Agent {agent_name} timed out after {self.timeout_seconds} seconds")
        except Exception as e:
            raise Exception(f"Agent {agent_name} execution failed: {str(e)}")
    
    def _validate_agent_request(self, agent_name: str, request: str) -> bool:
        """Validate that an agent request is valid and authorized"""
        # Check if agent exists
        config = self.registry.get_agent_by_name(agent_name)
        if not config:
            logger.warning(f"Agent {agent_name} not found in registry")
            return False
        
        # Check permissions
        if config.requires_permissions:
            user_permissions = self.context_manager.get_user_permissions()
            if not any(perm in user_permissions for perm in config.requires_permissions):
                logger.warning(f"User lacks permissions for agent {agent_name}")
                return False
        
        # Check business context compatibility
        if config.business_contexts:
            business_type = self.context_manager.business_context.get("type")
            if business_type and business_type not in config.business_contexts:
                logger.warning(f"Agent {agent_name} not compatible with business type {business_type}")
                return False
        
        return True
    
    async def execute_conditional_agents(self, 
                                       conditional_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute agents based on conditional logic
        
        Args:
            conditional_requests: List of conditional agent requests
                Format: [{"agent": "agent_name", "request": "request_text", "condition": "condition_logic"}]
                
        Returns:
            Dict with results and metadata
        """
        # Evaluate conditions and build agent requests
        agent_requests = []
        
        for req in conditional_requests:
            agent_name = req.get("agent")
            request_text = req.get("request")
            condition = req.get("condition")
            
            if not agent_name or not request_text:
                continue
                
            # Evaluate condition if provided
            if condition:
                if not self._evaluate_condition(condition):
                    continue
            
            agent_requests.append((agent_name, request_text))
        
        return await self.execute_parallel_agents(agent_requests)
    
    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition string (simplified implementation)"""
        # This is a simplified condition evaluator
        # In a full implementation, this would support complex logic
        
        ctx = self.context_manager.get_routing_context()
        
        # Simple condition evaluation
        if "business_hours" in condition:
            return ctx['temporal']['is_business_hours']
        elif "driving" in condition:
            return ctx['session']['is_driving']
        elif "admin" in condition:
            return "admin" in ctx['user']['permissions']
        elif "finance" in condition:
            return "finance" in ctx['user']['permissions']
        
        # Default to true for unknown conditions
        return True
    
    async def execute_sequential_with_dependencies(self, 
                                                 dependent_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute agents sequentially with dependencies
        
        Args:
            dependent_requests: List of dependent agent requests
                Format: [{"agent": "agent_name", "request": "request_text", "depends_on": ["agent1", "agent2"]}]
                
        Returns:
            Dict with results and metadata
        """
        start_time = datetime.now()
        results = {}
        errors = {}
        completed_agents = set()
        
        # Keep trying to execute agents until all are done or we hit a deadlock
        remaining_requests = dependent_requests.copy()
        max_iterations = len(dependent_requests) * 2  # Prevent infinite loops
        iteration = 0
        
        while remaining_requests and iteration < max_iterations:
            iteration += 1
            executed_this_iteration = []
            
            for req in remaining_requests:
                agent_name = req.get("agent")
                request_text = req.get("request")
                dependencies = req.get("depends_on", [])
                
                # Check if dependencies are satisfied
                if all(dep in completed_agents for dep in dependencies):
                    try:
                        # Execute the agent
                        result = await self._execute_agent_with_timeout(agent_name, request_text)
                        results[agent_name] = result
                        completed_agents.add(agent_name)
                        executed_this_iteration.append(req)
                        
                    except Exception as e:
                        errors[agent_name] = str(e)
                        executed_this_iteration.append(req)
            
            # Remove executed requests
            for req in executed_this_iteration:
                remaining_requests.remove(req)
            
            # If nothing was executed this iteration, we have a deadlock
            if not executed_this_iteration:
                for req in remaining_requests:
                    agent_name = req.get("agent")
                    errors[agent_name] = "Dependency deadlock or circular dependency"
                break
        
        # Calculate metadata
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        metadata = {
            "execution_time_seconds": execution_time,
            "agents_executed": len(results),
            "agents_failed": len(errors),
            "total_agents_requested": len(dependent_requests),
            "iterations": iteration,
            "timestamp": end_time.isoformat()
        }
        
        if errors:
            metadata["errors"] = errors
            
        return {
            "results": results,
            "metadata": metadata
        }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return {
            "max_concurrent_agents": self.max_concurrent_agents,
            "timeout_seconds": self.timeout_seconds,
            "cached_agents": len(self._agent_cache),
            "available_agents": len(self.registry.get_all_agents())
        }
    
    def clear_agent_cache(self):
        """Clear cached agents"""
        self._agent_cache.clear()
        
    def set_timeout(self, timeout_seconds: int):
        """Set execution timeout"""
        self.timeout_seconds = max(5, min(300, timeout_seconds))  # 5-300 seconds
        
    def set_max_concurrent(self, max_concurrent: int):
        """Set maximum concurrent agents"""
        self.max_concurrent_agents = max(1, min(10, max_concurrent))  # 1-10 agents 