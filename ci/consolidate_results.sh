#!/bin/bash
set -e

# consolidate_results.sh
# Consolidates results from multiple parallel evaluation runs.
# Composition Over Coordination: Aggregates outputs from independent units.
# Single Responsibility: Only consolidates, doesn't evaluate.

RESULTS_BASE="tests/results"

echo "==> Consolidating results from all evaluations"

# Find all result directories
RESULT_DIRS=$(find "$RESULTS_BASE" -type d -name "*" -mindepth 2)

if [ -z "$RESULT_DIRS" ]; then
    echo "No results found in $RESULTS_BASE"
    exit 1
fi

# Check for failures
FAILED=0
SUCCEEDED=0
ALL_RESULTS=""

echo ""
echo "Results by provider/model:"
echo "=========================="

for dir in $RESULT_DIRS; do
    if [ ! -f "$dir/exit_code" ]; then
        continue
    fi
    
    EXIT_CODE=$(cat "$dir/exit_code")
    PROVIDER_MODEL=$(echo "$dir" | sed "s|$RESULTS_BASE/||")
    
    if [ "$EXIT_CODE" -eq 0 ]; then
        echo "✅ $PROVIDER_MODEL - PASSED"
        SUCCEEDED=$((SUCCEEDED + 1))
    else
        echo "❌ $PROVIDER_MODEL - FAILED (exit code: $EXIT_CODE)"
        FAILED=$((FAILED + 1))
    fi
    
    # Collect summary if exists
    if [ -f "$dir/summary.json" ]; then
        ALL_RESULTS="$ALL_RESULTS\n### Results: $PROVIDER_MODEL\n"
        ALL_RESULTS="$ALL_RESULTS$(cat "$dir/summary.json")\n"
    fi
done

echo ""
echo "Summary:"
echo "========"
echo "Succeeded: $SUCCEEDED"
echo "Failed: $FAILED"

# Generate consolidated comment for PR
if [ -n "$PR_NUMBER" ] && [ "$FAILED" -eq 0 ]; then
    echo ""
    echo "Generating consolidated PR comment..."
    
    COMMENT="## 🎉 All Evaluations Passed\n\n"
    COMMENT="${COMMENT}Tested across $SUCCEEDED provider/model combinations.\n\n"
    COMMENT="${COMMENT}${ALL_RESULTS}"
    
    echo -e "$COMMENT" > comment.md
    echo "✓ Consolidated comment saved to comment.md"
fi

# Exit with failure if any evaluation failed
if [ "$FAILED" -gt 0 ]; then
    echo ""
    echo "❌ $FAILED evaluation(s) failed"
    exit 1
fi

echo ""
echo "✅ All evaluations passed"
exit 0
