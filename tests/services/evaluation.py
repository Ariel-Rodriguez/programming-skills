"""
Evaluation Service

Single Responsibility: Runs test evaluations against models.
"""

from domain import (
    Skill,
    TestSuite,
    TestCase,
    TestResult,
    EvaluationResult,
    ModelConfig,
    build_skill_instruction,
    evaluate_response_against_expectations,
    is_failure,
    JudgmentResult,
    build_judgment_prompt,
    parse_judgment_response,
)
from ports import ModelPort


def run_evaluation(
    skill: Skill,
    test_suite: TestSuite,
    model_port: ModelPort,
    config: ModelConfig,
    verbose: bool = False,
    use_judge: bool = False
) -> EvaluationResult:
    """
    Run complete evaluation: baseline vs skill-enhanced.
    
    Single Direction Data Flow: Tests → execution → results.
    Composition Over Coordination: Composes simple test runs.
    
    Args:
        skill: Skill being evaluated
        test_suite: Tests to run
        model_port: AI model adapter
        config: Model configuration
        verbose: Print progress
        use_judge: Use LLM judge for semantic evaluation
        
    Returns:
        EvaluationResult with baseline and skill results
    """
    skill_instruction = build_skill_instruction(skill.content)
    
    baseline_results = []
    skill_results = []
    
    for test in test_suite.tests:
        if verbose:
            print(f"    Running test: {test.name}...")
        
        # Baseline run (no skill context)
        baseline_result = _run_single_test(
            test, model_port, config, ""
        )
        baseline_results.append(baseline_result)
        
        # Skill run (with skill instruction)
        skill_result = _run_single_test(
            test, model_port, config, skill_instruction
        )
        skill_results.append(skill_result)
        
        # Verbose output
        if verbose:
            if not baseline_result.passed:
                print(f"      [BASELINE FAIL] {test.name}: {baseline_result.failure_reason}")
            if not skill_result.passed:
                print(f"      [SKILL FAIL] {test.name}: {skill_result.failure_reason}")
    
    # Optional: Run LLM judge evaluation
    judgment = None
    if use_judge:
        judgment = _run_judge_evaluation(
            skill, baseline_results, skill_results, model_port, config, verbose
        )
    
    # Return immutable result
    return EvaluationResult(
        skill_name=skill.name,
        severity=skill.severity,
        model=config.model_name,
        baseline_results=tuple(baseline_results),
        skill_results=tuple(skill_results),
        judgment=judgment
    )


def _run_single_test(
    test: TestCase,
    model_port: ModelPort,
    config: ModelConfig,
    skill_instruction: str
) -> TestResult:
    """
    Run a single test case.
    
    Local Reasoning: All dependencies explicit.
    Error Handling Design: Model errors become test failures.
    
    Args:
        test: Test case to run
        model_port: AI model adapter
        config: Model configuration
        skill_instruction: Optional skill context (empty for baseline)
        
    Returns:
        TestResult with pass/fail and response
    """
    # Build full prompt
    prompt = skill_instruction + test.input_prompt
    
    # Call model
    result = model_port.call(prompt, config)
    
    # Handle model errors
    if is_failure(result):
        # Always print model errors, not just in verbose mode
        print(f"      [MODEL ERROR] {test.name}: {result.error_message}")
        return TestResult(
            test_name=test.name,
            passed=False,
            response="",
            failure_reason=result.error_message
        )
    
    # Evaluate response (pure function)
    response = result.value
    passed, reason = evaluate_response_against_expectations(
        response, test.expected
    )
    
    return TestResult(
        test_name=test.name,
        passed=passed,
        response=response,
        failure_reason=reason
    )


def _run_judge_evaluation(
    skill: Skill,
    baseline_results: list[TestResult],
    skill_results: list[TestResult],
    model_port: ModelPort,
    config: ModelConfig,
    verbose: bool
) -> JudgmentResult | None:
    """
    Run LLM blind comparison to evaluate if skill improves code quality.
    
    Model doesn't know which version is baseline vs skill - fair evaluation.
    
    Args:
        skill: Skill being evaluated
        baseline_results: Results from baseline run
        skill_results: Results from skill-enhanced run
        model_port: AI model adapter
        config: Model configuration
        verbose: Print progress
        
    Returns:
        JudgmentResult or None if judgment fails
    """
    import random
    
    if verbose:
        print("    Running blind comparison evaluation...")
    
    # Combine all responses (focus on actual code, not individual test results)
    baseline_response = "\n\n".join(r.response for r in baseline_results if r.response)
    skill_response = "\n\n".join(r.response for r in skill_results if r.response)
    
    if not baseline_response or not skill_response:
        if verbose:
            print("      [JUDGE SKIP] Missing responses to evaluate")
        return None
    
    # Randomize which is A and which is B
    baseline_is_a = random.random() > 0.5
    if baseline_is_a:
        option_a = baseline_response
        option_b = skill_response
    else:
        option_a = skill_response
        option_b = baseline_response
    
    # Extract principle and instructions from skill
    from domain.skill_extraction import extract_skill_guidance
    guidance = extract_skill_guidance(skill.content)
    
    # Build judgment prompt
    lines = skill.content.split('\n')
    principle = ""
    for line in lines:
        if line.strip().startswith('## Principle'):
            idx = lines.index(line)
            if idx + 1 < len(lines):
                principle = lines[idx + 1].strip()
                break
    
    if not principle:
        principle = skill.description
    
    prompt = build_judgment_prompt(
        principle=principle,
        instructions=guidance,
        baseline_response=option_a,  # Could be baseline or skill
        skill_response=option_b       # Could be skill or baseline
    )
    
    # Call model
    result = model_port.call(prompt, config)
    
    if is_failure(result):
        if verbose:
            print(f"      [JUDGE ERROR] {result.error_message}")
        return None
    
    # Parse judgment with baseline_is_a info
    try:
        judgment_response = parse_judgment_response(result.value, baseline_is_a=baseline_is_a)
        
        # Calculate deterministic score based on test pass rates
        # Score = how many tests passed with the skill version
        skill_passed = sum(1 for r in skill_results if r.passed)
        total_tests = len(skill_results)
        deterministic_score = (skill_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Create judgment with deterministic score, not vibes
        judgment = JudgmentResult(
            principle_better=judgment_response.principle_better,
            quality_better=judgment_response.quality_better,
            overall_better=judgment_response.overall_better,
            score=int(deterministic_score),  # Deterministic: % tests passed
            reasoning=judgment_response.reasoning,
            baseline_is_a=baseline_is_a
        )
        
        if verbose:
            better = judgment.overall_better
            skill_won = better == "B" if baseline_is_a else better == "A"
            status = "✓ Skill improved" if skill_won else "✗ No improvement"
            print(f"      [JUDGE] {status} (score: {judgment.score}/100 = {skill_passed}/{total_tests} tests)")
        return judgment
    except ValueError as e:
        if verbose:
            print(f"      [JUDGE PARSE ERROR] {e}")
        return None

