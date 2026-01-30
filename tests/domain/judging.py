"""
Domain logic for LLM-based judgment of code quality.

This module provides semantic evaluation of code responses using an LLM judge,
rather than relying solely on mechanical pattern matching.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class JudgmentResult:
    """Result of LLM judge evaluation."""
    follows_principle: Literal["Yes", "No", "Partial"]
    vs_baseline: Literal["Better", "Same", "Worse"]
    score: int  # 0-100
    reasoning: str
    
    @property
    def is_improvement(self) -> bool:
        """Whether the skill response is better than baseline."""
        return self.vs_baseline == "Better" and self.score >= 70


def build_judgment_prompt(
    principle: str,
    instructions: str,
    baseline_response: str,
    skill_response: str
) -> str:
    """
    Build a prompt for LLM judge to evaluate code quality.
    
    Args:
        principle: The core principle being taught (e.g., "Composition over Coordination")
        instructions: Key rules/guidance from the skill
        baseline_response: Code generated without skill guidance
        skill_response: Code generated with skill guidance
    
    Returns:
        Evaluation prompt for the judge
    """
    return f"""You are evaluating whether code follows a programming principle.

PRINCIPLE: {principle}

KEY INSTRUCTIONS:
{instructions}

BASELINE CODE (without skill guidance):
```
{baseline_response}
```

REFACTORED CODE (with skill guidance):
```
{skill_response}
```

Evaluate the refactored code on these criteria:

1. **Follows Principle**: Does the refactored code follow the stated principle?
   - "Yes" if it clearly demonstrates the principle
   - "Partial" if it shows some adherence but has issues
   - "No" if it violates or ignores the principle

2. **vs Baseline**: Is the refactored code better than the baseline?
   - "Better" if it's a clear improvement
   - "Same" if there's no meaningful difference
   - "Worse" if the baseline was actually better

3. **Score**: Overall quality score from 0-100
   - 90-100: Excellent demonstration of principle
   - 70-89: Good adherence with minor issues
   - 50-69: Partial adherence, some problems
   - 0-49: Poor adherence or violates principle

4. **Reasoning**: Brief explanation (2-3 sentences) of your evaluation

Respond ONLY with valid JSON in this exact format:
{{
  "follows_principle": "Yes/No/Partial",
  "vs_baseline": "Better/Same/Worse",
  "score": 85,
  "reasoning": "Your explanation here"
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
    follows_principle = data.get("follows_principle", "").strip()
    if follows_principle not in ["Yes", "No", "Partial"]:
        raise ValueError(f"Invalid follows_principle: {follows_principle}")
    
    vs_baseline = data.get("vs_baseline", "").strip()
    if vs_baseline not in ["Better", "Same", "Worse"]:
        raise ValueError(f"Invalid vs_baseline: {vs_baseline}")
    
    score = data.get("score")
    if not isinstance(score, int) or not 0 <= score <= 100:
        raise ValueError(f"Invalid score: {score}")
    
    reasoning = data.get("reasoning", "").strip()
    if not reasoning:
        raise ValueError("Missing reasoning")
    
    return JudgmentResult(
        follows_principle=follows_principle,  # type: ignore
        vs_baseline=vs_baseline,  # type: ignore
        score=score,
        reasoning=reasoning
    )
