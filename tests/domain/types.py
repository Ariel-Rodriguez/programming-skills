"""
Domain Types - Illegal States Unrepresentable

Immutable domain types representing the core business concepts.
No dependencies on external systems or frameworks.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Union, Any


class Severity(Enum):
    """Explicit severity levels for skills"""
    SUGGEST = "SUGGEST"
    WARN = "WARN"
    BLOCK = "BLOCK"


class Provider(Enum):
    """AI model providers"""
    OLLAMA = "ollama"
    COPILOT = "copilot"


@dataclass(frozen=True)
class Skill:
    """
    Immutable skill representation.
    Minimize Mutation: Frozen dataclass prevents accidental changes.
    """
    name: str
    path: Path
    description: str
    content: str
    severity: Severity


@dataclass(frozen=True)
class TestCase:
    """
    Immutable test case.
    Naming as Design: Clear purpose from name alone.
    """
    name: str
    input_prompt: str
    expected: dict


@dataclass(frozen=True)
class TestSuite:
    """
    Collection of test cases for a skill.
    Explicit State Invariants: Count is derived, not stored.
    """
    skill_name: str
    severity: Severity
    tests: tuple[TestCase, ...]
    
    @property
    def test_count(self) -> int:
        """Derived data, not duplicate state"""
        return len(self.tests)


@dataclass(frozen=True)
class ModelConfig:
    """
    Model configuration with sensible defaults.
    Local Reasoning: All config in one place.
    """
    provider: Provider
    model_name: str
    base_url: str
    num_ctx: int = 64000


@dataclass(frozen=True)
class TestResult:
    """
    Single test execution result.
    Explicit State Invariants: Either passed or has failure_reason.
    """
    test_name: str
    passed: bool
    response: str
    failure_reason: str = ""
    
    @property
    def response_preview(self) -> str:
        """Derived preview for display"""
        max_length = 100
        if len(self.response) > max_length:
            return self.response[:max_length] + "..."
        return self.response


@dataclass(frozen=True)
class EvaluationResult:
    """
    Complete evaluation result comparing baseline vs skill-enhanced runs.
    Single Direction Data Flow: Data flows in, derived metrics flow out.
    """
    skill_name: str
    severity: Severity
    model: str
    baseline_results: tuple[TestResult, ...]
    skill_results: tuple[TestResult, ...]
    judgment: "JudgmentResult | None" = None  # Optional LLM judge evaluation
    
    @property
    def baseline_pass_rate(self) -> int:
        """Pure calculation: baseline pass percentage"""
        return self._calculate_pass_rate(self.baseline_results)
    
    @property
    def skill_pass_rate(self) -> int:
        """Pure calculation: skill pass percentage"""
        return self._calculate_pass_rate(self.skill_results)
    
    @property
    def improvement(self) -> int:
        """Pure calculation: improvement delta"""
        return self.skill_pass_rate - self.baseline_pass_rate
    
    @property
    def baseline_rating(self) -> str:
        """Categorical rating for baseline, adjusted by judge verdict"""
        from .logic import get_rating_label
        baseline_raw = get_rating_label(self.baseline_pass_rate)
        
        if not self.judgment or self.judgment.overall_better == "Equal":
            return baseline_raw
            
        # If skill (B) is better, baseline (A) should be at most one level below skill
        if self.judgment.overall_better == "B":
            skill_raw = get_rating_label(self.skill_pass_rate)
            return self._downgrade_if_equal(baseline_raw, skill_raw)
            
        return baseline_raw
    
    @property
    def skill_rating(self) -> str:
        """Categorical rating for skill-enhanced, adjusted by judge verdict"""
        from .logic import get_rating_label
        skill_raw = get_rating_label(self.skill_pass_rate)
        
        if not self.judgment or self.judgment.overall_better == "Equal":
            return skill_raw
            
        # If baseline (A) is better, skill (B) should be at most one level below baseline
        if self.judgment.overall_better == "A":
            baseline_raw = get_rating_label(self.baseline_pass_rate)
            return self._downgrade_if_equal(skill_raw, baseline_raw)
            
        return skill_raw
    
    def _downgrade_if_equal(self, raw_label: str, winner_label: str) -> str:
        """Helper to ensure loser rating is strictly below winner rating if they were equal"""
        ratings = ["vague", "regular", "good", "outstanding"]
        
        try:
            raw_idx = ratings.index(raw_label)
            winner_idx = ratings.index(winner_label)
            
            # If loser is same as winner or higher (mechanical tie or anomaly), 
            # force loser to be one level below winner (capped at vague)
            if raw_idx >= winner_idx:
                new_idx = max(0, winner_idx - 1)
                return ratings[new_idx]
        except ValueError:
            pass
            
        return raw_label

    @property
    def baseline_pass_count(self) -> str:
        """String representation of baseline pass count: n/N"""
        passed = sum(1 for r in self.baseline_results if r.passed)
        return f"{passed}/{len(self.baseline_results)}"
    
    @property
    def skill_pass_count(self) -> str:
        """String representation of skill pass count: n/N"""
        passed = sum(1 for r in self.skill_results if r.passed)
        return f"{passed}/{len(self.skill_results)}"

    @staticmethod
    def _calculate_pass_rate(results: tuple[TestResult, ...]) -> int:
        """Policy-Mechanism Separation: Reusable calculation"""
        if not results:
            return 0
        passed = sum(1 for r in results if r.passed)
        return int((passed / len(results)) * 100)


# Error Handling Design: Result types for explicit error handling

@dataclass(frozen=True)
class Success:
    """
    Successful operation result.
    Explicit error handling instead of exceptions.
    """
    value: Any


@dataclass(frozen=True)
class Failure:
    """
    Failed operation result with context.
    Error Handling Design: Errors part of type signature.
    """
    error_message: str
    context: dict = field(default_factory=dict)


# Result type: Makes success/failure explicit in function signatures
Result = Union[Success, Failure]


def is_success(result: Result) -> bool:
    """Type guard for Success"""
    return isinstance(result, Success)


def is_failure(result: Result) -> bool:
    """Type guard for Failure"""
    return isinstance(result, Failure)
