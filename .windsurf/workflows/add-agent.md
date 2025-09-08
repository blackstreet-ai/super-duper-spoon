---
description: Create a new agent file with template structure
---

# Add Agent Workflow

This workflow creates a new agent file with the proper template structure for The Black Street Journal project.

## Prerequisites
- Python 3.11+ environment
- OpenAI Agents SDK installed
- Project structure in place

## Steps

1. **Validate Python version**
```bash
python --version
```
Ensure Python 3.11 or higher is installed.

2. **Create agent file**
Create a new file in `src/app/` with the agent name (e.g., `fact_checker_agent.py`).

3. **Add agent template**
```python
from agents import Agent
from tools.file_tools import save_markdown

def make_[agent_name]() -> Agent:
    """
    Construct the [Agent Name] Agent.
    
    Purpose:
    - [Describe the agent's primary responsibility]
    
    Inputs:
    - [List expected inputs from orchestrator/other agents]
    
    Outputs:
    - [Describe expected outputs and deliverables]
    
    Guardrails:
    - [List compliance requirements and constraints]
    """
    return Agent(
        name="[Agent Name]",
        instructions="""
        You are the [Agent Name] for The Black Street Journal.
        
        [Detailed instructions for the agent's behavior and responsibilities]
        """,
        tools=[save_markdown],  # Add relevant tools
        handoffs=[],  # Add handoff targets if needed
    )
```

4. **Update orchestrator imports**
Add import to `src/app/orchestrator_agent.py`:
```python
from app.[agent_name]_agent import make_[agent_name]
```

5. **Add to handoffs**
Update orchestrator handoffs list:
```python
handoffs=[make_research_summarizer, make_script_drafter, make_[agent_name]],
```

6. **Create agent tool function**
Add function tool in `src/tools/agent_tools.py`:
```python
@function_tool
def run_[agent_name](
    # Add relevant parameters
) -> str:
    """
    Run the [Agent Name] agent.
    """
    # Add input validation
    # Run agent
    # Add output validation
    # Return result with validation report
```

7. **Test the agent**
```bash
# Add test case to main.py or create smoke test
.venv/bin/python src/main.py
```

## Next Steps
- Update README.md with new agent description
- Add agent to workflow documentation
- Create specific smoke test for the agent
