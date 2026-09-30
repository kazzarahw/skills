#!/usr/bin/env python3
"""
finding-id-generator.py

Generates unique, sequential finding IDs for security audit reports.
Supports web2 (WSTG-v42-CATEGORY-NN) and web3 (SWC-NNN) formats.
Persists state across runs.

Usage:
    python finding-id-generator.py [OPTIONS] <command>

Commands:
    next              Generate next finding ID
    reserve <count>   Reserve a range of finding IDs
    list              List all generated finding IDs
    reset             Reset the counter (use with caution)
    status            Show current status

Options:
    -t, --type <web2|web3>     Finding type (default: web2)
    -c, --category <category>   Category code (e.g., AUTH, XSS, SQLI)
    -s, --state <file>          State file path (default: .finding-ids.json)
    -p, --prefix <prefix>       Custom prefix (overrides type default)
    --start <number>            Starting number (default: 1)
    -v, --verbose               Verbose output
    -h, --help                  Show this help message

Examples:
    python finding-id-generator.py next
    python finding-id-generator.py -t web3 -c SWC-107 next
    python finding-id-generator.py -t web2 -c AUTH next
    python finding-id-generator.py reserve 10
    python finding-id-generator.py list
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# ─── Category Mappings ───────────────────────────────────────────────────────

# Web2 categories based on WSTG-v42
WEB2_CATEGORIES = {
    "AUTH": "Authentication",
    "AUTHZ": "Authorization",
    "SESS": "Session Management",
    "INPV": "Input Validation",
    "ERRH": "Error Handling",
    "CRYP": "Cryptography",
    "BUSL": "Business Logic",
    "CONF": "Configuration",
    "DEPN": "Dependencies",
    "LOGG": "Logging",
    "SSRF": "Server-Side Request Forgery",
    "XSS": "Cross-Site Scripting",
    "SQLI": "SQL Injection",
    "CMDI": "Command Injection",
    "PATH": "Path Traversal",
    "XXE": "XML External Entity",
    "CSRF": "Cross-Site Request Forgery",
    "CLIK": "Clickjacking",
    "CORS": "CORS Misconfiguration",
    "FILE": "File Upload",
    "REDIR": "Open Redirect",
    "API": "API Security",
    "MOB": "Mobile Security",
    "CLOUD": "Cloud Security",
    "CONTAINER": "Container Security",
    "K8S": "Kubernetes Security",
    "IAC": "Infrastructure as Code",
    "SECRETS": "Secrets Management",
    "NET": "Network Security",
    "DNS": "DNS Security",
    "MAIL": "Email Security",
    "BACKUP": "Backup Security",
    "MON": "Monitoring",
    "INC": "Incident Response",
    "COMPLIANCE": "Compliance",
    "PRIV": "Privacy",
    "OTHER": "Other",
}

# Web3 categories based on SWC Registry
WEB3_CATEGORIES = {
    "SWC-100": "Function Default Visibility",
    "SWC-101": "Integer Overflow and Underflow",
    "SWC-102": "Outdated Compiler Version",
    "SWC-103": "Floating Pragma",
    "SWC-104": "Unchecked Call Return Value",
    "SWC-105": "Unprotected Ether Withdrawal",
    "SWC-106": "Unprotected SELFDESTRUCT Instruction",
    "SWC-107": "Reentrancy",
    "SWC-108": "State Variable Default Visibility",
    "SWC-109": "Uninitialized Storage Pointer",
    "SWC-110": "Assert Violation",
    "SWC-111": "Use of Deprecated Solidity Functions",
    "SWC-112": "Delegatecall to Untrusted Callee",
    "SWC-113": "DoS with Failed Call",
    "SWC-114": "Transaction Order Dependence",
    "SWC-115": "Authorization through tx.origin",
    "SWC-116": "Timestamp Dependence",
    "SWC-117": "Signature Malleability",
    "SWC-118": "Incorrect Constructor Name",
    "SWC-119": "Shadowing State Variables",
    "SWC-120": "Weak Sources of Randomness from Chain Attributes",
    "SWC-121": "Missing Protection against Signature Replay Attacks",
    "SWC-122": "Lack of Proper Signature Verification",
    "SWC-123": "Requirement Violation",
    "SWC-124": "Write to Arbitrary Storage Location",
    "SWC-125": "Incorrect Inheritance Order",
    "SWC-126": "Insufficient Gas Griefing",
    "SWC-127": "Arbitrary Jump with Function Type Variable",
    "SWC-128": "DoS with Block Gas Limit",
    "SWC-129": "Typographical Error",
    "SWC-130": "Right-To-Left-Override Control Character",
    "SWC-131": "Presence of Unused Variables",
    "SWC-132": "Unexpected Ether Balance",
    "SWC-133": "Hash Collisions with Multiple Variable Length Arguments",
    "SWC-134": "Message Call with Hardcoded Gas Amount",
    "SWC-135": "Code With No Effects",
    "SWC-136": "Unencrypted Private Data On-Chain",
}


# ─── State Management ────────────────────────────────────────────────────────

class FindingIdState:
    """Manages finding ID state persistence."""
    
    def __init__(self, state_file: str):
        self.state_file = state_file
        self.state = self._load()
    
    def _load(self) -> Dict:
        """Load state from file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {
            "counters": {},
            "findings": [],
            "metadata": {
                "created": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        }
    
    def _save(self):
        """Save state to file."""
        os.makedirs(os.path.dirname(self.state_file) or '.', exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def get_next_id(self, prefix: str, category: str, start: int = 1) -> str:
        """Generate next finding ID."""
        key = f"{prefix}-{category}"
        
        if key not in self.state["counters"]:
            self.state["counters"][key] = {
                "next": start,
                "prefix": prefix,
                "category": category
            }
        
        counter = self.state["counters"][key]["next"]
        self.state["counters"][key]["next"] += 1
        
        finding_id = f"{prefix}-{category}-{counter:03d}"
        
        self.state["findings"].append({
            "id": finding_id,
            "prefix": prefix,
            "category": category,
            "number": counter,
            "created": datetime.utcnow().isoformat()
        })
        
        self._save()
        return finding_id
    
    def reserve_range(self, prefix: str, category: str, count: int, start: int = 1) -> List[str]:
        """Reserve a range of finding IDs."""
        key = f"{prefix}-{category}"
        
        if key not in self.state["counters"]:
            self.state["counters"][key] = {
                "next": start,
                "prefix": prefix,
                "category": category
            }
        
        counter = self.state["counters"][key]["next"]
        self.state["counters"][key]["next"] += count
        
        finding_ids = []
        for i in range(count):
            finding_id = f"{prefix}-{category}-{counter + i:03d}"
            finding_ids.append(finding_id)
            self.state["findings"].append({
                "id": finding_id,
                "prefix": prefix,
                "category": category,
                "number": counter + i,
                "created": datetime.utcnow().isoformat()
            })
        
        self._save()
        return finding_ids
    
    def list_findings(self) -> List[Dict]:
        """List all generated finding IDs."""
        return self.state["findings"]
    
    def reset(self):
        """Reset all counters."""
        self.state = {
            "counters": {},
            "findings": [],
            "metadata": {
                "created": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "reset": True
            }
        }
        self._save()
    
    def get_status(self) -> Dict:
        """Get current status."""
        return {
            "total_findings": len(self.state["findings"]),
            "counters": self.state["counters"],
            "state_file": self.state_file
        }


# ─── ID Generator ────────────────────────────────────────────────────────────

class FindingIdGenerator:
    """Generates finding IDs for security audit reports."""
    
    def __init__(self, state_file: str = ".finding-ids.json"):
        self.state = FindingIdState(state_file)
    
    def generate(
        self,
        finding_type: str = "web2",
        category: str = "OTHER",
        prefix: Optional[str] = None,
        start: int = 1
    ) -> str:
        """Generate a single finding ID."""
        
        # Determine prefix
        if prefix:
            pass
        elif finding_type == "web2":
            prefix = "WSTG-v42"
        elif finding_type == "web3":
            prefix = "SWC"
        else:
            prefix = "FIND"
        
        # Validate category
        if finding_type == "web2":
            category = category.upper()
            if category not in WEB2_CATEGORIES:
                print(f"Warning: Unknown web2 category '{category}'", file=sys.stderr)
        elif finding_type == "web3":
            if category not in WEB3_CATEGORIES:
                print(f"Warning: Unknown web3 category '{category}'", file=sys.stderr)
        
        return self.state.get_next_id(prefix, category, start)
    
    def reserve(
        self,
        count: int,
        finding_type: str = "web2",
        category: str = "OTHER",
        prefix: Optional[str] = None,
        start: int = 1
    ) -> List[str]:
        """Reserve a range of finding IDs."""
        
        if prefix:
            pass
        elif finding_type == "web2":
            prefix = "WSTG-v42"
        elif finding_type == "web3":
            prefix = "SWC"
        else:
            prefix = "FIND"
        
        return self.state.reserve_range(prefix, category, count, start)
    
    def list_findings(self) -> List[Dict]:
        """List all generated finding IDs."""
        return self.state.list_findings()
    
    def reset(self):
        """Reset all counters."""
        self.state.reset()
    
    def get_status(self) -> Dict:
        """Get current status."""
        return self.state.get_status()


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate unique, sequential finding IDs for security audit reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "command",
        choices=["next", "reserve", "list", "reset", "status"],
        help="Command to execute"
    )
    parser.add_argument(
        "-t", "--type",
        choices=["web2", "web3"],
        default="web2",
        help="Finding type (default: web2)"
    )
    parser.add_argument(
        "-c", "--category",
        default="OTHER",
        help="Category code (e.g., AUTH, XSS, SWC-107)"
    )
    parser.add_argument(
        "-s", "--state",
        default=".finding-ids.json",
        help="State file path (default: .finding-ids.json)"
    )
    parser.add_argument(
        "-p", "--prefix",
        help="Custom prefix (overrides type default)"
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Starting number (default: 1)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    # Reserve command argument
    parser.add_argument(
        "count",
        nargs="?",
        type=int,
        help="Number of IDs to reserve (for 'reserve' command)"
    )
    
    args = parser.parse_args()
    
    generator = FindingIdGenerator(args.state)
    
    if args.command == "next":
        finding_id = generator.generate(
            finding_type=args.type,
            category=args.category,
            prefix=args.prefix,
            start=args.start
        )
        print(finding_id)
    
    elif args.command == "reserve":
        if args.count is None:
            print("Error: 'reserve' command requires a count", file=sys.stderr)
            sys.exit(1)
        
        finding_ids = generator.reserve(
            count=args.count,
            finding_type=args.type,
            category=args.category,
            prefix=args.prefix,
            start=args.start
        )
        
        for finding_id in finding_ids:
            print(finding_id)
    
    elif args.command == "list":
        findings = generator.list_findings()
        
        if not findings:
            print("No findings generated yet.")
        else:
            print(f"Total findings: {len(findings)}")
            print()
            print(f"{'ID':<30} {'Category':<15} {'Created'}")
            print("-" * 70)
            for finding in findings:
                print(f"{finding['id']:<30} {finding['category']:<15} {finding['created']}")
    
    elif args.command == "reset":
        generator.reset()
        print("Finding ID counter reset.")
    
    elif args.command == "status":
        status = generator.get_status()
        print(f"State file: {status['state_file']}")
        print(f"Total findings: {status['total_findings']}")
        print()
        print("Counters:")
        for key, counter in status["counters"].items():
            print(f"  {key}: next={counter['next']}")


if __name__ == "__main__":
    main()
