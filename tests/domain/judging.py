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
    principle_better: Literal["A", "B", "Equal"]  # Which solution better follows principle
    quality_better: Literal["A", "B", "Equal"]    # Which solution has better code quality
    overall_better: Literal["A", "B", "Equal"]    # Overall winner
    score: int  # 0-100, rating of the better solution
    reasoning: str
    # Note: A = without_skill, B = with_skill (consistent, non-randomized for debugging)
    
    @property
    def is_improvement(self) -> bool:
        """
        Smart improvement detection:
        
        PASS (return True) if:
        - With_skill (B) is chosen as better, OR
        - Equal AND score >= 50 (at least some improvement or neutral-good)
        
        FAIL (return False) if:
        - Without_skill (A) is chosen as better (degradation), OR
        - Equal AND score < 50 (neutral with low performance)
        
        Logic:
        - If ANY case shows degradation (A is better) → FAIL
        - If ALL cases are neutral (Equal) AND score < 50 → FAIL (not worth it)
        - If skill (B) wins in any case → PASS
        - If Equal but score >= 50 (at least half tests pass) → PASS (reasonable)
        """
        # FAIL if skill caused degradation
        if self.overall_better == "A":
            return False
        
        # PASS if skill improved
        if self.overall_better == "B":
            return True
        
        # For Equal: pass if score is reasonable (at least 50%)
        # This means at least half the tests pass, which is acceptable for neutral-good code
        return self.score >= 50


def build_judgment_prompt(
    principle: str,
    instructions: str,
    without_skill_response: str,
    with_skill_response: str
) -> str:
    """
    Build a blind comparison prompt for LLM self-judgment.
    
    The model doesn't know which version had skill guidance.
    It must evaluate them on principle adherence and choose which is better.
    This creates a fair, unbiased evaluation.
    
    Internally, we always put without_skill as "Solution A" and with_skill as "Solution B"
    for consistent debugging. The judge doesn't know this.
    
    Args:
        principle: The core principle being taught (e.g., "Composition over Coordination")
        instructions: Key rules/guidance from the skill
        without_skill_response: Code generated without skill guidance (always Solution A)
        with_skill_response: Code generated with skill guidance (always Solution B)
    
    Returns:
        Blind comparison evaluation prompt
    """
    # Consistent naming for debugging: A = without skill, B = with skill
    option_a = without_skill_response
    option_b = with_skill_response
    
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


def parse_judgment_response(response: str) -> JudgmentResult:
    """
    Parse LLM judge response into JudgmentResult.
    
    Args:
        response: Raw LLM response (should be JSON)
    
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
        reasoning=reasoning
    )
