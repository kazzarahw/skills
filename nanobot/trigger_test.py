#!/usr/bin/env python3
"""
Trigger test for skill descriptions.

Tests whether common task phrases would match skill descriptions.
Use this to verify that skill descriptions trigger correctly
for smaller models that need explicit direction.

Usage:
    python3 nanobot/trigger_test.py

Exit code 0 = all tests pass, 1 = some tests fail.
"""

import yaml
import os
import sys

SKILLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'skills')

# Test phrases that should trigger each skill
TRIGGER_TESTS = {
    'security-recon': [
        'scan this network for open ports',
        'recon this target',
        'enumerate subdomains',
        'map the attack surface',
        'what ports are open on this host',
        'discover infrastructure',
    ],
    'security-audit': [
        'review this code for vulnerabilities',
        'audit this configuration',
        'check for security issues in this repo',
        'threat model this system',
        'assess protocol security',
    ],
    'deep-research': [
        'research Rust vs Go',
        'compare these two technologies',
        'investigate this topic in depth',
        'do a deep dive on this',
        'evaluate adoption of this technology',
    ],
    'osint': [
        'investigate this person',
        'who owns this domain',
        'background check this company',
        'is this email real',
        'trace this crypto address',
    ],
    'security-suite': [
        'start a pentest',
        'run a security assessment',
        'begin an engagement',
        'incident response for this breach',
    ],
    'security-exploit': [
        'exploit this vulnerability',
        'validate this finding',
        'demonstrate impact',
        'test remediation',
    ],
    'security-verify': [
        'verify this finding',
        'is this a false positive',
        'confirm this vulnerability',
        'check reproducibility',
    ],
    'security-forensics': [
        'investigate this incident',
        'trace these funds',
        'analyze this breach',
        'post-mortem analysis',
    ],
    'security-report': [
        'write a report',
        'generate a pentest report',
        'document findings',
        'create disclosure documentation',
    ],
}

# Minimum word overlap percentage to consider a trigger match
THRESHOLD = 30


def load_descriptions():
    """Load all skill descriptions from SKILL.md files."""
    descriptions = {}
    for name in sorted(os.listdir(SKILLS_DIR)):
        path = os.path.join(SKILLS_DIR, name, 'SKILL.md')
        if not os.path.isfile(path):
            continue
        with open(path) as f:
            content = f.read()
        if not content.startswith('---'):
            continue
        end = content.find('---', 3)
        if end == -1:
            continue
        try:
            fm = yaml.safe_load(content[3:end])
            descriptions[name] = fm.get('description', '')
        except Exception:
            continue
    return descriptions


def test_trigger(phrase, description):
    """Test if a phrase would trigger a skill based on word overlap."""
    desc_words = set(description.lower().split())
    phrase_words = phrase.lower().split()
    matches = sum(1 for w in phrase_words if w in desc_words)
    return (matches / len(phrase_words)) * 100


def main():
    descriptions = load_descriptions()
    failures = []
    total = 0
    passed = 0

    print('Skill Trigger Test Results')
    print('=' * 70)

    for skill, phrases in TRIGGER_TESTS.items():
        desc = descriptions.get(skill, '')
        if not desc:
            print(f'\n{skill}: SKIPPED (no description found)')
            continue

        print(f'\n{skill}:')
        for phrase in phrases:
            total += 1
            pct = test_trigger(phrase, desc)
            status = 'PASS' if pct >= THRESHOLD else 'FAIL'
            if pct >= THRESHOLD:
                passed += 1
            else:
                failures.append((skill, phrase, pct))
            print(f'  {status} ({pct:5.1f}%) "{phrase}"')

    print('\n' + '=' * 70)
    print(f'Results: {passed}/{total} passed ({passed/total*100:.1f}%)')

    if failures:
        print('\nFailures:')
        for skill, phrase, pct in failures:
            print(f'  - {skill}: "{phrase}" ({pct:.1f}% overlap)')
        sys.exit(1)
    else:
        print('\nAll trigger tests passed!')
        sys.exit(0)


if __name__ == '__main__':
    main()
