import os
from agents import Agent, Runner
from dotenv import load_dotenv
from agents import RunConfig
from app.orchestrator_agent import make_orchestrator


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
