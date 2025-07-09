# Hero365 Reasoning Voice Agent Guide

## Overview

The Hero365 Reasoning Voice Agent extends the standard Personal Voice Agent with advanced reasoning capabilities, implementing a **Plan-Act-Verify** loop for complex multi-tool workflows. This enables the agent to handle sophisticated business management tasks through a single voice interaction.

## Key Features

### 🧠 Plan-Act-Verify Loop
- **PLAN**: Analyzes user requests and creates detailed execution plans
- **ACT**: Executes the plan using appropriate tools in the correct sequence
- **VERIFY**: Checks if goals were achieved and revises plans if needed

### 🔄 Multi-Tool Coordination
- **Sequential execution**: Tools run one after another with dependencies
- **Parallel execution**: Independent tools run simultaneously
- **Dependency management**: Ensures proper data flow between tools
- **Error handling**: Graceful failure recovery with plan revision

### 🎯 Reasoning Transparency
- **Explain reasoning**: Users can ask to see the thought process
- **Plan visibility**: Shows what tools will be used and why
- **Progress tracking**: Real-time updates during complex workflows
- **Confidence scoring**: Provides confidence levels for results

## Architecture

### Core Components

#### 1. ReasoningVoiceAgent (Base Class)
```python
from app.voice_agents.core.reasoning_agent import ReasoningVoiceAgent
```
- Implements the Plan-Act-Verify loop
- Manages execution plans and tool coordination
- Provides reasoning transparency features
- Handles plan revision and adaptation

#### 2. ReasoningPersonalVoiceAgent (Implementation)
```python
from app.voice_agents.personal.reasoning_personal_agent import ReasoningPersonalVoiceAgent
```
- Extends ReasoningVoiceAgent for personal use cases
- Integrates with all existing Hero365 tools
- Provides business-specific reasoning capabilities
- Maintains compatibility with existing workflows

#### 3. Action Types
- **DIRECT_RESPONSE**: Simple responses without tools
- **SINGLE_TOOL**: Single tool execution
- **MULTI_TOOL_SEQUENCE**: Tools executed in sequence
- **MULTI_TOOL_PARALLEL**: Tools executed in parallel

#### 4. Execution Status
- **PENDING**: Not yet started
- **IN_PROGRESS**: Currently executing
- **COMPLETED**: Successfully finished
- **FAILED**: Execution failed
- **NEEDS_REVISION**: Plan needs to be revised

## Usage

### Environment Configuration

Enable reasoning in your environment:

```bash
# Enable reasoning capabilities
ENABLE_REASONING=true

# Set maximum reasoning iterations (default: 3)
MAX_REASONING_ITERATIONS=3
```

### Room Metadata Configuration

For LiveKit integration, configure via room metadata:

```json
{
  "business_context": {
    "name": "Smith's Home Services",
    "services": ["plumbing", "electrical", "HVAC"]
  },
  "user_context": {
    "name": "John Smith",
    "safety_mode": true
  },
  "enable_reasoning": true,
  "max_reasoning_iterations": 3
}
```

### Code Integration

```python
# Create reasoning agent
reasoning_agent = ReasoningPersonalVoiceAgent(
    business_context=business_context,
    user_context=user_context,
    config=DEFAULT_PERSONAL_CONFIG,
    max_reasoning_iterations=3
)

# Use in LiveKit worker
agent = Hero365Agent(
    business_context=business_context,
    user_context=user_context,
    agent_config=agent_config,
    enable_reasoning=True,
    max_reasoning_iterations=3
)
```

## Voice Commands

### Standard Operations
All existing voice commands continue to work:
- "Get my upcoming jobs"
- "Create a new project"
- "Check inventory levels"

### Complex Workflows
The reasoning agent excels at complex requests:
- "Create a project for the Johnson kitchen renovation, add electrical and plumbing jobs, and send estimates to the client"
- "Find all overdue invoices and create follow-up tasks for each client"
- "Check inventory levels and handle any low stock items"

### Reasoning Transparency
- "Explain your reasoning"
- "Why did you choose that approach?"
- "What tools are you planning to use?"
- "Revise the current plan"

## Example Scenarios

### 1. Complex Project Creation

**User Request**: "Create a project for the Johnson kitchen renovation, add electrical and plumbing jobs, and send estimates to the client"

**Reasoning Process**:
1. **PLAN**: Create project → Add jobs → Generate estimates
2. **ACT**: Execute tools in sequence with dependencies
3. **VERIFY**: Confirm all steps completed successfully

