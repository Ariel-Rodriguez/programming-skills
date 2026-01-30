# Tests / Benchmarks

Evaluate how well AI models apply programming principles from this repository.

**Architecture Note:** This evaluator has been completely refactored to demonstrate all programming skills from the `skills/` folder. See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design documentation.

## Modular Structure

```
tests/
├── evaluator.py          # Main entry point
├── domain/              # Pure business logic (no IO)
├── ports/               # Interface definitions
├── adapters/            # External system implementations
└── services/            # Application orchestration
```

## Setup

```bash
# Navigate to tests directory
cd tests

# Install dependencies (creates .venv automatically)
uv sync

# Start Ollama (for local LLM testing)
ollama serve

# Pull a model
ollama pull llama3.2
```

## Running Evaluations

### Basic Usage

```bash
# Test all skills with a model
uv run python evaluator.py --all --model llama3.2:latest

# Test specific skill
uv run python evaluator.py --skill ps-functional-core-imperative-shell --model llama3.2:latest

# Use Copilot provider
uv run python evaluator.py --all --provider copilot --model claude-sonnet-4

# Verbose output
uv run python evaluator.py --all --verbose
```

### Evaluation Modes

#### 🤖 Semantic Evaluation (Recommended)

Use `--judge` to enable **LLM-as-judge** for semantic code quality evaluation:

```bash
# Semantic evaluation with reasoning
uv run python evaluator.py \
  --skill ps-composition-over-coordination \
  --provider copilot \
  --model claude-sonnet-4.5 \
  --judge \
  --verbose
```

**Benefits:**
- ✅ Evaluates principle adherence, not just syntax
- ✅ Provides detailed reasoning for decisions
- ✅ Reduces false negatives (good code failing mechanical tests)
- ✅ Better PR feedback with explanations

**Output includes:**
- Judge verdict: Better/Same/Worse vs baseline
- Quality score: 0-100
- Reasoning: Why the code passes/fails

#### ⚙️ Mechanical Evaluation (Fast)

Without `--judge`, uses pattern matching (includes/excludes/regex):

```bash
# Fast mechanical checks only
uv run python evaluator.py --all --model llama3.2:latest
```

**Use when:**
- Quick validation needed
- Testing infrastructure changes
- Judge would add unnecessary cost

### Report Generation

```bash
# Console report
uv run python evaluator.py --report

# GitHub PR comment
uv run python evaluator.py --github-comment

# Both
uv run python evaluator.py --report --github-comment
```

### Thresholds

```bash
# Fail if skills don't meet 70% improvement
uv run python evaluator.py --all --threshold 70

# With judge, threshold applies to judge verdict
uv run python evaluator.py --all --judge --threshold 70
```

## Configuration

Edit `config.yaml` to change models, paths, or benchmark settings.

## Results

Results are saved to `results/summary.json` and include:

**Standard Metrics:**
- Baseline pass rate (without skill guidance)
- Skill pass rate (with skill guidance)
- Improvement percentage

**Judge Metrics (with `--judge`):**
- Follows principle: Yes/No/Partial
- vs Baseline: Better/Same/Worse
- Quality score: 0-100
- Reasoning: Detailed explanation

View reports with:

```bash
# Console table
uv run python evaluator.py --report

# GitHub PR format
cat comment.md
```

## How It Works

### Test Generation
The harness dynamically discovers skills from `../skills/` and generates test cases from each skill's content. This means it adapts automatically as skills are added, renamed, or reorganized.

### Evaluation Pipeline
1. **Discovery**: Find skills in `skills/` directory
2. **Test Generation**: Create test cases from skill definitions
3. **Baseline Run**: Execute tests without skill guidance
4. **Skill Run**: Execute tests with skill instruction prepended
5. **Mechanical Check**: Pattern matching (includes/excludes/regex)
6. **Judge Evaluation** (optional): LLM assesses code quality semantically
7. **Reporting**: Generate console/PR reports with results

### LLM Judge (Semantic Evaluation)

When `--judge` is enabled, an LLM evaluates code quality beyond mechanical checks:

**Judge Prompt:**
```
PRINCIPLE: [skill principle]
INSTRUCTIONS: [key skill rules]
BASELINE CODE: [without skill]
REFACTORED CODE: [with skill]

Evaluate:
1. Does refactored code follow the principle?
2. Is it better than baseline?
3. Quality score (0-100)
4. Reasoning
```

**Judge Response:**
```json
{
  "follows_principle": "Yes",
  "vs_baseline": "Better",
  "score": 88,
  "reasoning": "The refactored code demonstrates..."
}
```

**Decision Logic:**
- If judge available: Use verdict (score ≥ 70 + Better = Pass)
- Otherwise: Use mechanical threshold

See [LLM_JUDGE_IMPLEMENTATION.md](LLM_JUDGE_IMPLEMENTATION.md) for full details.
