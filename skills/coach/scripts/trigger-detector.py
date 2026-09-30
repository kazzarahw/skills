#!/usr/bin/env python3
"""
Trigger Detection System for Security Coach

Detects behavioral patterns in agent tool call history that indicate
the agent is stuck, drifting, or using ineffective approaches.

Supports real-time and batch analysis of tool call histories.

Usage:
    from trigger_detector import TriggerDetector, ToolCall, TriggerType

    detector = TriggerDetector()
    detector.add_tool_call(ToolCall(...))
    triggers = detector.check_triggers()
    intervention = detector.get_intervention()

Batch analysis:
    detector = TriggerDetector()
    detector.load_history(tool_calls_json)
    report = detector.generate_report()
"""

import re
import json
import time
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple, Any
from enum import Enum
from collections import defaultdict
from pathlib import Path


class TriggerType(Enum):
    """Types of triggers that can be detected."""
    REPEATED_FAILURE = "repeated_failure"
    NO_PROGRESS = "no_progress"
    RABBIT_HOLE = "rabbit_hole"
    KNOWN_BAD_APPROACH = "known_bad_approach"
    SCOPE_DRIFT = "scope_drift"
    REWARD_HACKING = "reward_hacking"
    OVERTHINKING = "overthinking"
    PERFECTIONISM = "perfectionism"
    CONFIRMATION_BIAS = "confirmation_bias"
    TOOL_FIXATION = "tool_fixation"


# Priority order for resolution (lower number = higher priority)
PRIORITY_ORDER = {
    TriggerType.SCOPE_DRIFT: 1,
    TriggerType.REWARD_HACKING: 2,
    TriggerType.KNOWN_BAD_APPROACH: 3,
    TriggerType.REPEATED_FAILURE: 4,
    TriggerType.RABBIT_HOLE: 5,
    TriggerType.NO_PROGRESS: 6,
    TriggerType.OVERTHINKING: 7,
    TriggerType.PERFECTIONISM: 8,
    TriggerType.CONFIRMATION_BIAS: 9,
    TriggerType.TOOL_FIXATION: 10,
}


@dataclass
class ToolCall:
    """Represents a single tool call made by the agent."""
    tool_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    result: str = ""
    success: bool = True
    duration: float = 0.0
    target: str = ""
    command: str = ""
    agent_text: str = ""  # Text output from agent (for overthinking detection)

    def fingerprint(self) -> str:
        """Generate a unique fingerprint for this tool call."""
        # Normalize parameters for comparison
        normalized = json.dumps(self.parameters, sort_keys=True, default=str)
        data = f"{self.tool_name}:{normalized}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "timestamp": self.timestamp,
            "result": self.result,
            "success": self.success,
            "duration": self.duration,
            "target": self.target,
            "command": self.command,
            "agent_text": self.agent_text,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ToolCall":
        """Create ToolCall from dictionary."""
        return cls(
            tool_name=data.get("tool_name", ""),
            parameters=data.get("parameters", {}),
            timestamp=data.get("timestamp", time.time()),
            result=data.get("result", ""),
            success=data.get("success", True),
            duration=data.get("duration", 0.0),
            target=data.get("target", ""),
            command=data.get("command", ""),
            agent_text=data.get("agent_text", ""),
        )


@dataclass
class TriggerState:
    """Represents the current state of a detected trigger."""
    trigger_type: TriggerType
    confidence: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)
    first_detected: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    count: int = 1
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "trigger_type": self.trigger_type.value,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "first_detected": self.first_detected,
            "last_updated": self.last_updated,
            "count": self.count,
            "context": self.context,
        }


