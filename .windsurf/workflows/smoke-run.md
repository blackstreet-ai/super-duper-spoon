---
description: Run comprehensive smoke tests for all agents and MCP connections
---

# Smoke Run Workflow

This workflow runs comprehensive smoke tests to validate all agents and MCP connections are working properly.

## Prerequisites
- Python 3.11+ environment
- Virtual environment activated
- Required API keys set in .env file

## Steps

1. **Validate Python version**
// turbo
```bash
python --version
```

2. **Activate virtual environment**
// turbo
```bash
source .venv/bin/activate
```

3. **Check environment variables**
// turbo
```bash
echo "Checking required environment variables..."
if [ -z "$OPENAI_API_KEY" ]; then echo "❌ OPENAI_API_KEY not set"; else echo "✅ OPENAI_API_KEY set"; fi
if [ -z "$EXA_API_KEY" ]; then echo "⚠️  EXA_API_KEY not set (optional)"; else echo "✅ EXA_API_KEY set"; fi
if [ -z "$NOTION_TOKEN" ]; then echo "⚠️  NOTION_TOKEN not set (optional)"; else echo "✅ NOTION_TOKEN set"; fi
```

4. **Run basic orchestrator test**
// turbo
```bash
echo "Running basic orchestrator test..."
.venv/bin/python src/main.py
```

5. **Run research smoke test**
// turbo
```bash
echo "Running research smoke test..."
RESEARCH_SMOKE=1 .venv/bin/python src/main.py
```

6. **Run Notion smoke test**
// turbo
```bash
echo "Running Notion MCP smoke test..."
NOTION_SMOKE=1 .venv/bin/python src/main.py
```

7. **Run end-to-end pipeline test**
// turbo
```bash
echo "Running end-to-end pipeline test..."
E2E_TEST=1 .venv/bin/python src/main.py
```

8. **Check artifacts directory**
// turbo
```bash
echo "Checking generated artifacts..."
ls -la artifacts/
if [ -d "artifacts/research" ]; then
    echo "✅ Research artifacts directory exists"
    ls -la artifacts/research/
else
    echo "❌ No research artifacts found"
fi
```

9. **Validate guardrails**
// turbo
```bash
echo "Testing guardrails validation..."
python -c "
from src.tools.guardrails import validate_task_input, format_validation_report
result = validate_task_input({'topic': 'Test Topic'})
print(format_validation_report(result, 'Test'))
"
```

## Success Criteria
- ✅ All smoke tests complete without errors
- ✅ Artifacts are generated in artifacts/ directory
- ✅ MCP connections establish successfully
- ✅ Guardrails validation functions work
- ✅ Agents produce expected output formats

## Troubleshooting
- If OPENAI_API_KEY errors: Check .env file and API key validity
- If MCP connection fails: Verify Node.js installed and tokens are correct
- If import errors: Ensure virtual environment is activated and dependencies installed
