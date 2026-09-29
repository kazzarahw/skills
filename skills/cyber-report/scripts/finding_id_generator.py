#!/usr/bin/env python3
"""
finding_id_generator.py - Finding ID Generator

Generates unique, sequential finding IDs for penetration test reports.
Supports WSTG (Web Security Testing Guide) categories and maintains
state persistence across multiple invocations.

Usage:
    python3 finding_id_generator.py --category auth --count 5
    python3 finding_id_generator.py --category auth --next
    python3 finding_id_generator.py --list-categories
    python3 finding_id_generator.py --reset --category auth

ID Format: {CATEGORY_PREFIX}-{SEQUENCE:04d}
Example: AUTH-0001, AUTH-0002, INFO-0001

Exit Codes:
    0   Success
    1   Error
    2   Invalid arguments
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# =============================================================================
# CATEGORY MAP
# =============================================================================

CATEGORY_MAP = {
    # WSTG Categories
    "info": {"prefix": "INFO", "description": "Information Gathering"},
    "config": {"prefix": "CONF", "description": "Configuration and Deployment Management"},
    "auth": {"prefix": "AUTH", "description": "Authentication Testing"},
    "authz": {"prefix": "AUTHZ", "description": "Authorization Testing"},
    "session": {"prefix": "SESS", "description": "Session Management Testing"},
    "input": {"prefix": "INPT", "description": "Input Validation Testing"},
    "error": {"prefix": "ERR", "description": "Error Handling Testing"},
    "crypto": {"prefix": "CRYP", "description": "Cryptography Testing"},
    "business": {"prefix": "BUS", "description": "Business Logic Testing"},
    "client": {"prefix": "CLNT", "description": "Client-Side Testing"},
    "api": {"prefix": "API", "description": "API Testing"},
    "network": {"prefix": "NET", "description": "Network Security Testing"},
    "infra": {"prefix": "INFR", "description": "Infrastructure Testing"},
    "mobile": {"prefix": "MOB", "description": "Mobile Application Testing"},
    "social": {"prefix": "SOC", "description": "Social Engineering"},
    "physical": {"prefix": "PHY", "description": "Physical Security"},
    "doc": {"prefix": "DOC", "description": "Documentation and Reporting"},
    "other": {"prefix": "OTHR", "description": "Other"},
}

# Severity to category mapping hints
SEVERITY_CATEGORY_HINTS = {
    "critical": ["auth", "authz", "input", "business"],
    "high": ["auth", "authz", "input", "session", "crypto"],
    "medium": ["config", "input", "session", "client", "api"],
    "low": ["config", "info", "error", "doc"],
    "info": ["info", "doc"],
}


# =============================================================================
# STATE MANAGEMENT
# =============================================================================

DEFAULT_STATE_DIR = os.path.expanduser("~/.cyber-skills/finding-ids")
DEFAULT_STATE_FILE = "finding-ids.json"


@dataclass
class FindingIDState:
    """State for the finding ID generator."""
    sequences: Dict[str, int] = field(default_factory=dict)
    created_at: str = ""
    last_updated: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat() + "Z"
        self.last_updated = datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> dict:
        return {
            "sequences": self.sequences,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FindingIDState":
        return cls(
            sequences=data.get("sequences", {}),
            created_at=data.get("created_at", ""),
            last_updated=data.get("last_updated", ""),
        )


# =============================================================================
# GENERATOR CLASS
# =============================================================================

class FindingIDGenerator:
    """
    Generates unique, sequential finding IDs.
    
    Maintains state persistence to ensure IDs remain unique across
    multiple invocations and report generation sessions.
    
    Example:
        >>> generator = FindingIDGenerator()
        >>> generator.generate_id("auth")
        'AUTH-0001'
        >>> generator.generate_id("auth")
        'AUTH-0002'
        >>> generator.generate_id("info")
        'INFO-0001'
    """
    
    def __init__(self, state_file: Optional[str] = None):
        """
        Initialize the generator with optional state file.
        
        Args:
            state_file: Path to state file (default: ~/.cyber-skills/finding-ids/finding-ids.json)
        """
        if state_file is None:
            state_dir = os.environ.get("FINDING_ID_STATE_DIR", DEFAULT_STATE_DIR)
            state_file = os.path.join(state_dir, DEFAULT_STATE_FILE)
        
        self.state_file = state_file
        self.state = self._load_state()
    
    def _load_state(self) -> FindingIDState:
        """Load state from file or create new state."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                return FindingIDState.from_dict(data)
            except (json.JSONDecodeError, IOError):
                pass
        return FindingIDState()
    
    def _save_state(self):
        """Save current state to file."""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        self.state.last_updated = datetime.utcnow().isoformat() + "Z"
        with open(self.state_file, 'w') as f:
            json.dump(self.state.to_dict(), f, indent=2)
    
    def _get_prefix(self, category: str) -> str:
        """Get the prefix for a category."""
        category = category.lower().strip()
        if category in CATEGORY_MAP:
            return CATEGORY_MAP[category]["prefix"]
        # Generate prefix from category name
        return category[:4].upper()
    
    def generate_id(self, category: str) -> str:
        """
        Generate a new finding ID for the given category.
        
        Args:
            category: The finding category (e.g., "auth", "input", "info")
        
        Returns:
            A unique finding ID string (e.g., "AUTH-0001")
        
        Raises:
            ValueError: If category is empty or invalid
        """
        if not category or not category.strip():
            raise ValueError("Category cannot be empty")
        
        category = category.lower().strip()
        prefix = self._get_prefix(category)
        
        # Get current sequence for this category
        current_seq = self.state.sequences.get(category, 0)
        new_seq = current_seq + 1
        
        # Update state
        self.state.sequences[category] = new_seq
        self._save_state()
        
        # Format ID with zero-padding
        return f"{prefix}-{new_seq:04d}"
    
    def get_next_id(self, category: str) -> str:
        """
        Preview the next ID without consuming it.
        
        Args:
            category: The finding category
        
        Returns:
            The next ID that would be generated (e.g., "AUTH-0003")
        """
        if not category or not category.strip():
            raise ValueError("Category cannot be empty")
        
        category = category.lower().strip()
        prefix = self._get_prefix(category)
        current_seq = self.state.sequences.get(category, 0)
        next_seq = current_seq + 1
        
        return f"{prefix}-{next_seq:04d}"
    
    def generate_batch(self, category: str, count: int) -> List[str]:
        """
        Generate multiple finding IDs at once.
        
        Args:
            category: The finding category
            count: Number of IDs to generate
        
        Returns:
            List of finding ID strings
        """
        if count < 1:
            raise ValueError("Count must be at least 1")
        
        return [self.generate_id(category) for _ in range(count)]
    
    def get_sequence(self, category: str) -> int:
        """Get the current sequence number for a category."""
        category = category.lower().strip()
        return self.state.sequences.get(category, 0)
    
    def reset_category(self, category: str):
        """Reset the sequence for a category to 0."""
        category = category.lower().strip()
        self.state.sequences[category] = 0
        self._save_state()
    
    def reset_all(self):
        """Reset all sequences to 0."""
        self.state.sequences = {}
        self._save_state()
    
    def get_stats(self) -> dict:
        """Get statistics about generated IDs."""
        return {
            "total_categories": len(self.state.sequences),
            "total_ids_generated": sum(self.state.sequences.values()),
            "sequences": dict(self.state.sequences),
            "state_file": self.state_file,
            "created_at": self.state.created_at,
            "last_updated": self.state.last_updated,
        }
    
    def list_categories(self) -> dict:
        """List all available categories with their prefixes."""
        return {
            cat: {
                "prefix": info["prefix"],
                "description": info["description"],
                "current_sequence": self.state.sequences.get(cat, 0),
            }
            for cat, info in CATEGORY_MAP.items()
        }


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate unique, sequential finding IDs for penetration test reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a single ID
  %(prog)s --category auth

  # Generate multiple IDs
  %(prog)s --category input --count 5

  # Preview next ID without consuming it
  %(prog)s --category auth --next

  # List all categories
  %(prog)s --list-categories

  # Show statistics
  %(prog)s --stats

  # Reset a category
  %(prog)s --reset --category auth

  # Use custom state file
  %(prog)s --category auth --state-file /tmp/my-ids.json
        """
    )
    
    parser.add_argument(
        "--category", "-c",
        type=str,
        help="Finding category (e.g., auth, input, info)"
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=1,
        help="Number of IDs to generate (default: 1)"
    )
    parser.add_argument(
        "--next",
        action="store_true",
        help="Preview next ID without consuming it"
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List all available categories"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show generator statistics"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset sequence for the specified category"
    )
    parser.add_argument(
        "--reset-all",
        action="store_true",
        help="Reset all sequences"
    )
    parser.add_argument(
        "--state-file",
        type=str,
        help="Path to state file (default: ~/.cyber-skills/finding-ids/finding-ids.json)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = FindingIDGenerator(state_file=args.state_file)
    
    # Handle list categories
    if args.list_categories:
        categories = generator.list_categories()
        if args.json:
            print(json.dumps(categories, indent=2))
        else:
            print("\nAvailable Categories:")
            print("-" * 70)
            print(f"{'Category':<12} {'Prefix':<8} {'Seq':<6} {'Description'}")
            print("-" * 70)
            for cat, info in categories.items():
                print(f"{cat:<12} {info['prefix']:<8} {info['current_sequence']:<6} {info['description']}")
            print("-" * 70)
        return 0
    
    # Handle stats
    if args.stats:
        stats = generator.get_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("\nGenerator Statistics:")
            print("-" * 40)
            print(f"State file: {stats['state_file']}")
            print(f"Total categories: {stats['total_categories']}")
            print(f"Total IDs generated: {stats['total_ids_generated']}")
            print(f"Created: {stats['created_at']}")
            print(f"Last updated: {stats['last_updated']}")
            if stats['sequences']:
                print("\nSequences:")
                for cat, seq in sorted(stats['sequences'].items()):
                    print(f"  {cat}: {seq}")
        return 0
    
    # Handle reset
    if args.reset_all:
        generator.reset_all()
        print("All sequences reset to 0")
        return 0
    
    if args.reset:
        if not args.category:
            print("Error: --category required for --reset", file=sys.stderr)
            return 2
        generator.reset_category(args.category)
        print(f"Reset sequence for category '{args.category}'")
        return 0
    
    # Handle next ID preview
    if args.next:
        if not args.category:
            print("Error: --category required for --next", file=sys.stderr)
            return 2
        next_id = generator.get_next_id(args.category)
        if args.json:
            print(json.dumps({"next_id": next_id, "category": args.category}))
        else:
            print(next_id)
        return 0
    
    # Handle ID generation
    if not args.category:
        print("Error: --category is required", file=sys.stderr)
        return 2
    
    # Validate category
    category = args.category.lower().strip()
    if category not in CATEGORY_MAP:
        print(f"Warning: Unknown category '{category}'. Using generated prefix.", file=sys.stderr)
    
    # Generate IDs
    try:
        if args.count == 1:
            finding_id = generator.generate_id(category)
            if args.json:
                print(json.dumps({"id": finding_id, "category": category}))
            else:
                print(finding_id)
        else:
            ids = generator.generate_batch(category, args.count)
            if args.json:
                print(json.dumps({"ids": ids, "category": category, "count": len(ids)}))
            else:
                for fid in ids:
                    print(fid)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
