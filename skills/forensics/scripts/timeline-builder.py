#!/usr/bin/env python3
"""
Timeline Builder for Security Forensics
========================================

Takes log files and transaction data as input, correlates events across
sources, generates a chronological timeline, and outputs structured
timeline in markdown format.

Usage:
    python timeline-builder.py --logs <log_files> --tx-data <tx_files> [--output <file>]

Requirements:
    - Python 3.8+
    - dateutil

Author: Security Forensics Team
License: MIT
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dateutil import parser as date_parser
except ImportError:
    print("Error: 'python-dateutil' library required. Install with: pip install python-dateutil", file=sys.stderr)
    sys.exit(1)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class TimelineEvent:
    """Represents a single event in the timeline."""
    timestamp: datetime
    event_type: str
    source: str
    description: str
    evidence: str
    severity: str = "info"  # "critical", "high", "medium", "low", "info"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other: "TimelineEvent") -> bool:
        return self.timestamp < other.timestamp


@dataclass
class Timeline:
    """Represents a complete timeline."""
    title: str
    events: List[TimelineEvent]
    sources: List[str]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Log Parsers
# ============================================================================

class LogParser:
    """Base class for log parsers."""

    def __init__(self, source_name: str):
        self.source_name = source_name

    def parse(self, file_path: str) -> List[TimelineEvent]:
        """Parse a log file and return timeline events."""
        raise NotImplementedError


class SyslogParser(LogParser):
    """Parser for syslog format logs."""

    # Common syslog timestamp formats
    TIMESTAMP_PATTERNS = [
        r"(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})",  # Jan 15 10:30:00
        r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)",  # ISO 8601
    ]

    # Patterns for common events
    EVENT_PATTERNS = {
        "ssh_login": r"sshd.*Accepted.*for (\w+) from ([\d.]+)",
        "ssh_failed": r"sshd.*Failed.*for (\w+) from ([\d.]+)",
        "sudo": r"sudo:?\s+(\w+).*COMMAND=(.+)",
        "auth_failure": r"authentication failure.*user=(\w+)",
        "service_start": r"systemd.*Started (.+)",
        "service_stop": r"systemd.*Stopped (.+)",
        "error": r"error|ERROR|Error",
        "warning": r"warning|WARNING|Warning",
    }

    SEVERITY_MAP = {
        "ssh_failed": "high",
        "auth_failure": "high",
        "error": "medium",
        "warning": "low",
    }

    def parse(self, file_path: str) -> List[TimelineEvent]:
        """Parse syslog file."""
        events = []
        content = Path(file_path).read_text(errors="replace")

        for line in content.splitlines():
            event = self._parse_line(line)
            if event:
                events.append(event)

        return events

    def _parse_line(self, line: str) -> Optional[TimelineEvent]:
        """Parse a single log line."""
        # Extract timestamp
        timestamp = None
        for pattern in self.TIMESTAMP_PATTERNS:
            match = re.search(pattern, line)
            if match:
                try:
                    ts_str = match.group(1)
                    # Try to parse with current year if not present
                    if len(ts_str) < 16:  # Syslog format without year
                        ts_str = f"{datetime.now().year} {ts_str}"
                    timestamp = date_parser.parse(ts_str)
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    continue
                break

        if not timestamp:
            return None

        # Determine event type and description
        event_type = "system"
        description = line.strip()
        severity = "info"

        for event_name, pattern in self.EVENT_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                event_type = event_name
                severity = self.SEVERITY_MAP.get(event_name, "info")
                match = re.search(pattern, line, re.IGNORECASE)
                if match and match.groups():
                    description = f"{event_name}: {', '.join(match.groups())}"
                break

        return TimelineEvent(
            timestamp=timestamp,
            event_type=event_type,
            source=self.source_name,
            description=description,
            evidence=line.strip()[:200],
            severity=severity
        )


class JSONLogParser(LogParser):
    """Parser for JSON format logs."""

    def parse(self, file_path: str) -> List[TimelineEvent]:
        """Parse JSON log file."""
        events = []
        content = Path(file_path).read_text(errors="replace")

        # Try to parse as JSON lines
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                event = self._parse_json_entry(data)
                if event:
                    events.append(event)
            except json.JSONDecodeError:
                continue

        return events

    def _parse_json_entry(self, data: Dict[str, Any]) -> Optional[TimelineEvent]:
        """Parse a single JSON log entry."""
        # Extract timestamp
        timestamp = None
        for key in ["timestamp", "time", "ts", "@timestamp", "date"]:
            if key in data:
                try:
                    ts_val = data[key]
                    if isinstance(ts_val, (int, float)):
                        # Unix timestamp
                        timestamp = datetime.fromtimestamp(ts_val, tz=timezone.utc)
                    else:
                        timestamp = date_parser.parse(str(ts_val))
                        if timestamp.tzinfo is None:
                            timestamp = timestamp.replace(tzinfo=timezone.utc)
                    break
                except (ValueError, TypeError):
                    continue

        if not timestamp:
            return None

        # Extract event details
        event_type = data.get("event", data.get("type", data.get("level", "unknown")))
        description = data.get("message", data.get("msg", data.get("description", json.dumps(data)[:200])))
        severity = data.get("severity", data.get("level", "info")).lower()

        # Normalize severity
        severity_map = {
            "critical": "critical", "crit": "critical", "fatal": "critical",
            "error": "high", "err": "high",
            "warning": "medium", "warn": "medium",
            "info": "info", "information": "info",
            "debug": "low", "trace": "low",
        }
        severity = severity_map.get(severity, "info")

        return TimelineEvent(
            timestamp=timestamp,
            event_type=str(event_type),
            source=self.source_name,
            description=str(description),
            evidence=json.dumps(data)[:500],
            severity=severity,
            metadata={k: v for k, v in data.items() if k not in ["timestamp", "time", "ts", "@timestamp"]}
        )


class ApacheLogParser(LogParser):
    """Parser for Apache/Nginx access logs."""

    # Apache combined log format
    LOG_PATTERN = re.compile(
        r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<uri>\S+) \S+" (?P<status>\d{3}) (?P<size>\S+)'
    )

    def parse(self, file_path: str) -> List[TimelineEvent]:
        """Parse Apache/Nginx log file."""
        events = []
        content = Path(file_path).read_text(errors="replace")

        for line in content.splitlines():
            event = self._parse_line(line)
            if event:
                events.append(event)

        return events

    def _parse_line(self, line: str) -> Optional[TimelineEvent]:
        """Parse a single log line."""
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None

        data = match.groupdict()

        # Parse timestamp
        try:
            timestamp = date_parser.parse(data["time"])
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            return None

        # Determine severity based on status code
        status = int(data["status"])
        if status >= 500:
            severity = "high"
        elif status >= 400:
            severity = "medium"
        else:
            severity = "info"

        # Detect suspicious patterns
        event_type = "http_request"
        uri = data["uri"]
        if re.search(r"(union.*select|insert.*into|delete.*from|drop.*table)", uri, re.IGNORECASE):
            event_type = "sql_injection_attempt"
            severity = "critical"
        elif re.search(r"(\.\./|\.\.\\|%2e%2e)", uri):
            event_type = "path_traversal_attempt"
            severity = "high"
        elif re.search(r"(<script|javascript:|on\w+=)", uri, re.IGNORECASE):
            event_type = "xss_attempt"
            severity = "high"

        description = f'{data["method"]} {uri} -> {status} ({data["ip"]})'

        return TimelineEvent(
            timestamp=timestamp,
            event_type=event_type,
            source=self.source_name,
            description=description,
            evidence=line.strip()[:200],
            severity=severity,
            metadata={
                "ip": data["ip"],
                "method": data["method"],
                "uri": uri,
                "status": status,
                "size": data["size"]
            }
        )


class WindowsEventLogParser(LogParser):
    """Parser for Windows Event Log (JSON export)."""

    def parse(self, file_path: str) -> List[TimelineEvent]:
        """Parse Windows Event Log JSON file."""
        events = []
        content = Path(file_path).read_text(errors="replace")

        try:
            data = json.loads(content)
            if isinstance(data, list):
                for entry in data:
                    event = self._parse_entry(entry)
                    if event:
                        events.append(event)
            elif isinstance(data, dict):
                event = self._parse_entry(data)
                if event:
                    events.append(event)
        except json.JSONDecodeError:
            # Try JSON lines
            for line in content.splitlines():
                try:
                    entry = json.loads(line)
                    event = self._parse_entry(entry)
                    if event:
                        events.append(event)
                except json.JSONDecodeError:
                    continue

        return events

    def _parse_entry(self, data: Dict[str, Any]) -> Optional[TimelineEvent]:
        """Parse a single Windows Event Log entry."""
        # Extract timestamp
        timestamp = None
        for key in ["TimeCreated", "Timestamp", "EventTime"]:
            if key in data:
                try:
                    ts_val = data[key]
                    if isinstance(ts_val, dict):
                        ts_val = ts_val.get("#text", ts_val.get("SystemTime"))
                    timestamp = date_parser.parse(str(ts_val))
                    if timestamp.tzinfo is None:
                        timestamp = timestamp.replace(tzinfo=timezone.utc)
                    break
                except (ValueError, TypeError):
                    continue

        if not timestamp:
            return None

        # Extract event details
        event_id = data.get("EventID", data.get("Id", "unknown"))
        event_type = data.get("Task", data.get("EventType", "unknown"))
        description = data.get("Message", data.get("Description", json.dumps(data)[:200]))

        # Map event IDs to severity
        severity = "info"
        if event_id in [4625, 4672, 4720, 4726]:  # Failed logon, privilege use, account created/deleted
            severity = "high"
        elif event_id in [1102, 104]:  # Audit log cleared
            severity = "critical"

        return TimelineEvent(
            timestamp=timestamp,
            event_type=f"windows_event_{event_id}",
            source=self.source_name,
            description=str(description),
            evidence=json.dumps(data)[:500],
            severity=severity,
            metadata={"event_id": event_id, "event_type": event_type}
        )


# ============================================================================
# Transaction Data Parser
# ============================================================================

class TransactionDataParser:
    """Parser for blockchain transaction data."""

    def parse(self, file_path: str) -> List[TimelineEvent]:
        """Parse transaction data file."""
        events = []
        content = Path(file_path).read_text(errors="replace")

        try:
            data = json.loads(content)
            if isinstance(data, list):
                for tx in data:
                    event = self._parse_transaction(tx)
                    if event:
                        events.append(event)
            elif isinstance(data, dict):
                event = self._parse_transaction(data)
                if event:
                    events.append(event)
        except json.JSONDecodeError:
            # Try JSON lines
            for line in content.splitlines():
                try:
                    tx = json.loads(line)
                    event = self._parse_transaction(tx)
                    if event:
                        events.append(event)
                except json.JSONDecodeError:
                    continue

        return events

    def _parse_transaction(self, data: Dict[str, Any]) -> Optional[TimelineEvent]:
        """Parse a single transaction."""
        # Extract timestamp
        timestamp = None
        for key in ["timestamp", "time", "blockTime", "block_time"]:
            if key in data:
                try:
                    ts_val = data[key]
                    if isinstance(ts_val, (int, float)):
                        timestamp = datetime.fromtimestamp(ts_val, tz=timezone.utc)
                    else:
                        timestamp = date_parser.parse(str(ts_val))
                        if timestamp.tzinfo is None:
                            timestamp = timestamp.replace(tzinfo=timezone.utc)
                    break
                except (ValueError, TypeError):
                    continue

        if not timestamp:
            return None

        # Extract transaction details
        tx_hash = data.get("hash", data.get("tx_hash", data.get("transactionHash", "unknown")))
        from_addr = data.get("from", data.get("from_address", "unknown"))
        to_addr = data.get("to", data.get("to_address", "unknown"))
        value = data.get("value", 0)

        # Determine event type
        event_type = "transaction"
        severity = "info"

        # Check for suspicious patterns
        if data.get("status") == 0 or data.get("status") == "failed":
            event_type = "failed_transaction"
            severity = "medium"

        if data.get("is_exploit") or data.get("exploit"):
            event_type = "exploit_transaction"
            severity = "critical"

        description = f"Tx: {tx_hash[:20]}... From: {from_addr[:10]}... To: {to_addr[:10]}... Value: {value}"

        return TimelineEvent(
            timestamp=timestamp,
            event_type=event_type,
            source="blockchain",
            description=description,
            evidence=json.dumps(data)[:500],
            severity=severity,
            metadata={
                "tx_hash": tx_hash,
                "from": from_addr,
                "to": to_addr,
                "value": value,
                "block_number": data.get("blockNumber", data.get("block_number")),
            }
        )


# ============================================================================
# Timeline Builder
# ============================================================================

class TimelineBuilder:
    """Builds a timeline from multiple sources."""

    def __init__(self):
        self.events: List[TimelineEvent] = []
        self.sources: List[str] = []

    def add_events(self, events: List[TimelineEvent], source: str) -> None:
        """Add events from a source."""
        self.events.extend(events)
        if source not in self.sources:
            self.sources.append(source)

    def build(self, title: str = "Incident Timeline") -> Timeline:
        """Build the timeline."""
        # Sort events by timestamp
        self.events.sort()

        # Determine time range
        start_time = self.events[0].timestamp if self.events else None
        end_time = self.events[-1].timestamp if self.events else None

        return Timeline(
            title=title,
            events=self.events,
            sources=self.sources,
            start_time=start_time,
            end_time=end_time,
            metadata={
                "total_events": len(self.events),
                "sources": self.sources,
                "build_timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )


# ============================================================================
# Output Formatters
# ============================================================================

def format_markdown(timeline: Timeline) -> str:
    """Format timeline as markdown."""
    lines = [
        f"# {timeline.title}",
        "",
        "## Summary",
        "",
        f"- **Total Events:** {len(timeline.events)}",
        f"- **Sources:** {', '.join(timeline.sources)}",
    ]

    if timeline.start_time and timeline.end_time:
        lines.append(f"- **Start Time:** {timeline.start_time.isoformat()}")
        lines.append(f"- **End Time:** {timeline.end_time.isoformat()}")
        duration = timeline.end_time - timeline.start_time
        lines.append(f"- **Duration:** {duration}")

    lines.extend([
        "",
        "## Timeline",
        "",
        "| Time (UTC) | Event Type | Severity | Description | Source | Evidence |",
        "|------------|------------|----------|-------------|--------|----------|",
    ])

    for event in timeline.events:
        ts = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        lines.append(
            f"| {ts} | {event.event_type} | {event.severity} | "
            f"{event.description[:80]} | {event.source} | {event.evidence[:50]} |"
        )

    # Add detailed section
    lines.extend([
        "",
        "## Detailed Events",
        "",
    ])

    for i, event in enumerate(timeline.events, 1):
        lines.extend([
            f"### Event {i}: {event.event_type}",
            "",
            f"- **Time:** {event.timestamp.isoformat()}",
            f"- **Severity:** {event.severity}",
            f"- **Source:** {event.source}",
            f"- **Description:** {event.description}",
            f"- **Evidence:** `{event.evidence}`",
            "",
        ])

        if event.metadata:
            lines.extend([
                "**Metadata:**",
                "",
                "```json",
                json.dumps(event.metadata, indent=2, default=str),
                "```",
                "",
            ])

    return "\n".join(lines)


def format_json(timeline: Timeline) -> str:
    """Format timeline as JSON."""
    data = {
        "title": timeline.title,
        "summary": {
            "total_events": len(timeline.events),
            "sources": timeline.sources,
            "start_time": timeline.start_time.isoformat() if timeline.start_time else None,
            "end_time": timeline.end_time.isoformat() if timeline.end_time else None,
        },
        "events": [
            {
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "source": event.source,
                "description": event.description,
                "evidence": event.evidence,
                "severity": event.severity,
                "metadata": event.metadata,
            }
            for event in timeline.events
        ],
        "metadata": timeline.metadata,
    }
    return json.dumps(data, indent=2, default=str)


# ============================================================================
# Main
# ============================================================================

def detect_parser(file_path: str) -> Optional[LogParser]:
    """Detect the appropriate parser for a file."""
    content = Path(file_path).read_text(errors="replace")[:1000]

    # Check for JSON
    if content.strip().startswith("{") or content.strip().startswith("["):
        try:
            json.loads(content.splitlines()[0])
            return JSONLogParser(Path(file_path).name)
        except json.JSONDecodeError:
            pass

    # Check for Windows Event Log
    if "EventID" in content or "TimeCreated" in content:
        return WindowsEventLogParser(Path(file_path).name)

    # Check for Apache/Nginx
    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*\[.*\].*"(GET|POST|PUT|DELETE)', content):
        return ApacheLogParser(Path(file_path).name)

    # Default to syslog
    return SyslogParser(Path(file_path).name)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build incident timeline from logs and transaction data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python timeline-builder.py --logs /var/log/auth.log /var/log/syslog --output timeline.md
  python timeline-builder.py --logs access.log --tx-data transactions.json --output timeline.md
  python timeline-builder.py --logs *.log --format json --output timeline.json
        """
    )
    parser.add_argument("--logs", nargs="+", help="Log files to parse")
    parser.add_argument("--tx-data", nargs="+", help="Transaction data files to parse")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown",
                       help="Output format (default: markdown)")
    parser.add_argument("--title", default="Incident Timeline", help="Timeline title")

    args = parser.parse_args()

    if not args.logs and not args.tx_data:
        print("Error: At least one --logs or --tx-data file required", file=sys.stderr)
        sys.exit(1)

    builder = TimelineBuilder()

    # Parse log files
    if args.logs:
        for log_file in args.logs:
            print(f"Parsing log file: {log_file}", file=sys.stderr)
            parser = detect_parser(log_file)
            if parser:
                events = parser.parse(log_file)
                builder.add_events(events, Path(log_file).name)
                print(f"  Found {len(events)} events", file=sys.stderr)
            else:
                print(f"  Warning: Could not determine parser for {log_file}", file=sys.stderr)

    # Parse transaction data
    if args.tx_data:
        tx_parser = TransactionDataParser()
        for tx_file in args.tx_data:
            print(f"Parsing transaction data: {tx_file}", file=sys.stderr)
            events = tx_parser.parse(tx_file)
            builder.add_events(events, "blockchain")
            print(f"  Found {len(events)} events", file=sys.stderr)

    # Build timeline
    timeline = builder.build(title=args.title)

    # Format output
    if args.format == "markdown":
        output = format_markdown(timeline)
    else:
        output = format_json(timeline)

    # Write output
    if args.output:
        Path(args.output).write_text(output)
        print(f"Timeline written to: {args.output}", file=sys.stderr)
    else:
        print(output)

    # Print summary
    print("", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("TIMELINE SUMMARY", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Total events: {len(timeline.events)}", file=sys.stderr)
    print(f"Sources: {', '.join(timeline.sources)}", file=sys.stderr)
    if timeline.start_time and timeline.end_time:
        print(f"Time range: {timeline.start_time.isoformat()} to {timeline.end_time.isoformat()}", file=sys.stderr)
        duration = timeline.end_time - timeline.start_time
        print(f"Duration: {duration}", file=sys.stderr)


if __name__ == "__main__":
    main()
