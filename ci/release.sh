#!/bin/bash
set -e

PLATFORM=$1

if [ -z "$PLATFORM" ]; then
    echo "Usage: $0 <platform>"
    echo "Platforms: cursor-antigravity, copilot"
    exit 1
fi

case $PLATFORM in
    cursor-antigravity)
        echo "Packaging skills for Cursor/Antigravity..."
        cd skills
        zip -r ../cursor-antigravity.zip .
        ;;
    copilot)
        echo "Packaging skills for Copilot..."
        # For Copilot, we need to aggregate all skills into instructions.md
        mkdir -p .github/copilot
        echo "# Programming Skills" > .github/copilot/instructions.md
        echo "" >> .github/copilot/instructions.md
        
        for skill_dir in skills/*/; do
            if [ -f "$skill_dir/SKILL.md" ]; then
                echo "Adding $(basename $skill_dir)..."
                cat "$skill_dir/SKILL.md" >> .github/copilot/instructions.md
                echo "" >> .github/copilot/instructions.md
                echo "---" >> .github/copilot/instructions.md
                echo "" >> .github/copilot/instructions.md
            fi
        done
        
        cd .github
        zip -r ../copilot.zip copilot
        ;;
    *)
        echo "Unknown platform: $PLATFORM"
        exit 1
        ;;
esac

echo "✓ Package created: ${PLATFORM}.zip"
