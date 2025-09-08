from agents import Agent
import os
import asyncio
try:
    from agents import HostedMCPTool  # type: ignore
except Exception:  # pragma: no cover
    from agents.tools import HostedMCPTool  # type: ignore

try:
    # Prefer direct import path for MCP servers
    from agents.mcp.server import MCPServerStdio, MCPServerStreamableHttp  # type: ignore
except Exception:  # pragma: no cover
    # Fallback older layout
    from agents.mcp import MCPServerStdio, MCPServerStreamableHttp  # type: ignore

from tools.agent_tools import run_research_summarizer, run_script_drafter
from app.research_summarizer_agent import make_research_summarizer
from app.script_drafter_agent import make_script_drafter

def make_orchestrator() -> Agent:
    """
    Construct the Orchestrator Agent.

    Central coordinator for The Black Street Journal pipeline. 
    It assigns work, enforces guardrails, manages handoffs between specialist agents (research, drafting, QC),
    and updates Notion so the whole flow stays observable and recoverable.

    """
    # Function tools available to the Orchestrator
    tools_list = [
        run_research_summarizer,
        run_script_drafter,
    ]

    # Configure Notion MCP server(s); preflight connect to avoid runtime init errors
    mcp_servers = []

    notion_token = os.getenv("NOTION_TOKEN")
    if notion_token:
        # STDIO transport (local subprocess) using @notionhq/notion-mcp-server
        stdio_server = MCPServerStdio(
            params={
                "command": "npx",
                "args": ["-y", "@notionhq/notion-mcp-server"],
                "env": {"NOTION_TOKEN": notion_token},
            },
            name="notion-stdio",
            cache_tools_list=True,
        )
        try:
            asyncio.get_event_loop().run_until_complete(stdio_server.connect())
            print("\n[Notion MCP] Connected via stdio (npx @notionhq/notion-mcp-server)\n")
            mcp_servers.append(stdio_server)
        except Exception as e:
            print(f"\n[Notion MCP stdio] Preflight connect failed: {e}. Continuing without stdio server.\n")

    # Optional: allow hosted/HTTP transport if explicitly configured
    notion_mcp_url = os.getenv("NOTION_MCP_URL")
    notion_auth = os.getenv("NOTION_MCP_AUTH_TOKEN")
    if notion_mcp_url:
        # If user insists on hosted tool style, also expose HostedMCPTool; otherwise prefer MCPServerStreamableHttp
        if os.getenv("NOTION_MCP_USE_HOSTED_TOOL") == "1":
            tools_list.append(
                HostedMCPTool(
                    tool_config={
                        "type": "mcp",
                        "server_label": "notion",
                        "server_url": notion_mcp_url,
                        "require_approval": "never",
                    }
                )
            )
        else:
            http_server = MCPServerStreamableHttp(
                params={
                    "url": notion_mcp_url,
                    # Header-style auth if provided by the server
                    "headers": {"Authorization": f"Bearer {notion_auth}"} if notion_auth else {},
                },
                name="notion-http",
                cache_tools_list=True,
            )
            try:
                asyncio.get_event_loop().run_until_complete(http_server.connect())
                print(f"\n[Notion MCP] Connected via HTTP at {notion_mcp_url}\n")
                mcp_servers.append(http_server)
            except Exception as e:
                print(f"\n[Notion MCP http] Preflight connect failed: {e}. Continuing without http server.")

    return Agent(
        name="Orchestrator",
        instructions="""
        You are the Orchestrator for The Black Street Journal's research-to-script pipeline.

        When given a research task, you should:
        1. Parse the task requirements (topic, geo_focus, time_window, must_hits, red_lines)
        2. Transfer to the Research Summarizer agent to gather sources and create a research brief
        3. Once research is complete, transfer to the Script Drafter agent to create the final script
        4. Coordinate the entire process and provide final summary

        Use the transfer_to_research_summarizer and transfer_to_script_drafter functions to hand off work to specialist agents.
        Always transfer with clear, structured instructions including all necessary context.
        """,
        tools=tools_list,
        mcp_servers=mcp_servers,
        handoffs=[make_research_summarizer, make_script_drafter],
    )
