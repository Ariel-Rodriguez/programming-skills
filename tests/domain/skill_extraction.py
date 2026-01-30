"""
Smart Skill Extraction

Extracts focused guidance from skills instead of dumping entire files.
Policy-Mechanism Separation: Extraction rules as data, parsing as mechanism.
"""

import re


def extract_skill_guidance(skill_content: str) -> str:
    """
    Extract focused skill guidance for model prompting.
    
    Includes:
    - Principle section (core concept)
    - Instructions/Rules
    - ONE good example (not all examples)
    
    Excludes:
    - Bad examples
    - Checklists
    - References
    - Meta sections
    
    Args:
        skill_content: Full SKILL.md content
        
    Returns:
        Condensed guidance (~15-20% of original size)
    """
    sections = _parse_markdown_sections(skill_content)
    
    parts = []
    
    # 1. Principle - The "why"
    if 'Principle' in sections:
        parts.append("## Core Principle\n" + sections['Principle'])
    
    # 2. Instructions - The "how"
    if 'Instructions' in sections:
        parts.append("## Key Guidelines\n" + sections['Instructions'])
    elif 'When to Use' in sections:
        parts.append("## When to Apply\n" + sections['When to Use'])
    
    # 3. ONE good example - concrete demonstration
    if 'Examples' in sections:
        good_example = _extract_first_good_example(sections['Examples'])
        if good_example:
            parts.append("## Example\n" + good_example)
    
    return '\n\n'.join(parts)


def _parse_markdown_sections(content: str) -> dict[str, str]:
    """
    Parse markdown into sections by ## headers.
    
    Pure function: String parsing only.
    
    Args:
        content: Markdown content
        
    Returns:
        Dict of section_name -> section_content
    """
    sections = {}
    
    # Remove frontmatter
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    
    # Split by ## headers
    parts = re.split(r'\n## ', content)
    
    for part in parts[1:]:  # Skip content before first ##
        lines = part.split('\n', 1)
        if len(lines) == 2:
            section_name = lines[0].strip()
            section_content = lines[1].strip()
            sections[section_name] = section_content
    
    return sections


def _extract_first_good_example(examples_section: str) -> str:
    """
    Extract first "good" example from Examples section.
    
    Looks for patterns like:
    - ### ✅ Good: ...
    - ### Good: ...
    - First code block after "good" indicator
    
    Args:
        examples_section: Content of Examples section
        
    Returns:
        First good example with context, or empty string
    """
    # Look for good example marker
    good_pattern = r'###\s*[✅✓]?\s*Good[:\s]+(.*?)(?=\n###|\n##|$)'
    match = re.search(good_pattern, examples_section, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return ""
    
    good_content = match.group(1).strip()
    
    # Limit to ~500 chars to keep it focused
    if len(good_content) > 500:
        # Try to cut at a natural boundary (end of code block or paragraph)
        code_block_end = good_content.find('```', good_content.find('```') + 3)
        if code_block_end > 0 and code_block_end < 500:
            good_content = good_content[:code_block_end + 3]
        else:
            good_content = good_content[:500] + "\n..."
    
    return good_content
