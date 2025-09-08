# agents-proj-15

A minimal starter project using the OpenAI Agents SDK with Python 3.11+.

## Features

- Exa Hosted MCP wired into the Research Summarizer for real-time web search and crawling
- Save to Markdown tool to persist artifacts under `artifacts/`
- Optional Notion MCP wiring (stdio primary, HTTP optional) from the Orchestrator
- Two smoke runners:
  - `RESEARCH_SMOKE=1` → exercises Exa search/crawling and prints a Sources Register preview
  - `NOTION_SMOKE=1` → exercises Notion MCP (lists users, read-only)

## Prerequisites
- Python 3.11 or newer
- An OpenAI API key available as `OPENAI_API_KEY`
- Node.js + `npx` (for Notion MCP stdio or starting the HTTP server locally)

## Quickstart

1) Create and activate a virtual environment (already created by the workflow under `.venv/`).

2) Install dependencies (already installed by the workflow):
```
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install openai-agents
```

3) Environment setup
- Copy `.env.example` to `.env` and set your real keys as needed:
```
cp .env.example .env
# then edit .env to set minimally:
# OPENAI_API_KEY=sk-...
#
# Optional (Exa Hosted MCP used by Research Summarizer):
# EXA_API_KEY=...
#
# Notion MCP (stdio primary):
# NOTION_TOKEN=ntn_...
#
# Notion MCP (HTTP optional):
# NOTION_MCP_URL=http://localhost:3001/mcp
# NOTION_MCP_AUTH_TOKEN=dev-secret
```

4) Run the hello agent
```
.venv/bin/python src/main.py
```
You should see a haiku printed to your terminal. If you don’t, double-check that your API key is set and that you’re using the project’s `.venv`.

## Smoke runners

- Research smoke (web search + crawl via Exa):
```
RESEARCH_SMOKE=1 .venv/bin/python src/main.py
```
Prints a truncated “Sources Register” and instructs the agent to save it under `artifacts/research/` using the `save_markdown` tool.

- Notion smoke (list users, read-only):
```
NOTION_SMOKE=1 .venv/bin/python src/main.py
```
If you prefer to test via a local HTTP server on port 3001 (e.g., to avoid stdio issues):
```
# Terminal 1: start the official Notion MCP over HTTP (requires Node installed)
NOTION_TOKEN=ntn_... npx @notionhq/notion-mcp-server --transport http --port 3001 --auth-token "dev-notion-mcp-test"

# Terminal 2: point the app to that server
NOTION_TOKEN= \
NOTION_MCP_URL=http://localhost:3001/mcp \
NOTION_MCP_AUTH_TOKEN=dev-notion-mcp-test \
NOTION_SMOKE=1 .venv/bin/python src/main.py
```

## Environment variables

- `OPENAI_API_KEY` (required): OpenAI key for the Agents SDK.
- `EXA_API_KEY` (optional): Exa Hosted MCP key used by the Research Summarizer’s web search/crawling.
- `NOTION_TOKEN` (optional): Notion integration token for stdio mode of the official Notion MCP server.
- `NOTION_MCP_URL` (optional): URL for the Notion MCP over HTTP (e.g., `http://localhost:3001/mcp`).
- `NOTION_MCP_AUTH_TOKEN` (optional): Bearer token the HTTP MCP server expects.

## Project layout
```
src/
  __init__.py
  main.py
  app/
    orchestrator_agent.py
    research_summarizer_agent.py
    script_drafter_agent.py
  tools/
    agent_tools.py
    file_tools.py   # save_markdown tool
```

## How it’s wired

- `src/app/research_summarizer_agent.py`
  - Uses Exa Hosted MCP to search/crawl when `EXA_API_KEY` is set.
  - Exposes `save_markdown` so the agent can persist artifacts under `artifacts/`.

- `src/app/orchestrator_agent.py`
  - Exposes Research and Drafting function tools.
  - Wires Notion MCP servers:
    - Primary: stdio via `npx @notionhq/notion-mcp-server` when `NOTION_TOKEN` is set.
    - Optional: HTTP via `NOTION_MCP_URL` (+ `NOTION_MCP_AUTH_TOKEN`).

## Troubleshooting

- “Server not initialized. Make sure you call `connect()` first.”
  - For stdio: ensure `npx -v` works and `NOTION_TOKEN` is set.
  - For HTTP: ensure the server is running, port is free, and client env includes `NOTION_MCP_URL` and `NOTION_MCP_AUTH_TOKEN`.

- Port conflicts (e.g., 3000/3001 in use)
  - Kill the conflicting process or pick another port via `--port` when starting the HTTP server.

## Using Makefile

You can run everything with one command:
```
make run
```
This will:
- create `.venv` if it doesn't exist
- upgrade `pip`
- install project dependencies
- run the app

To remove the virtual environment (cleanup):
```
make clean
```

## Python version policy
This repository requires Python 3.11+. See `pyproject.toml` for the `requires-python` setting.

