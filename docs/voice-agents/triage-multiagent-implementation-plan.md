# Triage-Based Multiagent Voice System Implementation Plan

## Executive Summary

This plan outlines the implementation of a scalable triage-based multiagent voice system that addresses the current scaling concerns with the personal agent approach (25+ tools) and provides intelligent routing to specialized agents.

## Current Architecture Issues

### Personal Agent Problems
- **Tool Overload**: Single agent with 25+ tools leads to poor performance
- **Context Confusion**: Hard to maintain domain expertise across all business functions
- **Scaling Bottleneck**: Adding new features means adding more tools to already overloaded agent

### Orchestrated Agent Limitations
- **No Intelligent Triage**: Simple handoff pattern without context-aware routing
- **Limited Context**: Doesn't leverage user, business, location, time data effectively
- **Manual Routing**: Relies on handoffs rather than intelligent intent analysis

## Proposed Architecture

### Core Components

1. **Triage Agent** - Central intelligence that analyzes user context and routes to specialists
2. **Specialized Agents** - Domain-focused agents with specific tools and expertise
3. **Context System** - Comprehensive user, business, location, time context
4. **Agent Registry** - Dynamic system for managing and adding specialized agents
5. **Parallel Execution** - Handle multi-domain requests efficiently

### Architecture Diagram

```
User Input → Triage Agent → Context Analysis → Intent Classification → Route to Specialist(s)
                ↓
        [Scheduling] [Jobs] [Invoices] [Estimates] [Contacts] [Payments] [Customer Service] [Inventory]
                ↓
        Response Synthesis ← Parallel Execution ← Specialized Agent Results
```

## Implementation Steps

### Phase 1: Core Triage System

#### 1.1 Create Intelligent Triage Agent

```python
# backend/app/voice_agents/triage/triage_agent.py
class TriageAgent(BaseVoiceAgent):
    """
    Central triage agent that analyzes user context and routes to appropriate specialists.
    
    Context-aware routing based on:
    - User intent analysis
    - Business context (type, size, industry)
    - User role and permissions
    - Location and time context
    - Conversation history
    """
    
    def get_instructions(self) -> str:
        return f"""You are the Hero365 AI Assistant Triage Agent for {self.business_context['name']}.

CORE MISSION:
Analyze user requests and route them to the most appropriate specialist agents based on intent, context, and business needs.

CONTEXT AWARENESS:
- Business: {self.business_context['name']} ({self.business_context['type']})
- User: {self.user_context['name']} ({self.user_context.get('role', 'User')})
- Location: {self.user_context.get('location', 'Unknown')}
- Time: {self.get_current_time()}
- Driving Mode: {"ON" if self.is_driving_mode() else "OFF"}

AVAILABLE SPECIALISTS:
1. **Scheduling Agent** - Calendar management, appointments, availability
2. **Job Agent** - Job creation, updates, tracking, completion
3. **Project Agent** - Project management, milestones, progress
4. **Invoice Agent** - Billing, payments, payment tracking
5. **Estimate Agent** - Quote creation, estimate management
6. **Contact Agent** - Client management, communication, follow-ups
7. **Payment Agent** - Payment processing, refunds, financial tracking
8. **Customer Service Agent** - Support, issue resolution, complaints
9. **Inventory Agent** - Stock management, product tracking, reordering

ROUTING LOGIC:
- Analyze user intent using natural language understanding
- Consider business context and user role
- Route to single specialist for simple requests
- Use parallel routing for complex, multi-domain requests
- Escalate to human support when needed

RESPONSE PATTERN:
1. Acknowledge user request
2. Analyze intent and context
3. Route to appropriate specialist(s)
4. Provide routing explanation
5. Synthesize specialist responses into coherent answer

SAFETY PROTOCOLS:
{"- Keep responses brief and hands-free friendly" if self.is_driving_mode() else ""}
{"- Avoid complex multi-step processes while driving" if self.is_driving_mode() else ""}
"""
```

#### 1.2 Context System Enhancement

```python
# backend/app/voice_agents/core/context_manager.py
class ContextManager:
    """Enhanced context management for triage-based routing"""
    
    def __init__(self, business_context: Dict, user_context: Dict):
        self.business_context = business_context
        self.user_context = user_context
        
    def get_routing_context(self) -> Dict[str, Any]:
        """Get comprehensive context for intelligent routing"""
        return {
            "business": {
                "name": self.business_context.get("name"),
                "type": self.business_context.get("type"),
                "size": self.business_context.get("size"),
                "industry": self.business_context.get("industry")
            },
            "user": {
                "name": self.user_context.get("name"),
                "role": self.user_context.get("role"),
                "permissions": self.user_context.get("permissions", []),
                "preferences": self.user_context.get("preferences", {})
            },
            "session": {
                "location": self.user_context.get("location"),
                "time_zone": self.user_context.get("time_zone"),
                "is_driving": self.user_context.get("is_driving", False),
                "device_type": self.user_context.get("device_type")
            },
            "temporal": {
                "current_time": datetime.now().isoformat(),
                "business_hours": self.get_business_hours(),
                "day_of_week": datetime.now().strftime("%A")
            }
        }
```

