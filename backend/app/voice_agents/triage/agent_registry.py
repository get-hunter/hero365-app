"""
Agent Registry for Triage-Based Voice Agent System

Dynamic registry for managing and routing to specialized agents.
"""

from typing import Dict, Any, List, Type, Optional
from dataclasses import dataclass
from ..core.base_agent import BaseVoiceAgent
from .scheduling_agent import SchedulingAgent


@dataclass
class AgentConfig:
    """Configuration for a specialized agent"""
    name: str
    agent_class: Type[BaseVoiceAgent]
    description: str
    capabilities: List[str]
    keywords: List[str]
    priority: int = 1
    requires_permissions: List[str] = None
    business_contexts: List[str] = None  # e.g., ["home_services", "contracting"]
    
    def __post_init__(self):
        if self.requires_permissions is None:
            self.requires_permissions = []
        if self.business_contexts is None:
            self.business_contexts = []


class AgentRegistry:
    """Dynamic registry for managing specialized agents"""
    
    def __init__(self):
        self.agents: Dict[str, AgentConfig] = {}
        self.keyword_map: Dict[str, List[str]] = {}
        self.register_default_agents()
    
    def register_default_agents(self):
        """Register the default specialized agents"""
        
        self.register_agent(AgentConfig(
            name="scheduling",
            agent_class=SchedulingAgent,
            description="Calendar management, appointments, and scheduling",
            capabilities=[
                "Schedule appointments",
                "Check availability", 
                "Reschedule meetings",
                "Block time slots",
                "Send calendar invites",
                "Manage recurring appointments"
            ],
            keywords=[
                "schedule", "calendar", "appointment", "meeting", "book", "reschedule",
                "availability", "time", "date", "when", "available", "busy"
            ],
            priority=2
        ))
        
        # Note: Other specialized agents (Job, Invoice, Estimate, Contact, Project) 
        # will be registered separately when their implementations are created
        # in the triage/specialists/ directory
    
    def register_agent(self, config: AgentConfig):
        """Register a new specialized agent"""
        self.agents[config.name] = config
        
        # Update keyword mapping
        for keyword in config.keywords:
            if keyword not in self.keyword_map:
                self.keyword_map[keyword] = []
            self.keyword_map[keyword].append(config.name)
    
    def get_agent_by_name(self, name: str) -> Optional[AgentConfig]:
        """Get agent configuration by name"""
        return self.agents.get(name)
    
    def get_all_agents(self) -> List[AgentConfig]:
        """Get all registered agents"""
        return list(self.agents.values())
    
    def get_agent_descriptions(self) -> str:
        """Get formatted descriptions of all available agents"""
        descriptions = []
        for config in self.agents.values():
            descriptions.append(f"**{config.name.title()}**: {config.description}")
        return "\n".join(descriptions)
    
    def create_agent(self, name: str, business_context: Dict[str, Any], 
                    user_context: Dict[str, Any]) -> BaseVoiceAgent:
        """Create an instance of a specialized agent"""
        config = self.get_agent_by_name(name)
        if not config:
            raise ValueError(f"Unknown agent: {name}")
        
        # Check business context compatibility
        if config.business_contexts and business_context.get("type"):
            if business_context["type"] not in config.business_contexts:
                raise ValueError(f"Agent {name} not compatible with business type {business_context['type']}")
        
        return config.agent_class(business_context, user_context)
    
    def find_agents_by_keywords(self, text: str, limit: int = 3) -> List[str]:
        """Find agents based on keyword matching in text"""
        text_lower = text.lower()
        agent_scores = {}
        
        # Score agents based on keyword matches
        for word in text_lower.split():
            if word in self.keyword_map:
                for agent_name in self.keyword_map[word]:
                    if agent_name not in agent_scores:
                        agent_scores[agent_name] = 0
                    agent_scores[agent_name] += 1
        
        # Sort by score and priority
        sorted_agents = sorted(
            agent_scores.items(), 
            key=lambda x: (x[1], self.agents[x[0]].priority), 
            reverse=True
        )
        
        return [agent_name for agent_name, _ in sorted_agents[:limit]]
    
    def get_compatible_agents(self, business_context: Dict[str, Any], 
                           user_context: Dict[str, Any]) -> List[str]:
        """Get agents compatible with current business and user context"""
        compatible_agents = []
        business_type = business_context.get("type", "")
        user_permissions = user_context.get("permissions", [])
        
        for name, config in self.agents.items():
            # Check business context compatibility
            if config.business_contexts and business_type:
                if business_type not in config.business_contexts:
                    continue
            
            # Check permission requirements
            if config.requires_permissions:
                if not any(perm in user_permissions for perm in config.requires_permissions):
                    continue
            
            compatible_agents.append(name)
        
        return compatible_agents
    
    def get_routing_suggestions(self, user_request: str, business_context: Dict[str, Any], 
                             user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get routing suggestions with confidence scores"""
        suggestions = []
        
        # Get keyword-based matches
        keyword_matches = self.find_agents_by_keywords(user_request)
        
        # Get compatible agents
        compatible_agents = self.get_compatible_agents(business_context, user_context)
        
        # Combine and score suggestions
        for agent_name in keyword_matches:
            if agent_name in compatible_agents:
                config = self.agents[agent_name]
                
                # Calculate confidence score (simplified)
                confidence = self._calculate_confidence(user_request, config)
                
                suggestions.append({
                    "agent_name": agent_name,
                    "description": config.description,
                    "confidence": confidence,
                    "capabilities": config.capabilities[:3]  # Top 3 capabilities
                })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return suggestions
    
    def _calculate_confidence(self, user_request: str, config: AgentConfig) -> float:
        """Calculate confidence score for routing (simplified implementation)"""
        request_lower = user_request.lower()
        keyword_matches = sum(1 for keyword in config.keywords if keyword in request_lower)
        
        # Base confidence on keyword matches and agent priority
        base_confidence = min(keyword_matches * 0.2, 0.8)
        priority_bonus = config.priority * 0.05
        
        return min(base_confidence + priority_bonus, 1.0)
    
    def get_agent_capabilities_summary(self) -> Dict[str, List[str]]:
        """Get a summary of all agent capabilities"""
        capabilities = {}
        for name, config in self.agents.items():
            capabilities[name] = config.capabilities
        return capabilities
    
    def validate_agent_registration(self, config: AgentConfig) -> bool:
        """Validate that an agent configuration is valid"""
        if not config.name or not config.agent_class:
            return False
        
        if not config.description or not config.capabilities:
            return False
        
        if not config.keywords:
            return False
        
        # Check that agent class is a subclass of BaseVoiceAgent
        if not issubclass(config.agent_class, BaseVoiceAgent):
            return False
        
        return True


# Create default registry instance
default_registry = AgentRegistry()


 