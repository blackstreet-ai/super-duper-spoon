---
description: Create and bootstrap a new Python project using the OpenAI Agents SDK with a runnable "hello agent", venv, and basic repo hygiene—requiring Python 3.11+
---

# Initialize Agents SDK Project

This workflow creates and bootstraps a new Python project using the OpenAI Agents SDK with all necessary components.

## Prerequisites
- Python 3.11+ installed
- Git installed
- Node.js installed (for MCP servers)

## Steps

1. **Validate Python version**
```bash
python --version
```
Abort if Python version is less than 3.11.

2. **Create project directory**
// turbo
```bash
mkdir new-agents-project
cd new-agents-project
```

3. **Initialize git repository**
// turbo
```bash
git init
```

4. **Create virtual environment**
// turbo
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\Activate.ps1  # Windows PowerShell
```

5. **Create pyproject.toml**
```toml
[project]
name = "agents-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "openai-agents",
    "python-dotenv"
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

6. **Install dependencies**
// turbo
```bash
pip install --upgrade pip
pip install openai-agents python-dotenv
```

7. **Create project structure**
// turbo
```bash
mkdir -p src/app src/tools src/workflows tests .windsurf/workflows
touch src/__init__.py src/app/__init__.py src/tools/__init__.py
```

8. **Create .env.example**
```env
OPENAI_API_KEY=YOUR-OPENAI-PROJECT-KEY
EXA_API_KEY=YOUR-EXA-API-KEY
NOTION_TOKEN=ntn_your_integration_secret_here
NOTION_MCP_URL=http://localhost:3001/mcp
NOTION_MCP_AUTH_TOKEN=dev-secret
```

9. **Create .gitignore**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# Environment variables
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Artifacts
artifacts/
```

10. **Create hello agent**
Create `src/app/hello_agent.py`:
```python
from agents import Agent

def make_hello_agent() -> Agent:
    """
    Simple hello world agent for testing.
    """
    return Agent(
        name="Hello Agent",
        instructions="You are a friendly assistant. When asked to say hello, respond with a creative greeting.",
        tools=[],
        handoffs=[],
    )
```

11. **Create main.py**
Create `src/main.py`:
```python
import os
from agents import Agent, Runner, RunConfig
from dotenv import load_dotenv
from app.hello_agent import make_hello_agent

def main() -> None:
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is not set. Please check your .env file.")
        return
    
    agent = make_hello_agent()
    result = Runner.run_sync(
        agent,
        "Say hello and introduce yourself!",
        run_config=RunConfig(workflow_name="Hello World"),
    )
    print("\n" + result.final_output + "\n")

if __name__ == "__main__":
    main()
```

12. **Create README.md**
```markdown
# Agents Project

A project using the OpenAI Agents SDK with Python 3.11+.

## Setup

1. Copy `.env.example` to `.env` and set your API keys
2. Activate virtual environment: `source .venv/bin/activate`
3. Run: `python src/main.py`

## Requirements
- Python 3.11+
- OpenAI API key
```

13. **Test the setup**
// turbo
```bash
cp .env.example .env
echo "Please edit .env to add your OPENAI_API_KEY"
python src/main.py
```

## Success Criteria
- ✅ Python 3.11+ validated
- ✅ Virtual environment created and activated
- ✅ Dependencies installed
- ✅ Project structure created
- ✅ Hello agent runs successfully
- ✅ Git repository initialized
- ✅ Proper .gitignore and .env.example in place
