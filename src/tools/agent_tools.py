from typing import List, Optional

from agents import Runner, function_tool
from app.research_summarizer_agent import make_research_summarizer
from app.script_drafter_agent import make_script_drafter

@function_tool
def run_research_summarizer(
    topic: str,
    geo_focus: Optional[str] = None,
    time_window: Optional[str] = None,
    must_hits: Optional[List[str]] = None,
    red_lines: Optional[List[str]] = None,
) -> str:
    """
    Run the Research Summarizer agent to produce a sources-backed research brief.

    Args:
        topic: The topic or question to research.
        geo_focus: Geographic focus (e.g., "US", "NYC", "Sub-Saharan Africa").
        time_window: Absolute range (e.g., "2023-01-01 to 2025-09-06").
        must_hits: Key points that MUST be addressed in findings.
        red_lines: Prohibitions or constraints the output must respect.

    Returns:
        The Research Summarizer's final output as a formatted string, including
        a Sources Register, Key Findings with [S#] citations, Must-Hits Coverage,
        and Gaps or Risks.
    """
    agent = make_research_summarizer()

    # Construct a concise, structured prompt for the agent
    parts = [
        f"Topic: {topic}",
    ]
    if geo_focus:
        parts.append(f"Geo Focus: {geo_focus}")
    if time_window:
        parts.append(f"Time Window: {time_window}")
    if must_hits:
        parts.append("Must-Hits:\n- " + "\n- ".join(must_hits))
    if red_lines:
        parts.append("Red Lines:\n- " + "\n- ".join(red_lines))

    prompt = "\n\n".join(parts)

    result = Runner.run_sync(agent, prompt)
    return result.final_output

@function_tool
def run_script_drafter(
    topic: str,
    audience: Optional[str] = None,
    tone: Optional[str] = None,
    red_lines: Optional[List[str]] = None,
    research_brief: Optional[str] = None,
) -> str:
    """
    Run the Script Drafter agent to produce an outline and draft script.

    Args:
        topic: The topic of the script.
        audience: Target audience (e.g., "general news viewers", "policymakers").
        tone: Voice/tone guidance (e.g., "clear, direct, no fluff").
        red_lines: Prohibitions or constraints the output must respect.
        research_brief: The full research brief text from the Research Summarizer,
                        including the Sources Register and Key Findings with [S#].

    Returns:
        The Script Drafter's final output as a formatted string, including Outline,
        Draft Script with [S#] citations, optional Callouts/Graphics, Redlines
        Check, and Handback Notes if any.
    """
    agent = make_script_drafter()

    parts = [
        f"Topic: {topic}",
    ]
    if audience:
        parts.append(f"Audience: {audience}")
    if tone:
        parts.append(f"Tone: {tone}")
    if red_lines:
        parts.append("Red Lines:\n- " + "\n- ".join(red_lines))
    if research_brief:
        parts.append("Research Brief:\n" + research_brief)

    prompt = "\n\n".join(parts)

    result = Runner.run_sync(agent, prompt)
    return result.final_output
