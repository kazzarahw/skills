#!/usr/bin/env python3
"""
Finding ID Generator
Generates unique, sequential finding IDs for security reports.

Supports:
- Web2: WSTG-v42-<CATEGORY>-<NN> format
- Web3: SWC-<NNN> format
- Custom prefixes

Usage:
    python finding-id-generator.py --type web2 --category INPV
    python finding-id-generator.py --type web3
    python finding-id-generator.py --type custom --prefix CUST
    python finding-id-generator.py --type web2 --category AUTH --count 5
    python finding-id-generator.py --list-categories
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

# State file path (persists across runs)
STATE_FILE = Path(__file__).parent / ".finding_id_state.json"

# WSTG v4.2 categories
WSTG_CATEGORIES = {
    "INFO": "Information Gathering",
    "CONF": "Configuration and Deployment Management",
    "IDNT": "Identity Management",
    "AUTH": "Authentication",
    "AUTHZ": "Authorization",
    "SESS": "Session Management",
    "INPV": "Input Validation",
    "ERRH": "Error Handling",
    "CRYP": "Cryptography",
    "BUSL": "Business Logic",
    "CLNT": "Client-side",
    "API": "API Testing",
    "FILE": "File Uploads",
    "CODE": "Code Quality",
}


def load_state() -> dict:
    """Load the current state from the state file."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_state(state: dict) -> None:
    """Save the current state to the state file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)


def get_next_number(state: dict, key: str) -> int:
    """Get the next sequential number for a given key."""
    return state.get(key, 0) + 1


def generate_web2_id(category: str, state: dict) -> str:
    """Generate a WSTG-v42 finding ID."""
    category = category.upper()
    if category not in WSTG_CATEGORIES:
        print(f"Error: Unknown category '{category}'", file=sys.stderr)
        print(f"Valid categories: {', '.join(WSTG_CATEGORIES.keys())}", file=sys.stderr)
        sys.exit(1)

    key = f"WSTG-v42-{category}"
    number = get_next_number(state, key)
    state[key] = number

    return f"WSTG-v42-{category}-{number:02d}"


def generate_web3_id(state: dict) -> str:
    """Generate an SWC finding ID."""
    key = "SWC"
    number = get_next_number(state, key)
    state[key] = number

    return f"SWC-{number:03d}"


def generate_custom_id(prefix: str, state: dict) -> str:
    """Generate a custom prefixed finding ID."""
    key = f"CUSTOM-{prefix}"
    number = get_next_number(state, key)
    state[key] = number

    return f"{prefix}-{number:03d}"


def list_categories() -> None:
    """List all available WSTG categories."""
    print("Available WSTG v4.2 categories:")
    print()
    for code, description in WSTG_CATEGORIES.items():
        print(f"  {code:6s} - {description}")


def show_state() -> None:
    """Show the current state."""
    state = load_state()
    if not state:
        print("No state found. No IDs have been generated yet.")
        return

    print("Current state:")
    print()
    for key, number in sorted(state.items()):
        print(f"  {key}: {number}")


def reset_state() -> None:
    """Reset the state file."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()
        print("State reset. All counters cleared.")
    else:
        print("No state file found.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate unique, sequential finding IDs for security reports.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --type web2 --category INPV
  %(prog)s --type web3
  %(prog)s --type custom --prefix CUST
  %(prog)s --type web2 --category AUTH --count 5
  %(prog)s --list-categories
  %(prog)s --show-state
  %(prog)s --reset-state
        """,
    )

    parser.add_argument(
        "--type",
        choices=["web2", "web3", "custom"],
        help="Type of finding ID to generate",
    )
    parser.add_argument(
        "--category",
        help="WSTG category (required for web2 type)",
    )
    parser.add_argument(
        "--prefix",
        help="Custom prefix (required for custom type)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of IDs to generate (default: 1)",
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List all available WSTG categories",
    )
    parser.add_argument(
        "--show-state",
        action="store_true",
        help="Show the current state",
    )
    parser.add_argument(
        "--reset-state",
        action="store_true",
        help="Reset the state file",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save state (generate IDs without persisting)",
    )

    args = parser.parse_args()

    if args.list_categories:
        list_categories()
        return

    if args.show_state:
        show_state()
        return

    if args.reset_state:
        reset_state()
        return

    if not args.type:
        parser.error("--type is required (unless using --list-categories, --show-state, or --reset-state)")

    state = load_state()

    for _ in range(args.count):
        if args.type == "web2":
            if not args.category:
                parser.error("--category is required for web2 type")
            finding_id = generate_web2_id(args.category, state)
        elif args.type == "web3":
            finding_id = generate_web3_id(state)
        elif args.type == "custom":
            if not args.prefix:
                parser.error("--prefix is required for custom type")
            finding_id = generate_custom_id(args.prefix, state)

        print(finding_id)

    if not args.no_save:
        save_state(state)


if __name__ == "__main__":
    main()
