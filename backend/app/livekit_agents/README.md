# Hero365 LiveKit Agents

This directory contains the LiveKit agents implementation for Hero365, following the latest LiveKit 1.0 patterns and best practices with intelligent agent routing.

## Architecture

The implementation follows an intelligent routing architecture with a main agent that can route to specialist agents:

### Main Agent
- **`worker.py`** - Contains the main `Hero365MainAgent` class that handles voice interactions with intelligent routing to specialist agents

### Specialist Agents
- **`specialists/contact_agent.py`** - Contact management specialist with full CRUD operations
- **`specialists/job_agent.py`** - Job management specialist  
- **`specialists/estimate_agent.py`** - Estimate management specialist
- **`specialists/scheduling_agent.py`** - Scheduling and calendar management specialist

### Support Agents
- **`hero365_triage_agent.py`** - General inquiry and triage agent (available for future use)

## Intelligent Routing System

### How Handoffs Work

The system uses a **main agent** that can intelligently route users to **specialist agents** based on their requests:

1. **Main Agent (`Hero365MainAgent`)**: 
   - Handles initial conversations and business overview
   - Analyzes user intent
   - Routes to appropriate specialists using routing tools
   - Maintains business context across all interactions

2. **Specialist Agents**:
   - Handle specific business functions (contacts, jobs, estimates, scheduling)
   - Have access to specialized tools for their domain
   - Provide deep expertise in their area

3. **Routing Tools**:
   - `route_to_contact_specialist()` - Routes to contact management
   - `route_to_job_specialist()` - Routes to job management
   - `route_to_estimate_specialist()` - Routes to estimate management
   - `route_to_scheduling_specialist()` - Routes to scheduling management

### Example Conversation Flow

```
User: "I need to create a new contact"
Main Agent: "I'll connect you with our contact specialist who can help you manage your contacts, create new ones, search for existing contacts, and handle all contact-related tasks."

User: "Show me my upcoming jobs"
Main Agent: "Let me transfer you to our job specialist who can help you create new jobs, update job status, schedule appointments, track job progress, and manage all your work orders."
```

## Key Features

### Intelligent Routing
- Main agent analyzes user intent and routes to appropriate specialists
- Seamless handoffs without breaking conversation flow
- Context preservation across agent transitions

### Simplified Tool Registration
All agents use the `@function_tool` decorator for tool registration, avoiding the duplicate function name issues that can occur with list-based tool registration.

### Business Context Integration
All agents can be initialized with business context through the `BusinessContextManager`, providing context-aware responses.

### Consistent Error Handling
All tools follow a consistent error handling pattern with proper logging and user-friendly error messages.

### Contact Management Tools
The contact agent provides comprehensive contact management capabilities:
- `create_contact()` - Create new contacts with smart defaults
- `search_contacts()` - Search contacts by name, email, or phone
- `get_suggested_contacts()` - Get context-aware contact suggestions
- `get_contact_details()` - Get detailed contact information
- `update_contact()` - Update existing contact information
- `get_contact_interactions()` - View contact interaction history
- `add_contact_note()` - Add notes to contacts
- `schedule_contact_follow_up()` - Schedule follow-up reminders

## Usage

### Running the Worker
```bash
cd backend
uv run python -m app.livekit_agents.worker dev --log-level debug
```

### Creating Agents
```python
from app.livekit_agents.worker import Hero365MainAgent
from app.livekit_agents.specialists.contact_agent import ContactAgent
from app.livekit_agents.config import LiveKitConfig

# Main agent with routing capabilities
agent = Hero365MainAgent(business_context=business_context, user_context=user_context)

# Specialist agents
config = LiveKitConfig()
contact_agent = ContactAgent(config)
```

### Agent Routing Example
```python
# The main agent automatically routes to specialists based on user requests
# No manual handoff code needed - the routing is handled by the main agent's tools

# User asks about contacts → Main agent uses route_to_contact_specialist()
# User asks about jobs → Main agent uses route_to_job_specialist()
# User asks about estimates → Main agent uses route_to_estimate_specialist()
# User asks about scheduling → Main agent uses route_to_scheduling_specialist()
```

## Configuration

The agents use the `LiveKitConfig` class for configuration, which loads settings from environment variables in the `/environments` folder.

## Development

### Adding New Specialist Agents

1. Create a new specialist agent in the `specialists/` directory
2. Inherit from `Agent` and use `@function_tool` decorators
3. Add the agent to `_initialize_specialist_agents()` in `Hero365MainAgent`
4. Add a routing tool in the main agent
5. Update the main agent's instructions to mention the new specialist

### Adding New Tools

1. Add the tool to the appropriate specialist agent using `@function_tool`
2. Implement the tool logic or integrate with `Hero365ToolsWrapper`
3. Add proper error handling and logging
4. Update the agent's instructions to mention the new tool

### Business Context Integration

All specialist agents receive business context through the `set_business_context()` method, allowing them to provide context-aware responses and suggestions.

## Troubleshooting

### Common Issues

1. **Agent not routing properly**: Check that the routing tools are properly defined in the main agent
2. **Tools not working**: Verify that the `Hero365ToolsWrapper` is properly initialized
3. **Context not available**: Ensure business context is properly loaded and passed to agents

### Debugging

Enable debug logging to see detailed information about agent routing and tool execution:

```bash
uv run python -m app.livekit_agents.worker dev --log-level debug
```

## Future Enhancements

- **Dynamic Agent Loading**: Load specialist agents on-demand based on usage patterns
- **Conversation Memory**: Maintain conversation context across agent handoffs
- **Advanced Routing**: Use AI to determine the best specialist for complex requests
- **Agent Collaboration**: Allow specialists to collaborate on multi-domain requests 