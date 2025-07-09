# Hero365 Voice Agent Workers Usage Guide

This guide explains how to use the different voice agent workers available in the Hero365 system.

## Available Workers

### 1. Standard Worker (`worker.py`)
- **Purpose**: Handles standard voice agent sessions
- **Features**: Direct tool execution, basic voice interactions
- **Use Case**: Simple business management tasks, quick queries
- **Response Style**: Direct, immediate tool execution

### 2. Reasoning Worker (`reasoning_worker.py`)
- **Purpose**: Handles complex reasoning-enabled voice agent sessions
- **Features**: Plan-Act-Verify loop, multi-tool coordination, reasoning transparency
- **Use Case**: Complex multi-step workflows, sophisticated business processes
- **Response Style**: Planned execution with reasoning explanation

## How to Launch Workers

### Option 1: Direct Execution

#### Standard Worker
```bash
cd backend
python -m app.voice_agents.worker
```

#### Reasoning Worker
```bash
cd backend
python -m app.voice_agents.reasoning_worker
```

### Option 2: Using the Launcher (Recommended)

#### Standard Mode
```bash
cd backend
python -m app.voice_agents.launcher --mode standard
```

#### Reasoning Mode
```bash
cd backend
python -m app.voice_agents.launcher --mode reasoning
```

#### Advanced Options
```bash
# Reasoning mode with custom iterations
python -m app.voice_agents.launcher --mode reasoning --max-iterations 5

# With verbose logging
python -m app.voice_agents.launcher --mode reasoning --verbose
```

## Environment Variables

### Required (Both Workers)
```bash
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
OPENAI_API_KEY=your_openai_key
DEEPGRAM_API_KEY=your_deepgram_key
CARTESIA_API_KEY=your_cartesia_key
```

### Optional (Reasoning Worker Only)
```bash
MAX_REASONING_ITERATIONS=3  # Default: 3
```

## Worker Comparison

| Feature | Standard Worker | Reasoning Worker |
|---------|-----------------|------------------|
| **Execution Style** | Direct tool calls | Plan-Act-Verify loop |
| **Complex Workflows** | Requires multiple interactions | Single interaction |
| **Reasoning Transparency** | No | Yes |
| **Plan Revision** | No | Yes |
| **Multi-tool Coordination** | Limited | Advanced |
| **Performance** | Fast | Moderate (due to planning) |
| **Use Case** | Simple tasks | Complex workflows |

## Example Use Cases

### Standard Worker
- "Get my upcoming jobs"
- "Create a new project"
- "Check inventory levels"
- "Update job status"

### Reasoning Worker
- "Create a project for the Johnson kitchen renovation, add electrical and plumbing jobs, and send estimates to the client"
- "Find all overdue invoices and create follow-up tasks for each client"
- "Check inventory levels, identify low stock items, and create purchase orders"
- "Schedule all pending jobs for next week based on technician availability"

## Room Metadata Configuration

### Standard Worker
```json
{
  "business_context": {
    "name": "Smith's Home Services",
    "services": ["plumbing", "electrical"]
  },
  "user_context": {
    "name": "John Smith",
    "safety_mode": true
  },
  "agent_config": {
    "temperature": 0.7,
    "max_conversation_duration": 1800
  }
}
```

### Reasoning Worker
```json
{
  "business_context": {
    "name": "Smith's Home Services",
    "services": ["plumbing", "electrical", "HVAC"],
    "capabilities": ["reasoning", "planning", "multi-tool_coordination"]
  },
  "user_context": {
    "name": "John Smith",
    "safety_mode": true,
    "reasoning_preferences": {
      "explain_reasoning": true,
      "show_plan": true,
      "confirm_complex_actions": true
    }
  },
  "max_reasoning_iterations": 3
}
```

## Voice Commands

### Standard Worker Commands
- Simple, direct commands
- One task per interaction
- Immediate execution

### Reasoning Worker Commands
- Complex, multi-step commands
- Natural language workflows
- Reasoning transparency commands:
  - "Explain your reasoning"
  - "What tools are you planning to use?"
  - "Revise the current plan"

## Choosing the Right Worker

### Use Standard Worker When:
- You need fast, direct responses
- Tasks are simple and single-step
- You prefer immediate tool execution
- You're doing quick queries or updates

### Use Reasoning Worker When:
- You have complex, multi-step workflows
- You need transparency in the process
- You want to handle multiple related tasks at once
- You need plan revision capabilities

## Production Deployment

### Standard Worker
```bash
# Production deployment
python -m app.voice_agents.worker
```

### Reasoning Worker
```bash
# Production deployment with optimized settings
MAX_REASONING_ITERATIONS=3 python -m app.voice_agents.reasoning_worker
```

## Monitoring and Debugging

### Standard Worker Logs
```
🤖 Hero365 Standard Voice Agent Worker Starting
Features enabled:
  ✅ Voice-based business management
  ✅ Job and project management
  ✅ Invoice and estimate handling
  ✅ Contact and inventory management
  ✅ Direct tool execution
```

### Reasoning Worker Logs
```
🧠 Hero365 Reasoning Voice Agent Worker Starting
Features enabled:
  ✅ Plan-Act-Verify reasoning loop
  ✅ Multi-tool coordination
  ✅ Reasoning transparency
  ✅ Plan revision capabilities
  ✅ Complex workflow handling
```

## Best Practices

1. **Choose the right worker** for your use case
2. **Use the launcher** for easier management
3. **Configure room metadata** appropriately
4. **Monitor logs** for debugging and optimization
5. **Test complex workflows** with reasoning worker first
6. **Use standard worker** for simple, frequent tasks

## Troubleshooting

### Common Issues
1. **Worker not starting**: Check environment variables
2. **Tools not working**: Verify context injection
3. **Reasoning loops**: Check iteration limits
4. **Performance issues**: Consider switching workers

### Debug Mode
```bash
python -m app.voice_agents.launcher --mode reasoning --verbose
```

This will provide detailed logging for troubleshooting complex reasoning workflows. 