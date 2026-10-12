#!/usr/bin/env python3
"""Validate a skill without relying on a particular agent's home directory."""
import re
import sys
from pathlib import Path

import yaml


def validate_skill(directory):
    path = Path(directory) / 'SKILL.md'
    if not path.is_file():
        return False, 'SKILL.md not found'
    text = path.read_text(encoding='utf-8')
    match = re.match(r'\A---\n(.*?)\n---(?:\n|$)', text, re.S)
    if not match:
        return False, 'Missing or invalid YAML frontmatter'
    try:
        data = yaml.safe_load(match[1])
    except yaml.YAMLError:
        return False, 'Invalid YAML frontmatter'
    if not isinstance(data, dict):
        return False, 'Frontmatter must be a mapping'
    if set(data) - {'name', 'description', 'license', 'allowed-tools', 'metadata'}:
        return False, 'Unexpected frontmatter properties'
    name = data.get('name')
    if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64:
        return False, 'Name must be nonempty hyphen-case, at most 64 characters'
    description = data.get('description')
    if not isinstance(description, str) or not description.strip() or len(description.strip()) > 1024:
        return False, 'Description must be nonempty text, at most 1024 characters'
    if '<' in description or '>' in description or description.strip().startswith('[TODO:'):
        return False, 'Description contains angle brackets or an unfinished placeholder'
    fence = None
    for line in text[match.end():].splitlines():
        marker = re.match(r'^[ \t]*(?:(?:[-+*]|\d+[.)])[ \t]+)?(`{3,}|~{3,})(.*)$', line)
        if marker:
            if fence is None:
                fence = marker[1]
            elif marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if fence is None and re.fullmatch(r'[ ]{0,3}\[TODO:[^\n]*\][ \t]*', line):
            return False, 'Skill contains an unfinished placeholder'
    return True, 'PASS: skill structure'


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: python scripts/check_skill.py <skill_directory>')
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
