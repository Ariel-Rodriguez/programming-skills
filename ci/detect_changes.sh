#!/bin/bash
set -e

# detect_changes.sh
# Detects modified skills in a PR.
# Single Responsibility: Only detects changes, doesn't run evaluations.
# Explicit Boundaries: Separates change detection from evaluation logic.

PR_NUMBER=$1

if [ -z "$PR_NUMBER" ]; then
    echo "Error: PR number not provided."
    echo "Usage: $0 <pr_number>"
    exit 1
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN not set"
    exit 1
fi

echo "Detecting modified skills in PR #$PR_NUMBER..."

# Detect modified skills
MODIFIED_FILES=$(gh pr diff "$PR_NUMBER" --name-only)
MODIFIED_SKILLS=$(echo "$MODIFIED_FILES" | grep '^skills/' | cut -d'/' -f2 | sort -u | xargs)

if [ -n "$MODIFIED_SKILLS" ]; then
    echo "Modified skills: $MODIFIED_SKILLS"
    echo "$MODIFIED_SKILLS"
else
    echo "No skills modified - will test all"
    echo ""
fi
