#!/bin/bash
set -e

# validate_skills.sh
# Detects modified skills in a PR and runs the benchmark harness.

PR_NUMBER=$1
THRESHOLD=${2:-50}

if [ -z "$PR_NUMBER" ]; then
    echo "Error: PR number not provided."
    exit 1
fi

# Ensure GITHUB_TOKEN is available for subprocess
if [ -n "$GITHUB_TOKEN" ]; then
    export GITHUB_TOKEN
    export COPILOT_GITHUB_TOKEN="$GITHUB_TOKEN"
    export GH_TOKEN="$GITHUB_TOKEN"
    
    # Authenticate GitHub CLI (required for Copilot CLI)
    echo "$GITHUB_TOKEN" | gh auth login --with-token
    
    echo "✓ GitHub token configured for Copilot CLI"
else
    echo "⚠ Warning: GITHUB_TOKEN not set in environment"
fi

echo "Checking for modified skills in PR #$PR_NUMBER..."

# Detect modified skills
MODIFIED_FILES=$(gh pr diff "$PR_NUMBER" --name-only)
MODIFIED_SKILLS=$(echo "$MODIFIED_FILES" | grep '^skills/' | cut -d'/' -f2 | sort -u | xargs)

# Build command array
CMD=("uv" "run" "--project" "tests" "tests/evaluator.py" "--provider" "copilot" "--model" "claude-sonnet-4.5" "--threshold" "$THRESHOLD" "--report" "--github-comment" "--judge" "--verbose")

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
