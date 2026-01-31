#!/bin/bash
set -e

# run_evaluation.sh
# Executes evaluation for a single provider/model combination.
# Policy-Mechanism Separation: Configuration passed as parameters.
# Single Responsibility: Only runs evaluation, doesn't detect or orchestrate.

PROVIDER=$1
MODEL=$2
THRESHOLD=${3:-50}
EXTRA_ARGS=${4:-""}

if [ -z "$PROVIDER" ] || [ -z "$MODEL" ]; then
    echo "Usage: $0 <provider> <model> [threshold] [extra_args]"
    exit 1
fi

# Explicit environment configuration
if [ -n "$GITHUB_TOKEN" ]; then
    export GITHUB_TOKEN
    export COPILOT_GITHUB_TOKEN="$GITHUB_TOKEN"
    export GH_TOKEN="$GITHUB_TOKEN"
fi

if [ -n "$OLLAMA_API_KEY" ]; then
    export OLLAMA_API_KEY
fi

# Results directory per provider/model for parallel execution
RESULTS_DIR="tests/results/${PROVIDER}/${MODEL//[:\/]/_}"
mkdir -p "$RESULTS_DIR"

echo "==> Running evaluation: $PROVIDER/$MODEL"
echo "    Results: $RESULTS_DIR"
echo "    Threshold: $THRESHOLD"

# Detect skills to test (passed via environment or default to all)
SKILL_ARGS=()
if [ -n "$MODIFIED_SKILLS" ]; then
    for skill in $MODIFIED_SKILLS; do
        SKILL_ARGS+=("--skill" "$skill")
    done
else
    SKILL_ARGS+=("--all")
fi

# Build command - Explicit State Invariants: All parameters explicit
CMD=(
    "uv" "run" "--project" "tests"
    "tests/evaluator.py"
    "--provider" "$PROVIDER"
    "--model" "$MODEL"
    "--threshold" "$THRESHOLD"
    "--results-dir" "$RESULTS_DIR"
    "--report"
    "--judge"
    "--verbose"
)

# Add extra args if provided
if [ -n "$EXTRA_ARGS" ]; then
    read -ra EXTRA_ARRAY <<< "$EXTRA_ARGS"
    CMD+=("${EXTRA_ARRAY[@]}")
fi

# Add skill arguments
CMD+=("${SKILL_ARGS[@]}")

# Execute
echo "Executing: ${CMD[*]}"
"${CMD[@]}"

EXIT_CODE=$?

# Save exit code for consolidation
echo "$EXIT_CODE" > "$RESULTS_DIR/exit_code"

exit $EXIT_CODE
