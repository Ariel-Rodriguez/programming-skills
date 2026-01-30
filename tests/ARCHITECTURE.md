# Refactored Evaluator - Architecture

This is a complete refactoring of the evaluator applying all programming skills from the `skills/` folder.

## Structure

```
tests/
├── evaluator.py          # Main entry point (Composition Root)
├── domain/              # Functional Core - Pure business logic
│   ├── __init__.py
│   ├── types.py         # Immutable domain types
│   ├── logic.py         # Pure functions (no side effects)
│   ├── skill_extraction.py  # Smart skill guidance extraction
│   └── judging.py       # LLM judge evaluation logic
├── ports/               # Interface definitions
│   ├── __init__.py
│   ├── filesystem.py    # FileSystem port interface
│   └── model.py         # AI Model port interface
├── adapters/            # Imperative Shell - External integrations
│   ├── __init__.py
│   ├── filesystem.py    # Real filesystem adapter
│   ├── ollama.py        # Ollama API adapter
│   └── copilot.py       # Copilot CLI adapter
└── services/            # Application services (orchestration)
    ├── __init__.py
    ├── skill_discovery.py
    ├── test_generation.py
    ├── evaluation.py    # Includes LLM judge integration
    └── reporting.py
```

## Applied Skills

### 1. **Functional Core, Imperative Shell**
- **Core**: `domain/` contains pure functions with no IO
- **Shell**: `adapters/` handle all side effects (file IO, HTTP, subprocess)
- Benefits: Core logic is testable without mocks

### 2. **Explicit State Invariants**
- All domain types use `@dataclass(frozen=True)` for immutability
- States modeled explicitly (e.g., `Success` vs `Failure`, not boolean flags)
- Impossible states are unrepresentable

### 3. **Single Direction Data Flow**
- Data flows: Files → Parsing → Domain Types → Evaluation → Results
- No circular dependencies
- Clear ownership at each layer

### 4. **Local Reasoning**
- All dependencies explicitly injected
- No hidden globals or ambient context
- Function signatures reveal all dependencies

### 5. **Naming as Design**
- Module names reveal purpose: `skill_discovery`, not `utils`
- Function names reveal intent: `evaluate_response_against_expectations`
- No generic "Manager" or "Handler" classes

### 6. **Policy-Mechanism Separation**
- **Policy**: Test priority (test.json > tests.json > markdown)
- **Mechanism**: Generic loading and parsing functions
- Evaluation rules passed as data structures

### 7. **Error Handling Design**
- `Result` type for explicit error handling
- `Success` and `Failure` instead of exceptions
- Errors visible in function signatures

### 8. **Minimize Mutation**
- All domain types immutable (`frozen=True`)
- Functions return new values instead of modifying inputs
- Tuples instead of lists for collections

### 9. **Explicit Boundaries Adapters**
- Domain depends on port interfaces, not implementations
- Adapters implement ports
- Easy to swap implementations (e.g., mock filesystem for testing)

### 10. **Composition Over Coordination**
- Small, focused services
- Each service has one clear responsibility
- No "Manager" classes orchestrating everything

## Usage

From the project root:

```bash
# Run with all skills
uv run --project tests tests/evaluator.py --all

# Run specific skill
uv run --project tests tests/evaluator.py --skill ps-single-direction-data-flow

# Use LLM judge for semantic evaluation (recommended)
uv run --project tests tests/evaluator.py --all --judge --provider copilot --model claude-sonnet-4.5

# Use different provider
uv run --project tests tests/evaluator.py --all --provider copilot --model claude-sonnet-4

# Verbose output
uv run --project tests tests/evaluator.py --all --verbose

# Generate reports
uv run --project tests tests/evaluator.py --all --report --github-comment
```

## Evaluation Modes

### Mechanical Evaluation (Fast)
Uses pattern matching (includes/excludes/regex) to check responses:
```bash
uv run --project tests tests/evaluator.py --all
```

### Semantic Evaluation (Recommended)
Uses LLM judge to evaluate principle adherence with reasoning:
```bash
uv run --project tests tests/evaluator.py --all --judge
```

The judge evaluates:
- Does code follow the principle? (Yes/No/Partial)
- Is it better than baseline? (Better/Same/Worse)
- Quality score (0-100)
- Detailed reasoning

When `--judge` is used, the judge verdict overrides mechanical thresholds.

## Testing Strategy

### Pure Functions (Domain Layer)
Test without any mocks - just pass data:

```python
from domain import parse_skill_frontmatter, Severity

def test_parse_frontmatter():
    content = "---\nseverity: BLOCK\n---\nBody"
    description, severity = parse_skill_frontmatter(content)
    assert severity == Severity.BLOCK
```

### Services
Inject test doubles for ports:

```python
from services import discover_skills

def test_discover_skills():
    mock_fs = MockFileSystem(...)
    skills = discover_skills(Path("skills"), mock_fs)
    assert len(skills) > 0
```

### Adapters
Integration tests with real external systems:

```python
def test_ollama_adapter():
    adapter = OllamaAdapter()
    config = ModelConfig(...)
    result = adapter.call("Hello", config)
    assert isinstance(result, Success)
```

## Benefits of This Architecture

1. **Testability**: Pure functions need no mocks
2. **Maintainability**: Clear separation of concerns
3. **Flexibility**: Swap adapters without changing domain
4. **Clarity**: Explicit dependencies and error handling
5. **Quality**: LLM judge provides semantic evaluation beyond pattern matching

## LLM Judge Integration

The evaluator includes optional semantic evaluation via `--judge` flag:

**Flow:**
1. Run tests baseline (no skill) and with skill
2. Mechanical checks evaluate patterns
3. If `--judge` enabled: LLM evaluates both responses
4. Judge provides verdict + score + reasoning
5. Reports show both mechanical and judge results

**Judge prompt structure:**
```
PRINCIPLE: [skill principle]
INSTRUCTIONS: [key rules]
BASELINE CODE: [without skill]
REFACTORED CODE: [with skill]

Evaluate: follows_principle, vs_baseline, score, reasoning
```

**Benefits:**
- Catches quality improvements mechanical tests miss
- Provides actionable feedback with reasoning
- Reduces false negatives
- Helps refine skill definitions
5. **Safety**: Immutable data prevents bugs
6. **Scalability**: Easy to add new skills, adapters, or services

## What Changed

The original evaluator was a single monolithic file. The refactored version splits it into:

- **Before**: Single 600+ line file with mixed concerns
- **After**: Modular architecture with clear boundaries

The old evaluator (`evaluator_old.py` - kept for reference) had:
- Mixed IO and business logic
- Hidden dependencies (globals, imports inside functions)
- Exceptions for control flow
- Mutable state
- God functions doing everything

The refactored version separates:
- **What to do** (domain logic) from **how to do it** (adapters)
- **Policy** (business rules) from **mechanism** (implementation)
- **Pure** (deterministic) from **impure** (side effects)

## Future Improvements

1. Add more adapters (e.g., OpenAI, Anthropic)
2. Implement caching adapter for model responses
3. Add parallel test execution
4. Create HTML report generator
5. Add CLI for managing skills
