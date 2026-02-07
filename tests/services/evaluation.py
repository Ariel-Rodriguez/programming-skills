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
        skill_version=skill.version,
        baseline_results=tuple(baseline_results),
        skill_results=tuple(skill_results),
        judgment=judgment,
        judge_error=(use_judge and judgment is None)
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
            input=test.input_prompt,
            expected=test.expected,
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
        input=test.input_prompt,
        expected=test.expected,
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
    if verbose:
        print("    Running blind comparison evaluation...")
    
    # Combine all responses (focus on actual code, not individual test results)
    without_skill_response = "\n\n".join(r.response for r in baseline_results if r.response)
    with_skill_response = "\n\n".join(r.response for r in skill_results if r.response)
    
    if not without_skill_response or not with_skill_response:
        if verbose:
            print("      [JUDGE SKIP] Missing responses to evaluate")
        return None
    
    # Consistent naming for debugging: A = without_skill, B = with_skill (no randomization)
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
        without_skill_response=without_skill_response,  # Always A
        with_skill_response=with_skill_response         # Always B
    )
    
    # Call model with retry logic
    attempts = 0
    max_attempts = 2
    current_prompt = prompt
    
    while attempts < max_attempts:
        attempts += 1
        result = model_port.call(current_prompt, config)
        
        if is_failure(result):
            if verbose:
                print(f"      [JUDGE ERROR] Attempt {attempts}: {result.error_message}")
            return None
        
        # Parse judgment
        try:
            judgment_response = parse_judgment_response(result.value)
            
            # Calculate deterministic score based on test pass rates
            with_skill_passed = sum(1 for r in skill_results if r.passed)
            total_tests = len(skill_results)
            deterministic_score = (with_skill_passed / total_tests * 100) if total_tests > 0 else 0
            
            # Create judgment with deterministic score
            judgment = JudgmentResult(
                principle_better=judgment_response.principle_better,
                quality_better=judgment_response.quality_better,
                overall_better=judgment_response.overall_better,
                option_a_rating=judgment_response.option_a_rating,
                option_b_rating=judgment_response.option_b_rating,
                score=int(deterministic_score),
                reasoning=judgment_response.reasoning
            )
            
            if verbose:
                overall_better = judgment.overall_better
                imp_label = "yes" if overall_better == 'B' else ("no" if overall_better == 'A' else "neutral")
                print(f"      [JUDGE] improvement: {imp_label} (score: {judgment.score}/100 = {with_skill_passed}/{total_tests} tests)")
            return judgment
            
        except ValueError as e:
            if verbose:
                print(f"      [JUDGE PARSE ERROR] Attempt {attempts}: {e}")
            
            if attempts < max_attempts:
                if verbose:
                    print("      [JUDGE RETRY] Requesting correction...")
                # Update prompt for next attempt with error feedback
                correction_feedback = f"\n\nERROR FROM LAST ATTEMPT: {str(e)}\nYour previous response could not be parsed. Please respond ONLY with the corrected JSON object matching the requested schema strictly."
                current_prompt = prompt + correction_feedback
            else:
                return None
    return None