class TechniqueClassifier:
    """Classifies tool calls into technique categories."""

    TECHNIQUE_PATTERNS = {
        "static_analysis": [
            r"\bread\b", r"\bgrep\b", r"\bglob\b", r"objdump", r"\bnm\b",
            r"\bstrings\b", r"decompil", r"disassembl", r"source.*review",
        ],
        "dynamic_analysis": [
            r"\bgdb\b", r"\blldb\b", r"\bfrida\b", r"\bafl\b", r"honggfuzz",
            r"libfuzzer", r"\bstrace\b", r"\bltrace\b", r"debug",
        ],
        "network_analysis": [
            r"\bnmap\b", r"\bmasscan\b", r"tcpdump", r"wireshark", r"\btshark\b",
            r"packet.*capture", r"service.*enumeration",
        ],
        "web_analysis": [
            r"\bcurl\b", r"\bwget\b", r"\bburp\b", r"\bzap\b", r"sqlmap",
            r"xsstrike", r"commix", r"\bwpscan\b", r"web.*test",
        ],
        "cryptanalysis": [
            r"\bopenssl\b", r"\bhashcat\b", r"cryptograph", r"protocol.*analysis",
            r"encryption.*review",
        ],
        "social_engineering": [
            r"phishing", r"pretexting", r"baiting", r"tailgating", r"vishing",
        ],
    }

    # Known bad approach patterns
    KNOWN_BAD_APPROACHES = {
        "sqli_on_nosql": {
            "patterns": [r"sqlmap", r"sql.*injection"],
            "target_patterns": [r"mongodb", r"nosql", r"dynamodb", r"cassandra"],
            "description": "SQL injection against NoSQL database",
        },
        "ssrf_on_static": {
            "patterns": [r"ssrf", r"server.*side.*request"],
            "target_patterns": [r"static", r"html", r"no.*backend"],
            "description": "SSRF against static site",
        },
        "source_review_on_binary": {
            "patterns": [r"source.*review", r"code.*review"],
            "target_patterns": [r"binary", r"exe", r"no.*source", r"stripped"],
            "description": "Source code review on compiled binary",
        },
        "brute_force_without_defaults": {
            "patterns": [r"hydra", r"medusa", r"brute"],
            "target_patterns": [r"login", r"auth"],
            "description": "Brute forcing without trying default credentials first",
        },
    }

    # Rabbit hole indicators
    RABBIT_HOLE_INDICATORS = {
        "consecutive_out_of_surface": 5,
        "time_threshold": 300,  # 5 minutes
    }

    # Scope keywords
    SCOPE_KEYWORDS = {
        "authorized", "scope", "allowed", "permitted", "authorized_targets",
        "in_scope", "out_of_scope", "excluded",
    }

    def __init__(self):
        self.technique_history: List[str] = []

    def classify(self, tool_call: ToolCall) -> List[str]:
        """Classify a tool call into technique categories."""
        techniques = []
        command = f"{tool_call.tool_name} {tool_call.command}".lower()

        for technique, patterns in self.TECHNIQUE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, command):
                    techniques.append(technique)
                    break

        if techniques:
            self.technique_history.extend(techniques)

        return techniques

    def get_summary(self) -> Dict:
        """Get classification summary."""
        technique_counts = {}
        for technique in self.technique_history:
            technique_counts[technique] = technique_counts.get(technique, 0) + 1

        return {
            "total_classifications": len(self.technique_history),
            "techniques": technique_counts,
            "primary_technique": max(technique_counts, key=technique_counts.get) if technique_counts else None,
        }


