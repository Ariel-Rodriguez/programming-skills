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
        
        # Transform to TestCase objects
        test_cases = []
        for test_data in raw_tests:
            # Prefer 'spec' (new format), fallback to 'input' (legacy)
            input_prompt = test_data.get('spec') or test_data.get('input', '')
            
            test_cases.append(TestCase(
                name=test_data.get('name', 'Unnamed'),
                input_prompt=input_prompt,
                expected=test_data.get('expected', {})
            ))
        
        return Success(test_cases)
    
    except json.JSONDecodeError as e:
        return Failure(f"Invalid JSON in {json_path}", {"error": str(e)})

    # Note: _inject_external_files removed directly as per refactor plan