**Standard Agent**: Would require 4-5 separate interactions
**Reasoning Agent**: Handles in single interaction with full transparency

### 2. Overdue Invoice Management

**User Request**: "Find all overdue invoices and create follow-up tasks"

**Reasoning Process**:
1. **PLAN**: Get overdue invoices → Get contact details → Create follow-up tasks
2. **ACT**: Sequential execution with data passing
3. **VERIFY**: Confirm all clients have follow-up tasks

**Result**: Complete workflow with actionable follow-up plan

### 3. Inventory Management

**User Request**: "Check inventory and handle low stock items"

**Reasoning Process**:
1. **PLAN**: Check stock → Get reorder suggestions → Create purchase orders
2. **ACT**: Sequential execution with user confirmation
3. **VERIFY**: Confirm all low stock items addressed

**Adaptation**: Can revise plan based on user feedback

## Available Tools

The reasoning agent has access to all existing tools:

### Job Management
- `create_job`, `get_upcoming_jobs`, `update_job_status`
- `schedule_job`, `get_job_details`, `search_jobs`

### Project Management
- `create_project`, `get_active_projects`, `update_project_status`
- `get_project_details`, `search_projects`

### Invoice Management
- `create_invoice`, `get_unpaid_invoices`, `get_overdue_invoices`
- `process_payment`, `get_invoice_details`, `search_invoices`

### Estimate Management
- `create_estimate`, `get_pending_estimates`, `convert_estimate_to_invoice`
- `get_estimate_details`, `update_estimate_status`, `search_estimates`

### Contact Management
- `create_contact`, `search_contacts`, `get_contact_details`
- `update_contact`, `add_contact_interaction`, `get_contact_interactions`

### Inventory Management
- `create_product`, `check_stock_levels`, `adjust_stock`
- `get_reorder_suggestions`, `search_products`, `get_product_details`

## Best Practices

### 1. Natural Language Requests
- Use conversational language for complex requests
- Combine multiple actions in a single sentence
- Be specific about desired outcomes

### 2. Leverage Transparency
- Ask for explanations when learning the system
- Request plan details for complex workflows
- Use revision capabilities to adjust plans

### 3. Error Handling
- The agent will attempt up to 3 reasoning iterations
- Plans automatically revise based on failures
- Fallback to simpler approaches when needed

### 4. Performance Considerations
- Complex reasoning may take longer than simple requests
- Plan verification adds slight overhead
- Multiple tool calls execute efficiently in sequence

## Integration Examples

### Running the Demo
```bash
cd backend
python -m app.voice_agents.examples.reasoning_example
```

### Testing with LiveKit
```bash
# Set environment variables
export ENABLE_REASONING=true
export MAX_REASONING_ITERATIONS=3

# Run the worker
python -m app.voice_agents.worker
```

### Development Setup
```python
# Create test agent
agent = ReasoningPersonalVoiceAgent(
    business_context={"name": "Test Business"},
    user_context={"name": "Test User"},
    max_reasoning_iterations=3
)

# Test complex workflow
result = await agent.execute_reasoning_workflow(
    "Create a project with multiple jobs and estimates"
)
```

## Limitations and Considerations

### Current Limitations
- LLM integration placeholder needs implementation
- Sequential tool execution (parallel execution simplified)
- Maximum 3 reasoning iterations per request
- English language only

### Future Enhancements
- Integration with actual LLM service for planning/verification
- True parallel tool execution with asyncio.gather
- Multi-language support
- Advanced error recovery strategies
- Learning from user feedback

### Performance Impact
- Additional processing time for complex requests
- Memory usage for plan storage and execution history
- Network overhead for multiple tool calls

## Troubleshooting

### Common Issues

1. **Reasoning not enabled**: Check `ENABLE_REASONING` environment variable
2. **Tool execution failures**: Verify tool context injection
3. **Plan revision loops**: Check reasoning iteration limits
4. **Memory issues**: Monitor execution history storage

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Monitoring
- Track reasoning iterations via logs
- Monitor tool execution success rates
- Analyze plan revision patterns
- Review confidence scores

## Conclusion

The Hero365 Reasoning Voice Agent represents a significant advancement in voice-based business management, enabling complex multi-step workflows through natural language interactions. By implementing the Plan-Act-Verify loop, the agent provides transparency, adaptability, and efficiency for sophisticated business operations.

The system maintains backward compatibility with existing tools while adding powerful reasoning capabilities that reduce the need for multiple interactions and improve user productivity in complex business scenarios. 