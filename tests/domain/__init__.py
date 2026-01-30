"""
Domain Layer - Pure Business Logic

Explicit Boundaries: Domain isolated from infrastructure.
Functional Core: No side effects, all pure functions.
"""

from .types import (
    Severity,
    Provider,
    Skill,
    TestCase,
    TestSuite,
    ModelConfig,
    TestResult,
    EvaluationResult,
    Success,
    Failure,
    Result,
    is_success,
    is_failure,
)
from .logic import (
    parse_skill_frontmatter,
    extract_description_from_content,
    evaluate_response_against_expectations,
    build_skill_instruction,
)
from .skill_extraction import (
    extract_skill_guidance,
)
from .judging import (
    JudgmentResult,
    build_judgment_prompt,
    parse_judgment_response,
)

__all__ = [
    # Types
    "Severity",
    "Provider",
    "Skill",
    "TestCase",
    "TestSuite",
    "ModelConfig",
    "TestResult",
    "EvaluationResult",
    "Success",
    "Failure",
    "Result",
    "is_success",
    "is_failure",
    # Logic
    "parse_skill_frontmatter",
    "extract_description_from_content",
    "evaluate_response_against_expectations",
    "build_skill_instruction",
    "extract_skill_guidance",
    # Judging
    "JudgmentResult",
    "build_judgment_prompt",
    "parse_judgment_response",
]
