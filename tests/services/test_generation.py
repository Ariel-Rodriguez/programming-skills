"""
Test Generation Service

Single Responsibility: Generates test suites from skill definitions.
"""

import json
import re
from pathlib import Path
from domain import Skill, TestCase, TestSuite, is_success, Success
from ports import FileSystemPort


def generate_test_suite(skill: Skill, fs: FileSystemPort) -> TestSuite:
    """
    Generate test suite for a skill.
    
    Policy-Mechanism Separation: Priority rules (policy) separate from loading (mechanism).
    Priority: test.json > tests.json > SKILL.md scenarios
    
    Args:
        skill: Skill to generate tests for
        fs: Filesystem port
        
    Returns:
        TestSuite with discovered tests
    """
    tests = []
    
    # Try loading from JSON files (preferred)
    for filename in ["test.json", "tests.json"]:
        json_path = skill.path / filename
        if fs.exists(json_path):
            result = _load_tests_from_json(json_path, fs, skill.path)
            if is_success(result):
                tests = result.value
                break
    
    # Fallback to markdown scenarios
    if not tests:
        tests = _extract_tests_from_markdown(skill.content)
    
    # Return immutable test suite
    return TestSuite(
        skill_name=skill.name,
        severity=skill.severity,
        tests=tuple(tests)
    )


def _load_tests_from_json(json_path: Path, fs: FileSystemPort, skill_path: Path) -> any:
    """
    Load test cases from JSON file.
    
    Error Handling Design: Returns Result type.
    Local Reasoning: All dependencies explicit.
    
    Args:
        json_path: Path to test.json file
        fs: Filesystem port
        skill_path: Path to skill directory (for loading external files)
    """
    from domain import Success, Failure
    
    result = fs.read_text(json_path)
    if isinstance(result, Failure):
        return result
    
    try:
        data = json.loads(result.value)
        raw_tests = []
        
        if isinstance(data, list):
            raw_tests = data
        elif isinstance(data, dict):
            raw_tests = data.get('tests', [])
        
        # Transform to TestCase objects with external file injection
        test_cases = []
        for test_data in raw_tests:
            input_prompt = test_data.get('input', '')
            
            # Check if input references an external file
            # Pattern: single line with filename (no newlines)
            input_prompt = _inject_external_files(input_prompt, skill_path, fs)
            
            test_cases.append(TestCase(
                name=test_data.get('name', 'Unnamed'),
                input_prompt=input_prompt,
                expected=test_data.get('expected', {})
            ))
        
        return Success(test_cases)
    
    except json.JSONDecodeError as e:
        return Failure(f"Invalid JSON in {json_path}", {"error": str(e)})


def _extract_tests_from_markdown(content: str) -> list[TestCase]:
    """
    Extract test cases from markdown benchmark scenarios section.
    
    Pure function: No IO, just string parsing.
    
    Args:
        content: Markdown content
        
    Returns:
        List of TestCase objects
    """
    tests = []
    
    # Find benchmark scenarios section
    scenario_section = re.search(
        r'## Benchmark Scenarios\s*\n(.*?)(?=\n##|$)',
        content,
        re.DOTALL
    )
    
    if not scenario_section:
        return tests
    
    scenario_content = scenario_section.group(1)
    
    # Extract JSON blocks
    json_blocks = re.findall(r'```json\n(.*?)\n```', scenario_content, re.DOTALL)
    
    for block in json_blocks:
        try:
            data = json.loads(block)
            
            if isinstance(data, list):
                for test_data in data:
                    tests.append(TestCase(
                        name=test_data.get('name', 'Unnamed'),
                        input_prompt=test_data.get('input', ''),
                        expected=test_data.get('expected', {})
                    ))
            elif isinstance(data, dict):
                tests.append(TestCase(
                    name=data.get('name', 'Unnamed'),
                    input_prompt=data.get('input', ''),
                    expected=data.get('expected', {})
                ))
        except json.JSONDecodeError:
            # Skip invalid JSON blocks
            continue
    
    return tests


def _inject_external_files(input_text: str, skill_path: Path, fs: FileSystemPort) -> str:
    """
    Inject external file contents into input text.
    
    Looks for references to files in the skill directory and replaces them with content.
    Pattern: If a line looks like a filename and the file exists, inject its content.
    
    Args:
        input_text: Input text that may reference files
        skill_path: Path to skill directory
        fs: Filesystem port
        
    Returns:
        Input text with file contents injected
    """
    # Split by lines to check for file references
    lines = input_text.split('\n')
    result_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Check if this line looks like a filename reference
        # (single word ending in .js, .py, .java, etc., no spaces)
        if stripped and not ' ' in stripped and '.' in stripped:
            # Try to load it as a file from skill directory
            file_path = skill_path / stripped
            if fs.exists(file_path) and fs.is_file(file_path):
                file_result = fs.read_text(file_path)
                if isinstance(file_result, Success):
                    # Replace the filename with the actual content in a code block
                    ext = file_path.suffix.lstrip('.')
                    result_lines.append(f"\n```{ext}")
                    result_lines.append(file_result.value)
                    result_lines.append("```\n")
                    continue
        
        # Keep the line as-is if not a file reference
        result_lines.append(line)
    
    return '\n'.join(result_lines)
