import pathlib
import re

def update_skills():
    skills_dir = pathlib.Path('skills')
    for skill_file in skills_dir.glob('**/SKILL.md'):
        print(f"Updating {skill_file}")
        content = skill_file.read_text(encoding='utf-8')
        
        # Add version after severity if it doesn't exist
        if 'version:' not in content:
            new_content = re.sub(
                r'severity:\s*(BLOCK|WARN|SUGGEST)',
                r'severity: \1\nversion: 1.0.0',
                content
            )
            skill_file.write_text(new_content, encoding='utf-8')

if __name__ == "__main__":
    update_skills()