### Phase 2: Specialized Agent Refactoring

#### 2.1 Agent-as-Tool Pattern

```python
# backend/app/voice_agents/triage/specialist_tools.py
class SpecialistAgentTools:
    """Convert specialized agents into callable tools for triage agent"""
    
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager
        
    @tool
    async def schedule_management(self, request: str) -> str:
        """Handle scheduling, calendar management, and appointment booking"""
        agent = SchedulingAgent(
            self.context_manager.business_context,
            self.context_manager.user_context
        )
        return await self.execute_specialist(agent, request)
    
    @tool
    async def job_management(self, request: str) -> str:
        """Handle job creation, updates, tracking, and completion"""
        agent = JobAgent(
            self.context_manager.business_context,
            self.context_manager.user_context
        )
        return await self.execute_specialist(agent, request)
    
    @tool
    async def invoice_management(self, request: str) -> str:
        """Handle billing, invoicing, and payment tracking"""
        agent = InvoiceAgent(
            self.context_manager.business_context,
            self.context_manager.user_context
        )
        return await self.execute_specialist(agent, request)
    
    # ... Additional specialist tools
```

#### 2.2 Enhanced Specialized Agents

```python
# backend/app/voice_agents/specialists/scheduling_agent.py
class SchedulingAgent(BaseVoiceAgent):
    """Specialized agent for scheduling and calendar management"""
    
    def get_instructions(self) -> str:
        return f"""You are the Scheduling Specialist for {self.business_context['name']}.

EXPERTISE FOCUS:
- Calendar management and scheduling
- Appointment booking and rescheduling
- Availability checking
- Schedule optimization
- Meeting coordination

CONTEXT AWARENESS:
- Current time: {self.get_current_time()}
- Business hours: {self.get_business_hours()}
- User timezone: {self.user_context.get('time_zone')}

CAPABILITIES:
- Check availability for appointments
- Schedule new appointments
- Reschedule existing appointments
- Block time for specific activities
- Send calendar invites
- Manage recurring appointments

COMMUNICATION STYLE:
- Be precise about dates and times
- Always confirm scheduling details
- Suggest alternative times if conflicts exist
- Consider user preferences and constraints
"""

    def get_tools(self) -> List[Any]:
        return [
            self.check_availability,
            self.schedule_appointment,
            self.reschedule_appointment,
            self.block_time,
            self.send_calendar_invite,
            self.get_upcoming_appointments
        ]
```

### Phase 3: New Specialized Agents

#### 3.1 Payment Agent

```python
# backend/app/voice_agents/specialists/payment_agent.py
class PaymentAgent(BaseVoiceAgent):
    """Specialized agent for payment processing and financial transactions"""
    
    def get_instructions(self) -> str:
        return f"""You are the Payment Specialist for {self.business_context['name']}.

EXPERTISE FOCUS:
- Payment processing and transactions
- Refund management
- Financial tracking and reporting
- Payment method management
- Dispute resolution

SECURITY PROTOCOLS:
- Never store or log sensitive payment information
- Always verify user authorization for financial transactions
- Use secure payment processing methods
- Confirm all financial transactions before execution

CAPABILITIES:
- Process payments for invoices
- Handle refund requests
- Track payment status
- Manage payment methods
- Generate financial reports
"""
```

#### 3.2 Customer Service Agent

```python
# backend/app/voice_agents/specialists/customer_service_agent.py
class CustomerServiceAgent(BaseVoiceAgent):
    """Specialized agent for customer service and support"""
    
    def get_instructions(self) -> str:
        return f"""You are the Customer Service Specialist for {self.business_context['name']}.

EXPERTISE FOCUS:
- Issue resolution and troubleshooting
- Customer complaint handling
- Support ticket management
- Service quality assurance
- Escalation management

COMMUNICATION STYLE:
- Be empathetic and understanding
- Listen actively to customer concerns
- Provide clear solutions and next steps
- Follow up on unresolved issues
- Maintain professional demeanor

ESCALATION TRIGGERS:
- Legal or regulatory issues
- Major service failures
- High-value client complaints
- Complex technical problems
"""
```

### Phase 4: Advanced Features

#### 4.1 Parallel Execution System

```python
# backend/app/voice_agents/triage/parallel_executor.py
class ParallelExecutor:
    """Execute multiple specialized agents in parallel for complex requests"""
    
    async def execute_parallel_agents(self, 
                                    agent_requests: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Execute multiple specialist agents concurrently
        
        Args:
            agent_requests: List of (agent_name, request) tuples
            
        Returns:
            Dict mapping agent names to their responses
        """
        tasks = []
        for agent_name, request in agent_requests:
            task = self.execute_specialist_async(agent_name, request)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        return {
            agent_requests[i][0]: results[i] 
            for i in range(len(agent_requests))
        }
```

