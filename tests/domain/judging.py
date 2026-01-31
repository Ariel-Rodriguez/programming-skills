"""
Domain logic for LLM-based judgment of code quality.

This module provides semantic evaluation of code responses using an LLM judge,
rather than relying solely on mechanical pattern matching.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class JudgmentResult:
    """Result of blind LLM comparison evaluation."""
    principle_better: Literal["A", "B", "Equal"]  # Which option better follows principle
    quality_better: Literal["A", "B", "Equal"]    # Which option has better code quality
    overall_better: Literal["A", "B", "Equal"]    # Overall winner
    score: int  # 0-100, rating of the better solution
    reasoning: str
    baseline_is_a: bool  # Track which option (A or B) was the baseline
    
    @property
    def is_improvement(self) -> bool:
        """
        Whether the skill version (which might be A or B) is better than baseline.
        If baseline_is_a=True, then we want B to be better (skill version).
        If baseline_is_a=False, then we want A to be better (skill version).
        
        Returns True only if skill version is clearly better AND score is good.
        """
        target = "B" if self.baseline_is_a else "A"
        is_better = self.overall_better == target  # Skill must win, not tie
        is_quality = self.score >= 70
        return is_better and is_quality


def build_judgment_prompt(
    principle: str,
    instructions: str,
    baseline_response: str,
    skill_response: str
) -> str:
    """
    Build a blind comparison prompt for LLM self-judgment.
    
    The model doesn't know which version is baseline vs skill.
    It must evaluate them on principle adherence and choose which is better.
    This creates a fair, unbiased evaluation without revealing treatment.
    
    Args:
        principle: The core principle being taught (e.g., "Composition over Coordination")
        instructions: Key rules/guidance from the skill
        baseline_response: Code generated without skill guidance (Option A or B)
        skill_response: Code generated with skill guidance (Option A or B)
    
    Returns:
        Blind comparison evaluation prompt
    """
    import random
    # Randomize which response goes first to avoid position bias
    if random.random() > 0.5:
        option_a = baseline_response
        option_b = skill_response
    else:
        option_a = skill_response
        option_b = baseline_response
    
    return f"""You are comparing two code solutions to determine which better follows a programming principle.

PRINCIPLE TO EVALUATE: {principle}

GUIDELINES:
{instructions}

---

SOLUTION A:
```
{option_a}
```

SOLUTION B:
```
{option_b}
```

---

Compare the solutions fairly without knowing which came first:

1. **Principle Adherence**: Which solution better demonstrates the principle (A, B, or Equal)?

2. **Code Quality**: Which solution is more maintainable, testable, and flexible (A, B, or Equal)?

3. **Overall Verdict**: Which solution is better overall?

4. **Reasoning**: 2-3 sentences explaining your choice

NOTE: You'll notice there's no score field below. The actual quality score is computed deterministically 
from how many test scenarios pass (not vibes/subjective rating). You're evaluating semantic quality and 
principle adherence, not scoring.

Respond ONLY with valid JSON:
{{
  "principle_better": "A/B/Equal",
  "quality_better": "A/B/Equal",
  "overall_better": "A/B/Equal",
  "reasoning": "Your explanation"
}}"""


def parse_judgment_response(response: str, baseline_is_a: bool = True) -> JudgmentResult:
    """
    Parse LLM judge response into JudgmentResult.
    
    Args:
        response: Raw LLM response (should be JSON)
        baseline_is_a: Whether baseline version was assigned to Option A
    
    Returns:
        Parsed JudgmentResult
    
    Raises:
        ValueError: If response is not valid JSON or missing required fields
    """
    import json
    import re
    
    # Extract JSON from response (might have markdown code blocks)
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find raw JSON
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            raise ValueError(f"No JSON found in response: {response[:200]}")
    
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in response: {e}") from e
    
    # Validate and extract fields
    principle_better = data.get("principle_better", "").strip()
    if principle_better not in ["A", "B", "Equal"]:
        raise ValueError(f"Invalid principle_better: {principle_better}")
    
    quality_better = data.get("quality_better", "").strip()
    if quality_better not in ["A", "B", "Equal"]:
        raise ValueError(f"Invalid quality_better: {quality_better}")
    
    overall_better = data.get("overall_better", "").strip()
    if overall_better not in ["A", "B", "Equal"]:
        raise ValueError(f"Invalid overall_better: {overall_better}")
    
    reasoning = data.get("reasoning", "").strip()
    if not reasoning:
        raise ValueError("Missing reasoning")
    
    # Note: score is NOT from judge response anymore
    # It will be set by the evaluation service based on test pass rates
    # Here we use a placeholder that will be replaced
    return JudgmentResult(
        principle_better=principle_better,  # type: ignore
        quality_better=quality_better,  # type: ignore
        overall_better=overall_better,  # type: ignore
        score=0,  # Placeholder - will be set by evaluation service
        reasoning=reasoning,
        baseline_is_a=baseline_is_a  # Passed by caller based on randomization
    )
