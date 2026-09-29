#!/usr/bin/env python3
"""
Evidence Hasher for Security Forensics
=======================================

Takes evidence files as input, generates SHA-256 hashes, creates evidence
manifest, and verifies evidence integrity.

Usage:
    python evidence-hasher.py --files <files> [--output <manifest>]
    python evidence-hasher.py --verify <manifest>

Requirements:
    - Python 3.8+

Author: Security Forensics Team
License: MIT
"""

import argparse
import hashlib
import json
import sys
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class EvidenceItem:
    """Represents a single piece of evidence."""
    file_path: str
    file_name: str
    file_size: int
    sha256_hash: str
    md5_hash: str
    collected_at: str
    collected_by: str = "unknown"
    description: str = ""
    case_number: str = ""
    evidence_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceManifest:
    """Represents the evidence manifest."""
    manifest_id: str
    case_number: str
    created_at: str
    created_by: str
    evidence_items: List[EvidenceItem]
    total_files: int
    total_size: int
    manifest_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Hash Functions
# ============================================================================

def calculate_sha256(file_path: str, chunk_size: int = 8192) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()


def calculate_md5(file_path: str, chunk_size: int = 8192) -> str:
    """Calculate MD5 hash of a file."""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            md5.update(chunk)
    return md5.hexdigest()


def calculate_sha1(file_path: str, chunk_size: int = 8192) -> str:
    """Calculate SHA-1 hash of a file."""
    sha1 = hashlib.sha1()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha1.update(chunk)
    return sha1.hexdigest()


def hash_string(data: str) -> str:
    """Calculate SHA-256 hash of a string."""
    return hashlib.sha256(data.encode()).hexdigest()


# ============================================================================
# Evidence Manifest
# ============================================================================

