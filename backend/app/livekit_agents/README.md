# Hero365 LiveKit Agents

This directory contains the LiveKit agents implementation for Hero365, following the latest LiveKit 1.0 patterns and best practices.

## Architecture

The implementation follows a simplified, modular approach:

### Main Agent
- **`worker.py`** - Contains the main `Hero365VoiceAgent` class that handles voice interactions with business context awareness

### Specialist Agents
- **`specialists/contact_agent.py`** - Contact management specialist
- **`specialists/job_agent.py`** - Job management specialist  
- **`specialists/estimate_agent.py`** - Estimate management specialist
- **`specialists/scheduling_agent.py`** - Scheduling and calendar management specialist

### Support Agents
- **`hero365_triage_agent.py`** - General inquiry and triage agent

## Key Features

### Simplified Tool Registration
All agents use the `@function_tool` decorator for tool registration, avoiding the duplicate function name issues that can occur with list-based tool registration.

### Business Context Integration
All agents can be initialized with business context through the `BusinessContextManager`, providing context-aware responses.

### Consistent Error Handling
All tools follow a consistent error handling pattern with proper logging and user-friendly error messages.

## Usage

### Running the Worker
```bash
cd backend
uv run python -m app.livekit_agents.worker dev --log-level debug
```

### Creating Agents
```python
from app.livekit_agents.worker import Hero365VoiceAgent
from app.livekit_agents.specialists.contact_agent import ContactAgent
from app.livekit_agents.config import LiveKitConfig

# Main voice agent
agent = Hero365VoiceAgent()

# Specialist agents
config = LiveKitConfig()
contact_agent = ContactAgent(config)
```

## Configuration

The agents use the `LiveKitConfig` class for configuration, which loads settings from environment variables in the `/environments` folder.

## Development

### Adding New Tools
1. Add the tool method to the appropriate agent class
2. Use the `@function_tool` decorator
3. Include proper error handling and logging
4. Update the agent's instructions to reference the new tool

### Adding New Agents
1. Create a new agent class inheriting from `Agent`
2. Initialize with instructions only (no tools list)
3. Add tools using `@function_tool` decorators
4. Include proper business context integration

## Troubleshooting

### Duplicate Function Name Errors
If you encounter duplicate function name errors:
1. Ensure tools are registered using `@function_tool` decorators only
2. Don't pass tools as a list in the `__init__` method
3. Check that function names are unique across all agents

### Business Context Issues
If business context is not loading:
1. Check that user_id and business_id are properly set in room metadata
2. Verify the dependency injection container is properly configured
3. Check the business context manager logs for errors 