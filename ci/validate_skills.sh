#!/bin/bash
set -e

# validate_skills.sh
# Detects modified skills in a PR and runs the benchmark harness.

PR_NUMBER=$1
THRESHOLD=${2:-50}
PROVIDER=${3:-"ollama"}  # Default to ollama
OLLAMA_MODEL=${4:-"rnj-1:8b-cloud"}

if [ -z "$PR_NUMBER" ]; then
    echo "Error: PR number not provided."
    exit 1
fi

# Ensure GitHub tokens are available
if [ -n "$GITHUB_TOKEN" ]; then
    export GITHUB_TOKEN
    export COPILOT_GITHUB_TOKEN="$GITHUB_TOKEN"
    export GH_TOKEN="$GITHUB_TOKEN"
    echo "✓ GitHub tokens exported to environment"
else
    echo "⚠ Warning: GITHUB_TOKEN not set in environment"
fi

# Ensure Ollama API key is available for cloud access
if [ -n "$OLLAMA_API_KEY" ]; then
    export OLLAMA_API_KEY
    echo "✓ Ollama API key configured for cloud access"
else
    echo "⚠ Warning: OLLAMA_API_KEY not set (required for Ollama Cloud)"
fi

echo "Checking for modified skills in PR #$PR_NUMBER..."

# Detect modified skills
MODIFIED_FILES=$(gh pr diff "$PR_NUMBER" --name-only)
MODIFIED_SKILLS=$(echo "$MODIFIED_FILES" | grep '^skills/' | cut -d'/' -f2 | sort -u | xargs)

# Build command based on provider
if [ "$PROVIDER" = "ollama" ]; then
    if [ -z "$OLLAMA_API_KEY" ]; then
        echo "❌ Error: OLLAMA_API_KEY not set. Cannot use Ollama Cloud."
        exit 1
    fi
    echo "Using Ollama Cloud $OLLAMA_MODEL"
    # Explicitly pass environment variables to uv run
    CMD=("env" "OLLAMA_API_KEY=$OLLAMA_API_KEY" "uv" "run" "--project" "tests" "tests/evaluator.py" "--provider" "ollama" "--model" "$OLLAMA_MODEL" "--ollama-cloud" "--threshold" "$THRESHOLD" "--report" "--github-comment" "--judge" "--verbose")
elif [ "$PROVIDER" = "copilot" ]; then
    echo "Using Copilot CLI (claude-sonnet-4.5)"
    CMD=("uv" "run" "--project" "tests" "tests/evaluator.py" "--provider" "copilot" "--model" "claude-sonnet-4.5" "--threshold" "$THRESHOLD" "--report" "--github-comment" "--judge" "--verbose")
elif [ "$PROVIDER" = "all" ]; then
    echo "Testing with all providers (not yet implemented - using ollama)"
    CMD=("uv" "run" "--project" "tests" "tests/evaluator.py" "--provider" "ollama" "--model" "$OLLAMA_MODEL" "--ollama-cloud" "--threshold" "$THRESHOLD" "--report" "--github-comment" "--judge" "--verbose")
else
    echo "Unknown provider: $PROVIDER (using ollama)"
    CMD=("uv" "run" "--project" "tests" "tests/evaluator.py" "--provider" "ollama" "--model" "$OLLAMA_MODEL" "--ollama-cloud" "--threshold" "$THRESHOLD" "--report" "--github-comment" "--judge" "--verbose")
fi

if [ -n "$MODIFIED_SKILLS" ]; then
    echo "Detected modified skills: $MODIFIED_SKILLS"
    for skill in $MODIFIED_SKILLS; do
        CMD+=("--skill" "$skill")
    done
else
    echo "No specific skills modified. Running all skills as fallback."
    CMD+=("--all")
fi

# Execute
echo "Executing: ${CMD[*]}"
"${CMD[@]}"

# Debug output on failure
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "============================================"
    echo "DEBUG: Evaluation failed. Showing details:"
    echo "============================================"
    
    if [ -f "tests/results/summary.json" ]; then
        echo ""
        echo "--- tests/results/summary.json ---"
        cat tests/results/summary.json
    fi
    
    if [ -f "comment.md" ]; then
        echo ""
        echo "--- comment.md ---"
        cat comment.md
    fi
fi

exit $EXIT_CODE
