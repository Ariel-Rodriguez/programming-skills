# Benchmarks

Evaluate how well AI models apply programming principles from this repository using [Upskill](https://github.com/huggingface/upskill).

## Setup

```bash
# Navigate to benchmarks directory
cd benchmarks

# Install dependencies (creates venv automatically)
uv sync

# Start Ollama (for local LLM testing)
ollama serve

# Pull a model
ollama pull llama3.2
```

## Running Benchmarks

```bash
# Check prerequisites
uv run python harness.py --check

# Test all skills with a model
uv run python harness.py --all --model llama3.2:latest

# Test specific skill
uv run python harness.py --skill functional-core-imperative-shell --model llama3.2:latest

# Compare multiple models
uv run python harness.py --all --model llama3.2:latest --model qwen2.5-coder:latest

# Generate report
uv run python harness.py --report
```

## Configuration

Edit `config.yaml` to change models, paths, or benchmark settings.

## Results

Results are saved to `results/` and can be viewed with:

```bash
uv run python harness.py --report
```

## How It Works

The harness dynamically discovers skills from `../skills/` and generates test cases from each skill's content. This means it adapts automatically as skills are added, renamed, or reorganized.
