# Case Study: Fairness in Automated Judging

This document demonstrates the core philosophy of our testing suite: **We do not grade on a curve.**

Our "LLM-as-a-Judge" system is designed to evaluate the *architectural quality* of code, not just the presence of specific keywords or patterns. It naturally favors the solution that best adheres to the underlying engineering principle, even if that means the "Baseline" (standard model output) beats the "Skill" (our custom instructions).

Below are two real examples from our `ps-composition-over-coordination` skill evaluation that prove the judge's fairness.

## Case 1: The Skill Wins
**Scenario**: Refactoring a specific Orchestrator class.

| metric | Baseline (Without Skill) | Skill (With Skill) |
|--------|--------------------------|--------------------|
| **Rating** | "Vague" | **"Good"** |
| **Verdict** | Used a monolithic manager | Decomposed into functions |

### Judge's Reasoning
> "Solution B (Skill) better demonstrates the principle... It properly decomposes the system into small, focused functions... Solution A, while well-structured, still contains a monolithic Manager class that violates the Single Responsibility Principle."

**Why it matters**: The judge correctly identified that simply creating classes (`Authentication`, `Validation`) isn't enough if they are all glued together by a "God Object" manager. The Skill model produced a decentralized design, which the judge recognized as superior.

---

## Case 2: The Skill Loses
**Scenario**: A different run of the same `ps-composition-over-coordination` test.

| metric | Baseline (Without Skill) | Skill (With Skill) |
|--------|--------------------------|--------------------|
| **Rating** | **"Outstanding"** | "Good" |
| **Verdict** | True Dependency Injection | Hardcoded Composition |

### Judge's Reasoning
> "Solution A (Baseline) is rated 'outstanding'... it demonstrates mastery by decomposing the system into highly cohesive, loosely coupled components... Solution B (Skill), while good... still maintains some coordination bottlenecks through the PaymentProcessor class."

**The Critical Difference**:
- **Baseline (Winner)**: Used **Dependency Injection** (`constructor(auth, db) { this.auth = auth }`). This allows true composition where parts can be swapped.
- **Skill (Loser)**: Instantiated dependencies *inside* the constructor (`this.auth = new AuthService()`). This is a "hardcoded" composition that mimics the *look* of the pattern but fails the *mechanism*.

### Conclusion
The judge does not blindly prefer the model with the skill. In Case 2, the "With Skill" model followed the *form* of the pattern (creating small units) but failed the *function* (tight coupling). The judge correctly penalized it and awarded the win to the Baseline, which happened to produce a cleaner, more modular architecture.

This proves that our validation suite measures **actual engineering quality**, validating that our skills must genuinely improve the code to earn a passing grade.