class TriggerDetector:
    """Detects problematic patterns in agent behavior."""

    def __init__(self):
        self.tool_calls: List[ToolCall] = []
        self.triggers: Dict[TriggerType, TriggerState] = {}
        self.scope_targets: Set[str] = set()
        self.failed_attempts: Dict[str, List[ToolCall]] = defaultdict(list)
        self.intervention_history: List[Dict] = []
        self.classifier = TechniqueClassifier()
        self.candidate_output_count = 0
        self.last_candidate_output_time: Optional[float] = None

    def add_tool_call(self, tool_call: ToolCall) -> None:
        """Add a tool call to the detector's history."""
        self.tool_calls.append(tool_call)

        # Classify the technique
        self.classifier.classify(tool_call)

        # Track failed attempts
        if not tool_call.success:
            key = f"{tool_call.tool_name}:{tool_call.target}"
            self.failed_attempts[key].append(tool_call)

        # Update scope if mentioned
        if "scope" in tool_call.parameters:
            self._update_scope(tool_call.parameters["scope"])

        # Track candidate outputs
        if self._is_candidate_output(tool_call):
            self.candidate_output_count += 1
            self.last_candidate_output_time = tool_call.timestamp

    def _update_scope(self, scope: Any) -> None:
        """Update the authorized scope targets."""
        if isinstance(scope, list):
            self.scope_targets.update(str(s) for s in scope)
        elif isinstance(scope, str):
            self.scope_targets.add(scope)

    def _is_candidate_output(self, tool_call: ToolCall) -> bool:
        """Check if a tool call produced a candidate output."""
        # File written to disk
        if tool_call.tool_name in ("write", "edit") and tool_call.success:
            return True

        # Finding reported
        if any(keyword in tool_call.result.lower() for keyword in ["found", "vulnerable", "exploit", "confirmed"]):
            return True

        # Hypothesis stated
        if any(keyword in tool_call.agent_text.lower() for keyword in ["hypothesis", "i think", "maybe", "could be"]):
            return True

        return False

    def check_triggers(self) -> List[TriggerState]:
        """Check all trigger conditions and return active triggers."""
        active_triggers = []

        # Check each trigger type
        checks = [
            self._detect_repeated_failure(),
            self._detect_no_progress(),
            self._detect_rabbit_hole(),
            self._detect_known_bad_approach(),
            self._detect_scope_drift(),
            self._detect_reward_hacking(),
            self._detect_overthinking(),
            self._detect_perfectionism(),
            self._detect_confirmation_bias(),
            self._detect_tool_fixation(),
        ]

        for trigger in checks:
            if trigger:
                # Increment count if this trigger type was already detected before
                if trigger.trigger_type in self.triggers:
                    trigger.count = self.triggers[trigger.trigger_type].count + 1
                self.triggers[trigger.trigger_type] = trigger
                active_triggers.append(trigger)

        return active_triggers

    def _detect_repeated_failure(self) -> Optional[TriggerState]:
        """
        Detect if agent is repeatedly failing with the same technique.

        Threshold: 3+ consecutive failed attempts with same technique.
        """
        if len(self.tool_calls) < 3:
            return None

        # Check for consecutive failures with same fingerprint
        recent = self.tool_calls[-10:]
        consecutive_count = 1
        last_fingerprint = recent[-1].fingerprint() if recent else None

        for i in range(len(recent) - 2, -1, -1):
            if recent[i].fingerprint() == last_fingerprint and not recent[i].success:
                consecutive_count += 1
            else:
                break

        if consecutive_count >= 3:
            confidence = min(0.70 + (consecutive_count - 3) * 0.15, 0.95)
            evidence = [
                f"{consecutive_count} consecutive failed attempts with same technique",
                f"Tool: {recent[-1].tool_name}",
                f"Target: {recent[-1].target or 'N/A'}",
            ]
            return TriggerState(
                trigger_type=TriggerType.REPEATED_FAILURE,
                confidence=confidence,
                evidence=evidence,
                context={
                    "consecutive_failures": consecutive_count,
                    "tool_name": recent[-1].tool_name,
                    "target": recent[-1].target,
                },
            )

        return None

    def _detect_no_progress(self) -> Optional[TriggerState]:
        """
        Detect if agent is making calls without producing candidate output.

        Threshold: 10+ tool calls without producing a candidate output.
        """
        if len(self.tool_calls) < 10:
            return None

        # Count calls since last candidate output
        calls_since_output = 0
        for call in reversed(self.tool_calls):
            if self._is_candidate_output(call):
                break
            calls_since_output += 1

        if calls_since_output >= 10:
            confidence = min(0.60 + (calls_since_output - 10) * 0.05, 0.95)
            evidence = [
                f"{calls_since_output} tool calls without producing candidate output",
                f"Last output: {self.last_candidate_output_time or 'never'}",
            ]
            return TriggerState(
                trigger_type=TriggerType.NO_PROGRESS,
                confidence=confidence,
                evidence=evidence,
                context={
                    "calls_without_output": calls_since_output,
                    "total_calls": len(self.tool_calls),
                },
            )

        return None

    def _detect_rabbit_hole(self) -> Optional[TriggerState]:
        """
        Detect if agent is going down a rabbit hole.

        Threshold: 5+ consecutive tool calls targeting code outside attack surface.
        """
        if len(self.tool_calls) < 5:
            return None

        # Check for consecutive out-of-surface calls
        consecutive_out = 0
        for call in reversed(self.tool_calls[-10:]):
            target = call.target.lower() if call.target else ""
            if not target:
                continue

            # Check if target is in scope
            in_scope = any(
                scope_target.lower() in target or target in scope_target.lower()
                for scope_target in self.scope_targets
            )

            if in_scope:
                break
            else:
                consecutive_out += 1

        if consecutive_out >= 5:
            confidence = min(0.60 + (consecutive_out - 5) * 0.08, 0.95)
            evidence = [
                f"{consecutive_out} consecutive calls outside attack surface",
                f"Last target: {self.tool_calls[-1].target or 'N/A'}",
            ]
            return TriggerState(
                trigger_type=TriggerType.RABBIT_HOLE,
                confidence=confidence,
                evidence=evidence,
                context={
                    "consecutive_out_of_surface": consecutive_out,
                    "last_target": self.tool_calls[-1].target,
                },
            )

        return None

    def _detect_known_bad_approach(self) -> Optional[TriggerState]:
        """
        Detect if agent is using a known bad approach.

        Checks for technique-target incompatibilities.
        """
        for call in self.tool_calls[-10:]:
            command = f"{call.tool_name} {call.command}".lower()
            target = call.target.lower()

            for approach_name, approach_info in self.classifier.KNOWN_BAD_APPROACHES.items():
                # Check if technique matches
                technique_match = any(
                    re.search(pattern, command)
                    for pattern in approach_info["patterns"]
                )

                if technique_match:
                    # Check if target matches
                    target_match = any(
                        re.search(pattern, target)
                        for pattern in approach_info["target_patterns"]
                    )

                    if target_match:
                        evidence = [
                            f"Technique: {approach_info['description']}",
                            f"Command: {call.command[:100]}",
                            f"Target: {call.target}",
                        ]
                        return TriggerState(
                            trigger_type=TriggerType.KNOWN_BAD_APPROACH,
                            confidence=0.90,
                            evidence=evidence,
                            context={
                                "approach": approach_name,
                                "technique": approach_info["description"],
                            },
                        )

        return None

    def _detect_scope_drift(self) -> Optional[TriggerState]:
        """
        Detect if agent is drifting outside authorized scope.

        Threshold: 3+ consecutive tool calls targeting out-of-scope resources.
        """
        if not self.scope_targets:
            return None

        out_of_scope_streak = 0
        for call in reversed(self.tool_calls[-10:]):
            target = call.target.lower() if call.target else ""
            if not target:
                continue

            in_scope = any(
                scope_target.lower() in target or target in scope_target.lower()
                for scope_target in self.scope_targets
            )

            if in_scope:
                break
            else:
                out_of_scope_streak += 1

        if out_of_scope_streak >= 3:
            confidence = min(0.70 + (out_of_scope_streak - 3) * 0.10, 0.95)
            evidence = [
                f"{out_of_scope_streak} consecutive out-of-scope targets",
                f"Last target: {call.target}",
                f"Authorized: {', '.join(list(self.scope_targets)[:3])}",
            ]
            return TriggerState(
                trigger_type=TriggerType.SCOPE_DRIFT,
                confidence=confidence,
                evidence=evidence,
                context={
                    "out_of_scope_streak": out_of_scope_streak,
                    "last_target": call.target,
                    "scope": list(self.scope_targets),
                },
            )

        return None

    def _detect_reward_hacking(self) -> Optional[TriggerState]:
        """
        Detect if agent is reward hacking (gaming the metrics).

        Indicators: hardcoded outputs, skipped verification, output manipulation.
        """
        if len(self.tool_calls) < 3:
            return None

        # Check for hardcoded outputs (writing files with expected values)
        offset = max(0, len(self.tool_calls) - 10)
        for i, call in enumerate(self.tool_calls[-10:]):
            if call.tool_name in ("write", "edit") and call.success:
                # Check if preceded by actual execution
                preceded_by_execution = any(
                    self.tool_calls[offset + j].tool_name in ("shell", "execute")
                    for j in range(max(0, i - 3), i)
                )
                if not preceded_by_execution:
                    # Check if content looks like expected values
                    if any(keyword in call.result.lower() for keyword in ["flag", "found", "success", "pwned"]):
                        evidence = [
                            "Hardcoded output detected without execution",
                            f"File: {call.target or call.parameters.get('path', 'unknown')}",
                        ]
                        return TriggerState(
                            trigger_type=TriggerType.REWARD_HACKING,
                            confidence=0.90,
                            evidence=evidence,
                            context={"indicator": "hardcoded_output"},
                        )

        # Check for skipped verification
        exploit_calls = [c for c in self.tool_calls if "exploit" in c.tool_name.lower() or "exploit" in c.command.lower()]
        if exploit_calls:
            last_exploit_idx = max(
                i for i, c in enumerate(self.tool_calls)
                if "exploit" in c.tool_name.lower() or "exploit" in c.command.lower()
            )
            post_exploit = self.tool_calls[last_exploit_idx:]
            verification_tools = [
                c for c in post_exploit
                if any(v in c.tool_name.lower() for v in ["verify", "validate", "confirm", "check"])
            ]
            if not verification_tools and len(post_exploit) > 2:
                evidence = [
                    "Exploitation without verification",
                    f"Last exploit: {exploit_calls[-1].command[:100]}",
                ]
                return TriggerState(
                    trigger_type=TriggerType.REWARD_HACKING,
                    confidence=0.80,
                    evidence=evidence,
                    context={"indicator": "skipped_verification"},
                )

        return None

    def _detect_overthinking(self) -> Optional[TriggerState]:
        """
        Detect if agent is overthinking (excessive analysis without action).

        Threshold: 5+ consecutive analysis paragraphs without tool calls.
        """
        if len(self.tool_calls) < 5:
            return None

        # Check for long text blocks without tool calls
        analysis_blocks = 0
        for call in reversed(self.tool_calls[-10:]):
            if call.agent_text and len(call.agent_text) > 200:
                # Count sentences
                sentences = len([s for s in call.agent_text.split('.') if s.strip()])
                if sentences >= 3:
                    analysis_blocks += 1
                else:
                    break
            else:
                break

        if analysis_blocks >= 5:
            confidence = min(0.60 + (analysis_blocks - 5) * 0.08, 0.90)
            evidence = [
                f"{analysis_blocks} analysis blocks without action",
                "Possible analysis paralysis",
            ]
            return TriggerState(
                trigger_type=TriggerType.OVERTHINKING,
                confidence=confidence,
                evidence=evidence,
                context={"analysis_blocks": analysis_blocks},
            )

        return None

    def _detect_perfectionism(self) -> Optional[TriggerState]:
        """
        Detect if agent is being overly perfectionist.

        Indicators: refining working solutions, cosmetic changes.
        """
        if len(self.tool_calls) < 8:
            return None

        # Check for repeated similar commands (refinement)
        recent = self.tool_calls[-8:]
        tool_commands = defaultdict(list)
        for call in recent:
            tool_commands[call.tool_name].append(call)

        for tool, calls in tool_commands.items():
            if len(calls) >= 4:
                # Check if commands are similar (refining)
                base_cmd = calls[0].command[:50] if calls[0].command else ""
                if base_cmd:
                    similar = sum(1 for c in calls if c.command and c.command[:50] == base_cmd)
                    if similar >= 3:
                        evidence = [
                            f"Repeated refinement of {tool} commands",
                            f"Similar commands: {similar}/{len(calls)}",
                        ]
                        return TriggerState(
                            trigger_type=TriggerType.PERFECTIONISM,
                            confidence=0.70,
                            evidence=evidence,
                            context={"tool": tool, "similar_commands": similar},
                        )

        return None

    def _detect_confirmation_bias(self) -> Optional[TriggerState]:
        """
        Detect if agent is only seeking confirming evidence.

        Indicators: only running confirming tests, ignoring contradictions.
        """
        if len(self.tool_calls) < 5:
            return None

        # Check for repeated similar tests without variation
        recent = self.tool_calls[-10:]
        test_calls = [c for c in recent if any(t in c.tool_name.lower() for t in ["scan", "test", "check", "probe"])]

        if len(test_calls) >= 5:
            # Check if all tests are the same type
            test_types = set()
            for call in test_calls:
                test_types.add(call.tool_name)

            if len(test_types) == 1:
                test_type = next(iter(test_types))
                evidence = [
                    f"Only one type of test used: {test_type}",
                    "No disconfirming tests detected",
                ]
                return TriggerState(
                    trigger_type=TriggerType.CONFIRMATION_BIAS,
                    confidence=0.70,
                    evidence=evidence,
                    context={"test_type": test_type},
                )

        return None

    def _detect_tool_fixation(self) -> Optional[TriggerState]:
        """
        Detect if agent is fixated on a single tool despite failures.

        Threshold: 5+ calls with same tool, 60%+ failure rate, no alternatives tried.
        """
        if len(self.tool_calls) < 5:
            return None

        tool_usage = defaultdict(list)
        for call in self.tool_calls:
            tool_usage[call.tool_name].append(call)

        for tool, calls in tool_usage.items():
            if len(calls) >= 5:
                failure_rate = sum(1 for c in calls if not c.success) / len(calls)
                if failure_rate >= 0.6:
                    # Check if agent has tried alternative tools
                    alternative_tools = self._get_alternative_tools(tool)
                    tried_alternatives = [t for t in alternative_tools if t in tool_usage]

                    if not tried_alternatives:
                        confidence = 0.75
                    else:
                        confidence = 0.60

                    evidence = [
                        f"Tool {tool} used {len(calls)} times with {failure_rate:.0%} failure rate",
                        f"Alternatives tried: {len(tried_alternatives)}",
                    ]
                    return TriggerState(
                        trigger_type=TriggerType.TOOL_FIXATION,
                        confidence=confidence,
                        evidence=evidence,
                        context={
                            "tool": tool,
                            "usage_count": len(calls),
                            "failure_rate": failure_rate,
                        },
                    )

        return None

    def _get_alternative_tools(self, tool_name: str) -> List[str]:
        """Get alternative tools for a given tool."""
        alternatives = {
            "nmap": ["masscan", "zmap", "rustscan"],
            "gobuster": ["ffuf", "dirb", "wfuzz"],
            "sqlmap": ["manual", "nosqlmap"],
            "hydra": ["medusa", "patator"],
            "gdb": ["lldb", "rr", "frida"],
        }
        return alternatives.get(tool_name.lower(), [])

    def get_intervention(self) -> Optional[Dict]:
        """
        Get intervention recommendation based on detected triggers.

        Returns:
            Dictionary with intervention details or None if no intervention needed.
        """
        triggers = self.check_triggers()

        if not triggers:
            return None

        # Sort by priority (lower number = higher priority)
        triggers.sort(key=lambda t: PRIORITY_ORDER.get(t.trigger_type, 99))
        primary_trigger = triggers[0]

        interventions = {
            TriggerType.REPEATED_FAILURE: {
                "message": "You've tried the same approach multiple times without success.",
                "suggestions": [
                    "Try a fundamentally different technique",
                    "Vary your attack vector",
                    "Consider a different approach category",
                ],
                "action": "redirect",
            },
            TriggerType.NO_PROGRESS: {
                "message": "You've made many calls without producing a candidate output.",
                "suggestions": [
                    "Form a hypothesis and test it",
                    "Step back and map the attack surface",
                    "Document what you've ruled out",
                ],
                "action": "redirect",
            },
            TriggerType.RABBIT_HOLE: {
                "message": "You appear to be going down a rabbit hole.",
                "suggestions": [
                    "Return to the attack surface",
                    "Focus on code reachable from attacker input",
                    "Consider if this path is viable",
                ],
                "action": "redirect",
            },
            TriggerType.KNOWN_BAD_APPROACH: {
                "message": "This approach is known to be ineffective for this target.",
                "suggestions": [
                    "Research the correct approach",
                    "Try a compatible technique",
                    "Verify target type before proceeding",
                ],
                "action": "correct",
            },
            TriggerType.SCOPE_DRIFT: {
                "message": "You are operating outside the authorized scope.",
                "suggestions": [
                    "Return to in-scope targets",
                    "Verify scope before proceeding",
                    "Contact engagement lead if unsure",
                ],
                "action": "halt",
            },
            TriggerType.REWARD_HACKING: {
                "message": "You may be gaming the metrics.",
                "suggestions": [
                    "Verify findings before reporting",
                    "Demonstrate the exploit works",
                    "Follow proper methodology",
                ],
                "action": "redirect",
            },
            TriggerType.OVERTHINKING: {
                "message": "You may be overthinking.",
                "suggestions": [
                    "Take action with available information",
                    "Set a time limit for analysis",
                    "Focus on high-probability paths",
                ],
                "action": "encourage",
            },
            TriggerType.PERFECTIONISM: {
                "message": "You may be overly perfectionist.",
                "suggestions": [
                    "Good enough is sufficient",
                    "Move to the next objective",
                    "Refine later if needed",
                ],
                "action": "encourage",
            },
            TriggerType.CONFIRMATION_BIAS: {
                "message": "You may only be seeking confirming evidence.",
                "suggestions": [
                    "Try to disprove your hypothesis",
                    "Test alternative explanations",
                    "Seek disconfirming evidence",
                ],
                "action": "redirect",
            },
            TriggerType.TOOL_FIXATION: {
                "message": "You may be fixated on a single tool.",
                "suggestions": [
                    "Try an alternative tool",
                    "Diversify your toolkit",
                    "Consider a different approach",
                ],
                "action": "redirect",
            },
        }

        intervention = interventions.get(primary_trigger.trigger_type, {})
        intervention["trigger_type"] = primary_trigger.trigger_type.value
        intervention["confidence"] = primary_trigger.confidence
        intervention["evidence"] = primary_trigger.evidence
        intervention["all_triggers"] = [t.trigger_type.value for t in triggers]

        # Record intervention
        self.intervention_history.append({
            "timestamp": time.time(),
            "trigger": primary_trigger.trigger_type.value,
            "intervention": intervention,
        })

        return intervention

    def should_escalate(self) -> bool:
        """
        Determine if the situation should be escalated to a human.

        Returns:
            True if escalation is recommended.
        """
        triggers = self.check_triggers()

        # Escalate if multiple high-confidence triggers
        high_confidence = [t for t in triggers if t.confidence >= 0.8]
        if len(high_confidence) >= 2:
            return True

        # Escalate on scope drift with high confidence
        for t in triggers:
            if t.trigger_type == TriggerType.SCOPE_DRIFT and t.confidence >= 0.7:
                return True

        # Escalate on reward hacking
        for t in triggers:
            if t.trigger_type == TriggerType.REWARD_HACKING:
                return True

        # Escalate if same trigger persists
        for t in triggers:
            if t.count >= 3:
                return True

        return False

    def get_summary(self) -> Dict:
        """Get a summary of the current state."""
        triggers = self.check_triggers()
        return {
            "total_tool_calls": len(self.tool_calls),
            "active_triggers": len(triggers),
            "trigger_types": [t.trigger_type.value for t in triggers],
            "should_escalate": self.should_escalate(),
            "intervention_count": len(self.intervention_history),
            "candidate_outputs": self.candidate_output_count,
        }

    def load_history(self, tool_calls_data: List[Dict]) -> None:
        """Load tool call history from a list of dictionaries."""
        for data in tool_calls_data:
            self.add_tool_call(ToolCall.from_dict(data))

    def load_from_json(self, filepath: str) -> None:
        """Load tool call history from a JSON file."""
        path = Path(filepath)
        if path.exists():
            with open(path, 'r') as f:
                data = json.load(f)
            self.load_history(data)

    def generate_report(self) -> Dict:
        """Generate a comprehensive analysis report."""
        triggers = self.check_triggers()
        return {
            "summary": self.get_summary(),
            "triggers": [t.to_dict() for t in triggers],
            "technique_summary": self.classifier.get_summary(),
            "intervention_history": self.intervention_history,
            "recommendations": self._generate_recommendations(triggers),
        }

    def _generate_recommendations(self, triggers: List[TriggerState]) -> List[str]:
        """Generate recommendations based on detected triggers."""
        recommendations = []

        for trigger in triggers:
            if trigger.trigger_type == TriggerType.SCOPE_DRIFT:
                recommendations.append("Immediately return to in-scope targets")
            elif trigger.trigger_type == TriggerType.REWARD_HACKING:
                recommendations.append("Enforce verification before reporting findings")
            elif trigger.trigger_type == TriggerType.KNOWN_BAD_APPROACH:
                recommendations.append("Redirect to a viable technique for this target type")
            elif trigger.trigger_type == TriggerType.REPEATED_FAILURE:
                recommendations.append("Try a fundamentally different approach")
            elif trigger.trigger_type == TriggerType.RABBIT_HOLE:
                recommendations.append("Return to the attack surface")
            elif trigger.trigger_type == TriggerType.NO_PROGRESS:
                recommendations.append("Form a hypothesis and test it")
            elif trigger.trigger_type == TriggerType.OVERTHINKING:
                recommendations.append("Take action with available information")
            elif trigger.trigger_type == TriggerType.PERFECTIONISM:
                recommendations.append("Focus on completing the objective")
            elif trigger.trigger_type == TriggerType.CONFIRMATION_BIAS:
                recommendations.append("Seek disconfirming evidence")
            elif trigger.trigger_type == TriggerType.TOOL_FIXATION:
                recommendations.append("Try an alternative tool")

        return recommendations