#### 4.2 Dynamic Agent Registry

```python
# backend/app/voice_agents/triage/agent_registry.py
class AgentRegistry:
    """Dynamic registry for managing specialized agents"""
    
    def __init__(self):
        self.agents = {}
        self.register_default_agents()
    
    def register_agent(self, name: str, agent_class: Type[BaseVoiceAgent], 
                      description: str, capabilities: List[str]):
        """Register a new specialized agent"""
        self.agents[name] = {
            "class": agent_class,
            "description": description,
            "capabilities": capabilities
        }
    
    def get_agent_descriptions(self) -> str:
        """Get formatted descriptions of all available agents"""
        descriptions = []
        for name, config in self.agents.items():
            descriptions.append(f"**{name}**: {config['description']}")
        return "\n".join(descriptions)
    
    def create_agent(self, name: str, business_context: Dict, 
                    user_context: Dict) -> BaseVoiceAgent:
        """Create an instance of a specialized agent"""
        if name not in self.agents:
            raise ValueError(f"Unknown agent: {name}")
        
        agent_class = self.agents[name]["class"]
        return agent_class(business_context, user_context)
```

### Phase 5: Integration Updates

#### 5.1 Updated Voice Agent API

```python
# backend/app/api/routes/openai_voice_agent.py
@router.post("/start")
async def start_voice_agent_session(request: VoiceAgentStartRequest):
    """Start a new voice agent session with triage-based routing"""
    
    # Create context manager
    context_manager = ContextManager(
        business_context=business_data,
        user_context=user_context
    )
    
    # Create triage agent with all specialist tools
    triage_agent = TriageAgent(
        business_context=business_data,
        user_context=user_context,
        context_manager=context_manager
    )
    
    # Initialize session
    session = VoiceAgentSession(
        session_id=session_id,
        agent=triage_agent,
        context_manager=context_manager
    )
    
    return VoiceAgentStartResponse(
        session_id=session_id,
        agent_name=triage_agent.get_agent_name(),
        greeting=triage_agent.get_personalized_greeting(),
        available_capabilities=triage_agent.get_available_capabilities()
    )
```

## Benefits of New Architecture

### 1. Scalability
- **Modular Design**: Easy to add new specialized agents without affecting existing ones
- **Tool Distribution**: No single agent overloaded with tools
- **Parallel Processing**: Handle complex multi-domain requests efficiently

### 2. Performance
- **Focused Expertise**: Each agent optimized for specific domain
- **Intelligent Routing**: Direct requests to most appropriate specialist
- **Context Awareness**: Leverage user, business, location, time data

### 3. Maintainability
- **Clear Separation**: Each agent has distinct responsibilities
- **Easy Testing**: Test each specialist independently
- **Simple Updates**: Modify single agent without affecting others

### 4. User Experience
- **Intelligent Responses**: Context-aware routing for better accuracy
- **Faster Resolution**: Direct routing to appropriate specialist
- **Consistent Experience**: Unified interface with specialized expertise

## Example User Interactions

### Simple Request
```
User: "Schedule a meeting with John for tomorrow at 2 PM"
Triage Agent: Analyzes intent → Routes to Scheduling Agent
Scheduling Agent: Checks availability → Creates appointment
Response: "Meeting scheduled with John for tomorrow at 2 PM"
```

### Complex Multi-Domain Request
```
User: "I need to create an invoice for the Johnson job, schedule a follow-up, and check my inventory"
Triage Agent: Analyzes intent → Routes to Invoice + Scheduling + Inventory agents (parallel)
All Agents: Execute simultaneously
Response: Synthesized response covering all three domains
```

### Context-Aware Routing
```
User: "Check my schedule" (while driving)
Triage Agent: Detects driving mode → Routes to Scheduling Agent with safety constraints
Scheduling Agent: Provides brief, voice-optimized schedule summary
```

## Migration Strategy

1. **Parallel Development**: Build new triage system alongside existing system
2. **Gradual Rollout**: Start with specific business functions, expand gradually
3. **A/B Testing**: Compare performance against existing personal agent
4. **Monitoring**: Track routing accuracy and user satisfaction
5. **Feedback Loop**: Continuously improve routing logic based on usage patterns

## Success Metrics

- **Routing Accuracy**: Percentage of requests routed to correct specialist
- **Response Time**: Average time to resolve user requests
- **User Satisfaction**: Qualitative feedback on response quality
- **System Scalability**: Ability to add new agents without performance degradation
- **Tool Utilization**: Distribution of tool usage across specialists

This architecture provides a robust foundation for scaling your voice agent system while maintaining high performance and user experience. 