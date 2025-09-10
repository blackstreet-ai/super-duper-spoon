from typing import List, Optional

from agents import Runner, function_tool, RunConfig
from app.research_summarizer_agent import make_research_summarizer
from app.script_drafter_agent import make_script_drafter
from pathlib import Path
from tools.guardrails import (
    validate_task_input, 
    validate_research_output, 
    validate_script_output,
    format_validation_report,
    TaskRequirements
)

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
    # Input validation
    task_data = {
        "topic": topic,
        "geo_focus": geo_focus,
        "time_window": time_window,
        "must_hits": must_hits,
        "red_lines": red_lines
    }
    
    input_validation = validate_task_input(task_data)
    if not input_validation.is_valid:
        return f"INPUT VALIDATION FAILED:\n{format_validation_report(input_validation, 'Research Input')}"
    
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
    output = result.final_output
    
    # Output validation
    requirements = TaskRequirements(
        topic=topic,
        geo_focus=geo_focus,
        time_window=time_window,
        must_hits=must_hits,
        red_lines=red_lines
    )
    
    output_validation = validate_research_output(output, requirements)
    validation_report = format_validation_report(output_validation, "Research Output")
    
    return f"{output}\n\n{validation_report}"

@function_tool
def save_markdown(path: str, contents: str, overwrite: bool = False) -> str:
    """
    Save Markdown contents to the given file path, creating parent directories as needed.

    Args:
        path: Relative or absolute file path. If it doesn't end with `.md`, the extension will be added.
        contents: Markdown text to write.
        overwrite: When False (default), raises an error if the file already exists.

    Returns:
        The absolute path to the written Markdown file as a string.
    """
    target = Path(path)
    if target.suffix.lower() != ".md":
        target = target.with_suffix(".md")

    target = target.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and not overwrite:
        raise FileExistsError(f"File already exists: {target}")

    target.write_text(contents, encoding="utf-8")
    return str(target)

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
    # Input validation
    task_data = {
        "topic": topic,
        "red_lines": red_lines
    }
    
    input_validation = validate_task_input(task_data)
    if not input_validation.is_valid:
        return f"INPUT VALIDATION FAILED:\n{format_validation_report(input_validation, 'Script Input')}"
    
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
    output = result.final_output
    
    # Output validation
    requirements = TaskRequirements(
        topic=topic,
        red_lines=red_lines
    )
    
    output_validation = validate_script_output(output, requirements)
    validation_report = format_validation_report(output_validation, "Script Output")
    
    return f"{output}\n\n{validation_report}"
