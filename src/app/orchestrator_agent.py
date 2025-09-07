from agents import Agent


def make_orchestrator() -> Agent:
    """
    Construct the Orchestrator Agent.

    The Orchestrator's responsibility is to interpret high-level user intents,
    decide on next actions, and (in future) hand off to specialist agents or tools.
    """
    return Agent(
        name="Orchestrator",
        instructions=(
            "You are the Orchestrator. Your job is to understand the user's goal, "
            "plan the next steps, and produce a concise response. Prefer clear, actionable "
            "outputs. If information is missing, ask brief, targeted questions."
        ),
        # tools=[],  # Add tools as they are created in src/tools/
        # handoffs=[],  # Wire specialist agents here in future iterations
    )
