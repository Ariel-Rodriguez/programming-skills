"""
Skill Discovery Service

Single Responsibility: Discovers and parses skills from filesystem.
"""

from pathlib import Path
from domain import Skill, Severity, parse_skill_frontmatter, extract_description_from_content, is_failure
from ports import FileSystemPort


def discover_skills(skills_dir: Path, fs: FileSystemPort) -> tuple[Skill, ...]:
    """
    Discover all skills from directory.
    
    Local Reasoning: All dependencies explicit (fs injected).
    Single Direction Data Flow: Files → parsing → Skill objects.
    Minimize Mutation: Returns immutable tuple.
    
    Args:
        skills_dir: Directory containing skill folders
        fs: Filesystem port for IO operations
        
    Returns:
        Tuple of discovered Skill objects, sorted by name
    """
    skills = []
    
    if not fs.exists(skills_dir):
        return tuple(skills)
    
    for item in fs.list_dir(skills_dir):
        if not fs.is_dir(item):
            continue
        
        skill_file = item / "SKILL.md"
        if not fs.exists(skill_file):
            continue
        
        # Read skill file
        result = fs.read_text(skill_file)
        if is_failure(result):
            # Skip skills we can't read
            continue
        
        content = result.value
        
        # Parse frontmatter (pure function)
        description, severity = parse_skill_frontmatter(content)
        
        # Fallback to content extraction if no frontmatter
        if not description:
            description = extract_description_from_content(content)
        
        # Create immutable skill object
        skills.append(Skill(
            name=item.name,
            path=item,
            description=description,
            content=content,
            severity=severity
        ))
    
    # Return sorted immutable tuple
    return tuple(sorted(skills, key=lambda s: s.name))
