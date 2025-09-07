import os
from agents import Agent, Runner
from dotenv import load_dotenv


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

    agent = Agent(name="Assistant", instructions="You are a helpful assistant")
    result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
    print(result.final_output)


if __name__ == "__main__":
    main()
