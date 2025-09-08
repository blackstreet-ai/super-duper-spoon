"""
Guardrails and validation functions for The Black Street Journal agents.
Implements input validation, output validation, and compliance checks.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


@dataclass
class TaskRequirements:
    """Structured task requirements for validation."""
    topic: str
    geo_focus: Optional[str] = None
    time_window: Optional[str] = None
    must_hits: Optional[List[str]] = None
    red_lines: Optional[List[str]] = None


def validate_task_input(task_data: Dict[str, Any]) -> ValidationResult:
    """
    Validate input task requirements before processing.
    
    Args:
        task_data: Dictionary containing task parameters
        
    Returns:
        ValidationResult with validation status and any issues
    """
    errors = []
    warnings = []
    
    # Required fields
    if not task_data.get("topic"):
        errors.append("Topic is required")
    
    # Validate time window format if provided
    time_window = task_data.get("time_window")
    if time_window:
        if not re.match(r'\d{4}-\d{2}-\d{2}\s+to\s+\d{4}-\d{2}-\d{2}', time_window):
            warnings.append("Time window should be in format 'YYYY-MM-DD to YYYY-MM-DD'")
    
    # Validate must_hits and red_lines are lists if provided
    must_hits = task_data.get("must_hits")
    if must_hits is not None and not isinstance(must_hits, list):
        errors.append("must_hits must be a list")
    
    red_lines = task_data.get("red_lines")
    if red_lines is not None and not isinstance(red_lines, list):
        errors.append("red_lines must be a list")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def validate_research_output(output: str, requirements: TaskRequirements) -> ValidationResult:
    """
    Validate research summarizer output for compliance and quality.
    
    Args:
        output: The research agent's output text
        requirements: Original task requirements
        
    Returns:
        ValidationResult with validation status and any issues
    """
    errors = []
    warnings = []
    
    # Check for Sources Register
    if "sources register" not in output.lower():
        errors.append("Missing Sources Register section")
    
    # Check for source citations [S#]
    citation_pattern = r'\[S\d+\]'
    citations = re.findall(citation_pattern, output)
    if len(citations) < 3:
        warnings.append("Few source citations found - ensure claims are properly cited")
    
    # Check for dates in sources
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    dates = re.findall(date_pattern, output)
    if len(dates) < 3:
        warnings.append("Few dates found - ensure sources include publication dates")
    
    # Check must-hits coverage if specified
    if requirements.must_hits:
        output_lower = output.lower()
        missing_hits = []
        for hit in requirements.must_hits:
            # Simple keyword check - could be made more sophisticated
            if not any(keyword.lower() in output_lower for keyword in hit.split()):
                missing_hits.append(hit)
        
        if missing_hits:
            errors.append(f"Missing must-hit coverage: {', '.join(missing_hits)}")
    
    # Check for red-line violations if specified
    if requirements.red_lines:
        output_lower = output.lower()
        violations = []
        for red_line in requirements.red_lines:
            # Simple keyword check for prohibited content
            red_line_keywords = red_line.lower().split()
            if any(keyword in output_lower for keyword in red_line_keywords):
                violations.append(red_line)
        
        if violations:
            errors.append(f"Potential red-line violations: {', '.join(violations)}")
    
    # Check minimum source count
    source_count = len(re.findall(r'^\d+\.', output, re.MULTILINE))
    if source_count < 5:
        errors.append(f"Insufficient sources found: {source_count} (minimum 5 required)")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def validate_script_output(output: str, requirements: TaskRequirements) -> ValidationResult:
    """
    Validate script drafter output for compliance and quality.
    
    Args:
        output: The script agent's output text
        requirements: Original task requirements
        
    Returns:
        ValidationResult with validation status and any issues
    """
    errors = []
    warnings = []
    
    # Check for required sections
    required_sections = ["hook", "context", "what's new", "receipts", "counterpoints", "implications"]
    output_lower = output.lower()
    
    missing_sections = []
    for section in required_sections:
        if section not in output_lower:
            missing_sections.append(section)
    
    if missing_sections:
        warnings.append(f"Missing or unclear sections: {', '.join(missing_sections)}")
    
    # Check word count (target 750-1100 words)
    word_count = len(output.split())
    if word_count < 500:
        warnings.append(f"Script may be too short: {word_count} words")
    elif word_count > 1500:
        warnings.append(f"Script may be too long: {word_count} words")
    
    # Check for source citations
    citation_pattern = r'\[S\d+\]'
    citations = re.findall(citation_pattern, output)
    if len(citations) < 3:
        warnings.append("Few source citations found in script")
    
    # Check for red-line violations if specified
    if requirements.red_lines:
        violations = []
        for red_line in requirements.red_lines:
            red_line_keywords = red_line.lower().split()
            if any(keyword in output_lower for keyword in red_line_keywords):
                violations.append(red_line)
        
        if violations:
            errors.append(f"Potential red-line violations in script: {', '.join(violations)}")
    
    # Check for speculative language (basic check)
    speculative_phrases = ["will likely", "probably will", "expected to", "should result in"]
    found_speculation = []
    for phrase in speculative_phrases:
        if phrase in output_lower:
            found_speculation.append(phrase)
    
    if found_speculation:
        warnings.append(f"Potentially speculative language found: {', '.join(found_speculation)}")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def format_validation_report(result: ValidationResult, agent_name: str) -> str:
    """
    Format a validation result into a readable report.
    
    Args:
        result: ValidationResult to format
        agent_name: Name of the agent being validated
        
    Returns:
        Formatted validation report string
    """
    report = [f"=== {agent_name} Validation Report ==="]
    report.append(f"Status: {'✅ PASSED' if result.is_valid else '❌ FAILED'}")
    
    if result.errors:
        report.append("\n🚨 ERRORS:")
        for error in result.errors:
            report.append(f"  - {error}")
    
    if result.warnings:
        report.append("\n⚠️  WARNINGS:")
        for warning in result.warnings:
            report.append(f"  - {warning}")
    
    if result.is_valid and not result.warnings:
        report.append("\n✨ All checks passed!")
    
    return "\n".join(report)
