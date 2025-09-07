from agents import Agent
import os
try:
    from agents import HostedMCPTool  # type: ignore
except Exception:  # pragma: no cover
    from agents.tools import HostedMCPTool  # type: ignore

from tools.agent_tools import run_research_summarizer, run_script_drafter

def make_orchestrator() -> Agent:
    """
    Construct the Orchestrator Agent.

    Central coordinator for The Black Street Journal pipeline. 
    It assigns work, enforces guardrails, manages handoffs between specialist agents (research, drafting, QC),
    and updates Notion so the whole flow stays observable and recoverable.

    """
    # Conditionally expose Notion Hosted MCP if configured
    tools_list = [
        run_research_summarizer,
        run_script_drafter,
    ]

    notion_mcp_url = os.getenv("NOTION_MCP_URL")
    if notion_mcp_url:
        tools_list.append(
            HostedMCPTool(
                tool_config={
                    "type": "mcp",
                    "server_label": "notion",
                    "server_url": notion_mcp_url,
                    # set to "never" for initial automation; tighten later
                    "require_approval": "never",
                }
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
        # handoffs=[],  # Wire specialist agents here in future iterations
    )
