from agents import Agent
import os
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

    # Configure Notion MCP server (prefer stdio using the official makenotion/notion-mcp-server)
    mcp_servers = []

    notion_token = os.getenv("NOTION_TOKEN")
    if notion_token:
        # STDIO transport (local subprocess) using @notionhq/notion-mcp-server
        mcp_servers.append(
            MCPServerStdio(
                params={
                    "command": "npx",
                    "args": ["-y", "@notionhq/notion-mcp-server"],
                    "env": {"NOTION_TOKEN": notion_token},
                },
                name="notion-stdio",
                cache_tools_list=True,
            )
        )

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
            mcp_servers.append(
                MCPServerStreamableHttp(
                    params={
                        "url": notion_mcp_url,
                        # Header-style auth if provided by the server
                        "headers": {"Authorization": f"Bearer {notion_auth}"} if notion_auth else {},
                    },
                    name="notion-http",
                    cache_tools_list=True,
                )
            )

    return Agent(
        name="Orchestrator",
        instructions="""
        1.	Intake & Scope: Read the active task (topic, geo_focus, time_window, must_hits, red_lines). Normalize dates to absolutes and set status: In Progress.
        2.	Plan & Dispatch: Create a brief task plan and delegate to the appropriate specialist agent(s) (e.g., research_summarizer → script_drafter). Pass only the minimum context needed.
        3.	Guardrails & Quality: At each handoff, check sources are dated and cited; reject unverifiable claims; ensure red_lines are not violated; require must_hits coverage.
        4.	Progress Control: If any step stalls or returns <5 credible sources, expand the scope once; otherwise flag Needs Input with a concise note of what's missing.
        5.	Assemble Outputs: Collect artifacts (brief, outline, draft), generate a final package (sources register, outline, draft), and link them in the task record.
        6.	Status & Logging: Update Notion fields (status → Ready for Review, sources_count, last_updated, links). Write an execution log with timestamps and decisions.
        7.	Finalize or Re-route: If guardrails fail, send the item back to the responsible agent with a structured correction note; else mark Done and notify.
        """,
        tools=tools_list,
        mcp_servers=mcp_servers,
        # handoffs=[],  # Wire specialist agents here in future iterations
    )
