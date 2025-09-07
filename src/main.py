import os
from agents import Agent, Runner
from dotenv import load_dotenv
from agents import RunConfig
from app.orchestrator_agent import make_orchestrator
from tools.agent_tools import run_research_summarizer


def research_smoke() -> None:
    """
    Quick smoke run to exercise the Research Summarizer tool chain (Exa MCP).
    Prints the beginning of the Sources Register if present; otherwise prints the
    first few lines of the agent output. Use by setting RESEARCH_SMOKE=1.
    """
    topic = "US labor market cooling signals in 2025"
    time_window = "2024-01-01 to 2025-09-07"
    print("[Smoke] Running Research Summarizer...\n")
    output = run_research_summarizer(topic=topic, time_window=time_window)

    # Try to locate the Sources Register section and print first ~10 entries/lines
    print("\n===== Research Summarizer Output (truncated) =====\n")
    lower = output.lower()
    idx = lower.find("sources register")
    snippet = output
    if idx != -1:
        snippet = output[idx:]
    lines = snippet.splitlines()
    # Print up to 30 lines to show early sources and structure
    preview = "\n".join(lines[:30])
    print(preview)
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

    # Use the Orchestrator Agent for the demo run
    agent = make_orchestrator()
    result = Runner.run_sync(
        agent,
        "Write a haiku about recursion in programming.",
        run_config=RunConfig(workflow_name="Orchestrator Hello"),
    )
    print("\n\n" + result.final_output + "\n\n")


if __name__ == "__main__":
    main()
