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

echo "Checking for modified skills in PR #$PR_NUMBER..."

# Detect modified skills
MODIFIED_FILES=$(gh pr diff "$PR_NUMBER" --name-only)
MODIFIED_SKILLS=$(echo "$MODIFIED_FILES" | grep '^skills/' | cut -d'/' -f2 | sort -u | xargs)

# Build command array
CMD=("uv" "run" "--project" "tests" "tests/evaluator.py" "--provider" "copilot" "--model" "claude-sonnet-4.5" "--threshold" "$THRESHOLD" "--report" "--github-comment" "--judge")

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
