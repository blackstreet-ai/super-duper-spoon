import os
from agents import Agent, Runner
from dotenv import load_dotenv
from agents import RunConfig
from app.orchestrator_agent import make_orchestrator
from app.research_summarizer_agent import make_research_summarizer
from datetime import datetime


def research_smoke() -> None:
    """
    Quick smoke run to exercise the Research Summarizer tool chain (Exa MCP).
    Prints the beginning of the Sources Register if present; otherwise prints the
    first few lines of the agent output. Use by setting RESEARCH_SMOKE=1.
    """
    topic = "Impact of Grocery Price Inflation on Consumer Spending"
    time_window = "2024-01-01 to 2025-09-07"
    print("[Smoke] Running Research Summarizer...\n")
    # Create a deterministic artifact filename under artifacts/
    slug = (
        topic.lower()
        .replace(" ", "_")
        .replace("/", "-")
        .replace("\\", "-")
    )
    today = datetime.now().strftime("%Y-%m-%d")
    artifact_path = f"artifacts/research/sources_{slug}_{today}.md"

    parts = [
        f"Topic: {topic}",
        f"Time Window: {time_window}",
        (
            "Task: Use your hosted MCP tools (web_search_exa, crawling) to find at least 2 "
            "recent credible sources and list a 'Sources Register' section with numbered "
            "entries in the format: Title - Outlet/Author - Date (YYYY-MM-DD) - URL - 1-liner relevance."
        ),
        "Be concise and ensure publish dates are included.",
        (
            "After you generate the 'Sources Register' section, call the save_markdown tool "
            f"to write ONLY that section to the file path: {artifact_path}. Use overwrite=true."
        ),
    ]
    prompt = "\n\n".join(parts)
    agent = make_research_summarizer()
    result = Runner.run_sync(agent, prompt, run_config=RunConfig(workflow_name="Research Smoke"))
    output = result.final_output

    # Try to locate the Sources Register section and print first ~10 entries/lines
    print("\n===== Research Summarizer Output (truncated) =====\n")
    lower = output.lower()
    idx = lower.find("sources register")
    snippet = output
    if idx != -1:
        snippet = output[idx:]
    lines = snippet.splitlines()
    # Print up to 80 lines to show early sources and structure
    preview = "\n".join(lines[:80])
    print(preview)
    print("\n===== End Preview =====\n")


def notion_smoke() -> None:
    """
    Quick smoke to verify Notion MCP (stdio) connectivity by asking for a read-only
    action (list users) and printing a small excerpt. Use by setting NOTION_SMOKE=1.
    """
    print("[Smoke] Verifying Notion MCP (stdio) connectivity...\n")
    # If NOTION_MCP_URL is provided, explicitly connect to the HTTP MCP server to avoid
    # 'Server not initialized' errors, then construct a temporary Agent for the smoke.
    notion_url = os.getenv("NOTION_MCP_URL")
    notion_auth = os.getenv("NOTION_MCP_AUTH_TOKEN")
    agent: Agent
    if notion_url:
        try:
            # Lazy import to keep main path lightweight
            try:
                from agents.mcp.server import MCPServerStreamableHttp  # type: ignore
            except Exception:
                from agents.mcp import MCPServerStreamableHttp  # type: ignore

            server = MCPServerStreamableHttp(
                params={
                    "url": notion_url,
                    "headers": {"Authorization": f"Bearer {notion_auth}"} if notion_auth else {},
                },
                name="notion-http-smoke",
                cache_tools_list=True,
            )

            # Connect before running
            import asyncio

            asyncio.get_event_loop().run_until_complete(server.connect())

            agent = Agent(
                name="Notion Smoke",
                instructions=(
                    "Use the Notion tools to list users (read-only). Return up to 5 users "
                    "with: name, id, type. If Notion is not configured, say so explicitly."
                ),
                mcp_servers=[server],
            )
        except Exception as e:
            print(f"\n[Smoke] Failed to prepare HTTP Notion MCP server: {e}\n")
            agent = make_orchestrator()
    else:
        agent = make_orchestrator()
    prompt = (
        "Use your Notion tools to list users (read-only). "
        "Return up to 5 users with: name, id, type. "
        "If Notion is not configured, say so explicitly."
    )
    result = Runner.run_sync(agent, prompt, run_config=RunConfig(workflow_name="Notion Smoke"))
    output = result.final_output
    print("\n===== Notion MCP Output (truncated) =====\n")
    lines = output.splitlines()
    print("\n".join(lines[:80]))
    print("\n===== End Preview =====\n")


def main() -> None:
    # Load environment variables from .env if present
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(
            "OPENAI_API_KEY is not set.\n"
            "- Copy .env.example to .env\n"
            "- Set OPENAI_API_KEY=sk-... in .env, then re-run: .venv/bin/python src/main.py"
        )
        return

    # Research smoke mode: set RESEARCH_SMOKE=1 to run the research tool directly
    if os.getenv("RESEARCH_SMOKE") == "1":
        research_smoke()
        return

    # Notion smoke mode: set NOTION_SMOKE=1 to test Notion MCP connectivity (read-only)
    if os.getenv("NOTION_SMOKE") == "1":
        notion_smoke()
        return

    # Use the Orchestrator Agent for the demo run
    agent = make_orchestrator()
    result = Runner.run_sync(
        agent,
        "Write a haiku about recursion in programming.",
        run_config=RunConfig(workflow_name="Orchestrator Hello"),
    )
    print("\n" + result.final_output + "\n")


if __name__ == "__main__":
    main()
