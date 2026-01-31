#!/bin/bash
set -e

echo "Collecting artifacts..."
find artifacts -name "*.zip" -exec mv {} . \;

echo "✓ Artifacts collected:"
ls -lh *.zip
