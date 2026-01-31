#!/usr/bin/env python3
"""
Parse /test command from GitHub comment.

Supports:
  /test                                    - Auto-detect changed skills
  /test skill ps-error-handling-design    - Override with specific skill
  /test skill skill1 skill2 skill3         - Override with multiple skills
"""

import sys
import re


def parse_command(comment: str) -> list:
    """Parse /test command and extract skills if specified.
    
    Returns list of skill names or empty list for auto-detect.
    """
    
    # Check if /test skill <names> is present
    match = re.search(r'/test\s+skill\s+(.+?)(?:\s*$|\s+\S)', comment)
    
    if match:
        # Extract everything after "/test skill" until end or next word
        skills_str = match.group(1).strip()
        skills = skills_str.split()
        return skills
    
    # No skill override, return empty (will trigger auto-detect)
    return []


def main():
    if len(sys.argv) < 2:
        print("Usage: parse_test_command.py <comment>")
        sys.exit(1)
    
    comment = sys.argv[1]
    skills = parse_command(comment)
    
    if skills:
        print(" ".join(skills))
    else:
        print("")


if __name__ == "__main__":
    main()
