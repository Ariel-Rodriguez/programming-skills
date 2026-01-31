"""
Domain Logic - Pure Functions

Functional Core, Imperative Shell: Pure computation, no side effects.
Local Reasoning: All dependencies explicit in function signatures.
"""

import re
from .types import Severity


def parse_skill_frontmatter(content: str) -> tuple[str, Severity]:
    """
    Extract description and severity from YAML frontmatter.
    
    Pure function - deterministic, no IO.
    Policy-Mechanism Separation: Parsing logic separated from file reading.
    
    Args:
        content: Markdown file content
        
    Returns:
        Tuple of (description, severity)
    """
    description = ""
    severity = Severity.SUGGEST
    
    if not content.startswith("---"):
        return description, severity
    
    frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return description, severity
    
    frontmatter = frontmatter_match.group(1)
    
    # Extract description
    desc_match = re.search(r'description:\s*["\']?(.+?)["\']?\s*\n', frontmatter)
    if desc_match:
        description = desc_match.group(1)
    
    # Extract severity
    sev_match = re.search(r'severity:\s*(\w+)', frontmatter)
    if sev_match:
        try:
            severity = Severity(sev_match.group(1).upper())
        except ValueError:
            # Default to SUGGEST if invalid severity
            severity = Severity.SUGGEST
    
    return description, severity


def extract_description_from_content(content: str) -> str:
    """
    Extract description from first meaningful paragraph.
    
    Pure function - no side effects.
    Naming as Design: Function name reveals intent.
    
    Args:
        content: Markdown content
        
    Returns:
        First non-empty, non-header line
    """
    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('---'):
            return stripped
    return ""


def evaluate_response_against_expectations(response: str, expected: dict) -> tuple[bool, str]:
    """
    Evaluate AI response - now just checks if response exists.
    
    Pure function - deterministic evaluation.
    Simplified: No mechanical rules, only semantic judgment.
    
    The "focus" field in expected is guidance for the judge, not rules.
    Actual scoring is deterministic: (tests_passed / total_tests) * 100
    
    Args:
        response: AI model response
        expected: Expectations dictionary with "focus" guidance
        
    Returns:
        Tuple of (passed, failure_reason)
        - Passes if response is non-empty
        - Judge will evaluate semantic quality
    """
    # Check if response is substantive (not just error or empty)
    if not response or len(response.strip()) < 10:
        return False, "Response too brief or empty"
    
    # If we get here, response is acceptable for judge evaluation
    return True, ""


def build_skill_instruction(skill_content: str) -> str:
    """
    Build instruction prompt from skill content.
    
    Uses smart extraction to focus on core guidance.
    Policy-Mechanism Separation: Extraction logic separated.
    
    Args:
        skill_content: Full skill markdown content
        
    Returns:
        Formatted instruction prompt with focused guidance
    """
    from .skill_extraction import extract_skill_guidance
    
    focused_guidance = extract_skill_guidance(skill_content)
    return f"Apply the following programming skill:\n\n{focused_guidance}\n\n"
