"""
Meaningful Skill Extraction

Extracts the full skill content minus metadata to ensure the model has full context.
"""

import re


def extract_skill_guidance(skill_content: str) -> str:
    """
    Extract skill guidance for model prompting.
    
    Returns:
        Full markdown content with YAML frontmatter removed.
    """
    # Remove frontmatter if present
    if skill_content.startswith("---"):
        content = re.sub(r'^---\n.*?\n---\n', '', skill_content, count=1, flags=re.DOTALL)
        return content.strip()
    
    return skill_content.strip()
