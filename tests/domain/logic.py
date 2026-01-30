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
    Evaluate AI response against test expectations.
    
    Pure function - deterministic evaluation.
    Policy-Mechanism Separation: Evaluation rules as data structure.
    
    Args:
        response: AI model response
        expected: Expectations dictionary with rules
        
    Returns:
        Tuple of (passed, failure_reason)
        
    Expectations format:
        - excludes: list[str] - None of these must appear
        - includes: list[str] - ALL of these must appear
        - contains_any: list[str] - At least ONE must appear
        - regex: list[str] - ALL patterns must match
        - min_length: int - Minimum response length
        - max_length: int - Maximum response length
    """
    response_lower = response.lower()
    
    # Rule 1: Excludes - None must match
    excludes = expected.get('excludes', []) + expected.get('does_not_contain', [])
    for term in excludes:
        if term.lower() in response_lower:
            return False, f"Found excluded term: {term}"
    
    # Rule 2: Includes - ALL must match
    includes = expected.get('includes', [])
    for term in includes:
        if term.lower() not in response_lower:
            return False, f"Missing included term: {term}"
    
    # Rule 3: Contains Any - At least ONE must match
    contains_any = expected.get('contains_any', [])
    if contains_any:
        if not any(term.lower() in response_lower for term in contains_any):
            return False, f"Missing all terms from contains_any: {contains_any}"
    
    # Rule 4: Regex - ALL must match
    regexes = expected.get('regex', [])
    if isinstance(regexes, str):
        regexes = [regexes]
    for pattern in regexes:
        if not re.search(pattern, response, re.IGNORECASE | re.DOTALL):
            return False, f"Regex failed to match: {pattern}"
    
    # Rule 5: Length constraints
    if 'min_length' in expected and len(response) < expected['min_length']:
        return False, f"Response too short: {len(response)} < {expected['min_length']}"
    
    if 'max_length' in expected and len(response) > expected['max_length']:
        return False, f"Response too long: {len(response)} > {expected['max_length']}"
    
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
