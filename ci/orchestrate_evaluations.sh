#!/bin/bash
set -e

# Orchestrate Evaluations
# 
# Refactored for scalability following programming skills:
# - Policy-Mechanism Separation: Config drives execution
# - Composition Over Coordination: Small focused scripts combined
# - Single Responsibility: Each script does one thing
# - Explicit State Invariants: Configuration validated upfront
# - Single Direction Data Flow: Clear pipeline of operations
#
# This orchestrator:
# 1. Validates configuration
# 2. Detects changed skills
# 3. Generates evaluation matrix from config
# 4. Runs evaluations (parallel or sequential)
# 5. Consolidates results
#
# Usage:
#   ./ci/orchestrate_evaluations.sh <pr_number> [--parallel] [--filter-provider <name>]

PR_NUMBER=$1
shift

PARALLEL=false
FILTER_PROVIDER="all"
THRESHOLD=50

# Parse optional arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --parallel)
            PARALLEL=true
            shift
            ;;
        --filter-provider)
            FILTER_PROVIDER="$2"
            shift 2
            ;;
        --threshold)
            THRESHOLD="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$PR_NUMBER" ]; then
    echo "Error: PR number not provided."
    echo "Usage: $0 <pr_number> [--parallel] [--filter-provider <name>] [--threshold <n>]"
    exit 1
fi

# Validate environment
echo "==> Validating environment"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN not set"
    exit 1
fi

if [ -z "$OLLAMA_API_KEY" ]; then
    echo "⚠ Warning: OLLAMA_API_KEY not set (required for Ollama)"
fi

export GITHUB_TOKEN
export COPILOT_GITHUB_TOKEN="$GITHUB_TOKEN"
export GH_TOKEN="$GITHUB_TOKEN"
export OLLAMA_API_KEY
export PR_NUMBER

echo "✓ Environment configured"

# Detect changes
echo ""
echo "==> Detecting changes"
MODIFIED_SKILLS=$(./ci/detect_changes.sh "$PR_NUMBER")
export MODIFIED_SKILLS

if [ -n "$MODIFIED_SKILLS" ]; then
    echo "✓ Will test skills: $MODIFIED_SKILLS"
else
    echo "✓ Will test all skills"
fi

# Generate matrix from configuration
echo ""
echo "==> Generating evaluation matrix"
MATRIX=$(uv run --with pyyaml ci/matrix_generator.py --filter-provider "$FILTER_PROVIDER")

if [ -z "$MATRIX" ] || [ "$MATRIX" = '{"include": []}' ]; then
    echo "❌ Error: No enabled providers in configuration"
    exit 1
fi

# Extract matrix items
MATRIX_ITEMS=$(echo "$MATRIX" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for item in data['include']:
    print(f\"{item['provider']}|{item['model']}|{item.get('extra_args', '')}\")
")

ITEM_COUNT=$(echo "$MATRIX_ITEMS" | wc -l | xargs)
echo "✓ Generated matrix with $ITEM_COUNT configurations"
echo "$MATRIX_ITEMS" | sed 's/^/  - /'

# Clean previous results
rm -rf tests/results/*
mkdir -p tests/results

# Run evaluations
echo ""
if [ "$PARALLEL" = true ]; then
    echo "==> Running evaluations in parallel"
    
    PIDS=()
    while IFS='|' read -r provider model extra_args; do
        echo "  Starting: $provider/$model"
        ./ci/run_evaluation.sh "$provider" "$model" "$THRESHOLD" "$extra_args" > "tests/results/${provider}_${model//[:\/]/_}.log" 2>&1 &
        PIDS+=($!)
    done <<< "$MATRIX_ITEMS"
    
    # Wait for all background jobs
    FAILED=0
    for pid in "${PIDS[@]}"; do
        if ! wait "$pid"; then
            FAILED=$((FAILED + 1))
        fi
    done
    
    echo "✓ All parallel evaluations completed"
    
    if [ "$FAILED" -gt 0 ]; then
        echo "⚠ $FAILED evaluation(s) reported failures"
    fi
else
    echo "==> Running evaluations sequentially"
    
    while IFS='|' read -r provider model extra_args; do
        ./ci/run_evaluation.sh "$provider" "$model" "$THRESHOLD" "$extra_args"
    done <<< "$MATRIX_ITEMS"
    
    echo "✓ All evaluations completed"
fi

# Consolidate results
echo ""
./ci/consolidate_results.sh

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Orchestration completed successfully"
else
    echo "❌ Orchestration failed"
fi

exit $EXIT_CODE