class EvidenceHasher:
    """Manages evidence hashing and manifest creation."""

    def __init__(self, case_number: str = "", collector: str = "unknown"):
        self.case_number = case_number
        self.collector = collector
        self.evidence_items: List[EvidenceItem] = []

    def add_file(self, file_path: str, description: str = "",
                 evidence_id: str = "", metadata: Optional[Dict[str, Any]] = None) -> EvidenceItem:
        """Add a file to the evidence manifest."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")

        # Calculate hashes
        sha256 = calculate_sha256(file_path)
        md5 = calculate_md5(file_path)

        # Generate evidence ID if not provided
        if not evidence_id:
            evidence_id = f"EVD-{datetime.now().strftime('%Y%m%d')}-{len(self.evidence_items) + 1:04d}"

        item = EvidenceItem(
            file_path=str(path.absolute()),
            file_name=path.name,
            file_size=path.stat().st_size,
            sha256_hash=sha256,
            md5_hash=md5,
            collected_at=datetime.now(timezone.utc).isoformat(),
            collected_by=self.collector,
            description=description,
            case_number=self.case_number,
            evidence_id=evidence_id,
            metadata=metadata or {}
        )

        self.evidence_items.append(item)
        return item

    def add_directory(self, directory: str, pattern: str = "*",
                      recursive: bool = True) -> List[EvidenceItem]:
        """Add all files matching a pattern from a directory."""
        path = Path(directory)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not path.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        items = []
        if recursive:
            files = path.rglob(pattern)
        else:
            files = path.glob(pattern)

        for file_path in files:
            if file_path.is_file():
                try:
                    item = self.add_file(str(file_path))
                    items.append(item)
                except (FileNotFoundError, ValueError):
                    continue

        return items

    def create_manifest(self) -> EvidenceManifest:
        """Create the evidence manifest."""
        manifest_id = f"MANIFEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        total_size = sum(item.file_size for item in self.evidence_items)

        manifest = EvidenceManifest(
            manifest_id=manifest_id,
            case_number=self.case_number,
            created_at=datetime.now(timezone.utc).isoformat(),
            created_by=self.collector,
            evidence_items=self.evidence_items,
            total_files=len(self.evidence_items),
            total_size=total_size,
            metadata={
                "hash_algorithm": "SHA-256",
                "secondary_hash": "MD5",
                "manifest_version": "1.0",
            }
        )

        # Calculate manifest hash
        manifest_data = json.dumps(
            [asdict(item) for item in self.evidence_items],
            sort_keys=True,
            default=str
        )
        manifest.manifest_hash = hash_string(manifest_data)

        return manifest

    def verify_file(self, file_path: str, expected_hash: str) -> Tuple[bool, str]:
        """Verify a file against an expected hash."""
        actual_hash = calculate_sha256(file_path)
        return actual_hash == expected_hash, actual_hash

    def verify_manifest(self, manifest: EvidenceManifest) -> Dict[str, Any]:
        """Verify all files in a manifest."""
        results = {
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "total_files": len(manifest.evidence_items),
            "verified_files": 0,
            "failed_files": 0,
            "missing_files": 0,
            "details": []
        }

        for item in manifest.evidence_items:
            detail = {
                "evidence_id": item.evidence_id,
                "file_path": item.file_path,
                "expected_hash": item.sha256_hash,
                "status": "unknown"
            }

            if not Path(item.file_path).exists():
                detail["status"] = "missing"
                results["missing_files"] += 1
            else:
                is_valid, actual_hash = self.verify_file(item.file_path, item.sha256_hash)
                detail["actual_hash"] = actual_hash
                if is_valid:
                    detail["status"] = "verified"
                    results["verified_files"] += 1
                else:
                    detail["status"] = "failed"
                    results["failed_files"] += 1

            results["details"].append(detail)

        results["integrity_intact"] = (
            results["failed_files"] == 0 and results["missing_files"] == 0
        )

        return results


# ============================================================================
# Output Formatters
# ============================================================================

def format_manifest_json(manifest: EvidenceManifest) -> str:
    """Format manifest as JSON."""
    data = {
        "manifest_id": manifest.manifest_id,
        "case_number": manifest.case_number,
        "created_at": manifest.created_at,
        "created_by": manifest.created_by,
        "total_files": manifest.total_files,
        "total_size": manifest.total_size,
        "total_size_human": format_size(manifest.total_size),
        "manifest_hash": manifest.manifest_hash,
        "metadata": manifest.metadata,
        "evidence_items": [asdict(item) for item in manifest.evidence_items],
    }
    return json.dumps(data, indent=2, default=str)


def format_manifest_text(manifest: EvidenceManifest) -> str:
    """Format manifest as human-readable text."""
    lines = [
        "=" * 80,
        "EVIDENCE MANIFEST",
        "=" * 80,
        f"Manifest ID:    {manifest.manifest_id}",
        f"Case Number:    {manifest.case_number}",
        f"Created:        {manifest.created_at}",
        f"Created By:     {manifest.collector}",
        f"Total Files:    {manifest.total_files}",
        f"Total Size:     {format_size(manifest.total_size)}",
        f"Manifest Hash:  {manifest.manifest_hash}",
        "=" * 80,
        "",
        "EVIDENCE ITEMS:",
        "-" * 80,
    ]

    for item in manifest.evidence_items:
        lines.extend([
            f"",
            f"Evidence ID:    {item.evidence_id}",
            f"File:           {item.file_name}",
            f"Path:           {item.file_path}",
            f"Size:           {format_size(item.file_size)}",
            f"SHA-256:        {item.sha256_hash}",
            f"MD5:            {item.md5_hash}",
            f"Collected:      {item.collected_at}",
            f"Collector:      {item.collected_by}",
            f"Description:    {item.description}",
            "-" * 80,
        ])

    return "\n".join(lines)


def format_verification_report(results: Dict[str, Any]) -> str:
    """Format verification results as a report."""
    lines = [
        "=" * 80,
        "EVIDENCE VERIFICATION REPORT",
        "=" * 80,
        f"Verified At:    {results['verified_at']}",
        f"Total Files:    {results['total_files']}",
        f"Verified:       {results['verified_files']}",
        f"Failed:         {results['failed_files']}",
        f"Missing:        {results['missing_files']}",
        f"Integrity:      {'INTACT' if results['integrity_intact'] else 'COMPROMISED'}",
        "=" * 80,
        "",
    ]

    for detail in results["details"]:
        status_icon = {
            "verified": "[OK]",
            "failed": "[FAIL]",
            "missing": "[MISSING]",
        }.get(detail["status"], "[?]")

        lines.append(
            f"{status_icon} {detail['evidence_id']}: {detail['file_path']}"
        )

        if detail["status"] == "failed":
            lines.append(f"    Expected: {detail['expected_hash']}")
            lines.append(f"    Actual:   {detail['actual_hash']}")

    return "\n".join(lines)


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Hash and verify evidence integrity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create manifest
  python evidence-hasher.py --files evidence1.log evidence2.log --case CASE-2024-0115 --output manifest.json

  # Add directory
  python evidence-hasher.py --directory /evidence/logs/ --pattern "*.log" --case CASE-2024-0115

  # Verify manifest
  python evidence-hasher.py --verify manifest.json

  # Output as text
  python evidence-hasher.py --files evidence1.log --format text --output manifest.txt
        """
    )
    parser.add_argument("--files", nargs="+", help="Evidence files to hash")
    parser.add_argument("--directory", help="Directory to scan for evidence")
    parser.add_argument("--pattern", default="*", help="File pattern (default: *)")
    parser.add_argument("--recursive", action="store_true", default=True,
                       help="Scan recursively (default: True)")
    parser.add_argument("--case", default="", help="Case number")
    parser.add_argument("--collector", default="unknown", help="Collector name")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                       help="Output format (default: json)")
    parser.add_argument("--verify", help="Verify existing manifest file")
    parser.add_argument("--description", default="", help="Description for evidence files")

    args = parser.parse_args()

    # Verify mode
    if args.verify:
        print(f"Verifying manifest: {args.verify}", file=sys.stderr)
        manifest_data = json.loads(Path(args.verify).read_text())

        # Reconstruct manifest
        manifest = EvidenceManifest(
            manifest_id=manifest_data["manifest_id"],
            case_number=manifest_data["case_number"],
            created_at=manifest_data["created_at"],
            created_by=manifest_data["created_by"],
            evidence_items=[EvidenceItem(**item) for item in manifest_data["evidence_items"]],
            total_files=manifest_data["total_files"],
            total_size=manifest_data["total_size"],
            manifest_hash=manifest_data.get("manifest_hash", ""),
            metadata=manifest_data.get("metadata", {})
        )

        hasher = EvidenceHasher(case_number=manifest.case_number, collector=manifest.created_by)
        results = hasher.verify_manifest(manifest)

        report = format_verification_report(results)
        if args.output:
            Path(args.output).write_text(report)
            print(f"Verification report written to: {args.output}", file=sys.stderr)
        else:
            print(report)

        # Exit with error code if integrity compromised
        if not results["integrity_intact"]:
            print("\nWARNING: Evidence integrity compromised!", file=sys.stderr)
            sys.exit(2)

        sys.exit(0)

    # Create manifest mode
    if not args.files and not args.directory:
        print("Error: At least one --files or --directory required", file=sys.stderr)
        sys.exit(1)

    hasher = EvidenceHasher(case_number=args.case, collector=args.collector)

    # Add individual files
    if args.files:
        for file_path in args.files:
            print(f"Hashing: {file_path}", file=sys.stderr)
            try:
                item = hasher.add_file(file_path, description=args.description)
                print(f"  SHA-256: {item.sha256_hash}", file=sys.stderr)
                print(f"  Size: {format_size(item.file_size)}", file=sys.stderr)
            except (FileNotFoundError, ValueError) as e:
                print(f"  Error: {e}", file=sys.stderr)

    # Add directory
    if args.directory:
        print(f"Scanning directory: {args.directory}", file=sys.stderr)
        items = hasher.add_directory(args.directory, pattern=args.pattern,
                                      recursive=args.recursive)
        print(f"  Found {len(items)} files", file=sys.stderr)

    # Create manifest
    manifest = hasher.create_manifest()

    # Format output
    if args.format == "json":
        output = format_manifest_json(manifest)
    else:
        output = format_manifest_text(manifest)

    # Write output
    if args.output:
        Path(args.output).write_text(output)
        print(f"\nManifest written to: {args.output}", file=sys.stderr)
    else:
        print(output)

    # Print summary
    print("", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("EVIDENCE MANIFEST SUMMARY", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Manifest ID: {manifest.manifest_id}", file=sys.stderr)
    print(f"Total files: {manifest.total_files}", file=sys.stderr)
    print(f"Total size: {format_size(manifest.total_size)}", file=sys.stderr)
    print(f"Manifest hash: {manifest.manifest_hash}", file=sys.stderr)


if __name__ == "__main__":
    main()