# Example usage and testing
if __name__ == "__main__":
    detector = TriggerDetector()

    # Set scope
    detector._update_scope(["www.example.com", "192.168.1.0/24"])

    # Simulate some tool calls
    calls = [
        ToolCall(tool_name="nmap", command="-sS -sV 192.168.1.1", success=True, target="192.168.1.1"),
        ToolCall(tool_name="nmap", command="-sS -sV 192.168.1.1", success=False, target="192.168.1.1"),
        ToolCall(tool_name="nmap", command="-sS -sV 192.168.1.1", success=False, target="192.168.1.1"),
        ToolCall(tool_name="nmap", command="-sS -sV 192.168.1.1", success=False, target="192.168.1.1"),
    ]

    for call in calls:
        detector.add_tool_call(call)

    # Check triggers
    triggers = detector.check_triggers()
    print(f"Detected {len(triggers)} trigger(s):")
    for t in triggers:
        print(f"  - {t.trigger_type.value} (confidence: {t.confidence:.2f})")
        for e in t.evidence:
            print(f"    {e}")

    # Get intervention
    intervention = detector.get_intervention()
    if intervention:
        print(f"\nIntervention: {intervention['message']}")

    # Summary
    print(f"\nSummary: {json.dumps(detector.get_summary(), indent=2)}")
