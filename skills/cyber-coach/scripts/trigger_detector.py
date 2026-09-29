#!/usr/bin/env python3
"""
Trigger Detection System for Cyber Coach

Detects when agents are stuck, going down rabbit holes, or using
ineffective approaches during penetration testing engagements.

Usage:
    from trigger_detector import TriggerDetector, ToolCall, TriggerState

    detector = TriggerDetector()
    detector.add_tool_call(ToolCall(...))
    triggers = detector.check_triggers()
    intervention = detector.get_intervention()
"""

import re
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
from collections import defaultdict


class TriggerType(Enum):
    """Types of triggers that can be detected."""
    RABBIT_HOLE = "rabbit_hole"
    KNOWN_BAD_APPROACH = "known_bad_approach"
    SCOPE_DRIFT = "scope_drift"
    REWARD_HACKING = "reward_hacking"
    OVERTHINKING = "overthinking"
    PERFECTIONISM = "perfectionism"


@dataclass
class ToolCall:
    """Represents a single tool call made by the agent."""
    tool_name: str
    parameters: Dict
    timestamp: float = field(default_factory=time.time)
    result: str = ""
    success: bool = True
    duration: float = 0.0
    target: str = ""
    command: str = ""


@dataclass
class TriggerState:
    """Represents the current state of trigger detection."""
    trigger_type: TriggerType
    confidence: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)
    first_detected: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    count: int = 1
    context: Dict = field(default_factory=dict)


class TriggerDetector:
    """Detects problematic patterns in agent behavior."""

    # Known bad approaches and their patterns
    KNOWN_BAD_APPROACHES = {
        "brute_force_login": {
            "patterns": [r"hydra", r"medusa", r"brute", r"wordlist.*login"],
            "description": "Brute forcing login credentials without trying default creds first",
        },
        "outdated_exploit": {
            "patterns": [r"exploit.*201[0-5]", r"ms08-067", r"ms17-010.*old"],
            "description": "Using outdated exploits without checking for patches",
        },
        "noisy_scan": {
            "patterns": [r"nmap.*-T5", r"masscan.*1000000"],
            "description": "Using overly aggressive scanning that may trigger alerts",
        },
        "ignore_scope": {
            "patterns": [r"scan.*(?!scope)", r"attack.*(?!authorized)"],
            "description": "Operating outside authorized scope",
        },
    }

    # Rabbit hole indicators
    RABBIT_HOLE_INDICATORS = {
        "repeated_failures": 3,  # Number of consecutive failures
        "time_threshold": 300,   # 5 minutes
        "tool_diversity_min": 2,  # Minimum different tools before it's a rabbit hole
    }

    # Scope keywords
    SCOPE_KEYWORDS = {
        "authorized", "scope", "allowed", "permitted", "authorized_targets",
        "in_scope", "out_of_scope", "excluded"
    }

    def __init__(self):
        self.tool_calls: List[ToolCall] = []
        self.triggers: Dict[TriggerType, TriggerState] = {}
        self.scope_targets: Set[str] = set()
        self.failed_attempts: Dict[str, List[ToolCall]] = defaultdict(list)
        self.intervention_history: List[Dict] = []

    def add_tool_call(self, tool_call: ToolCall) -> None:
        """Add a tool call to the detector's history."""
        self.tool_calls.append(tool_call)

        # Track failed attempts
        if not tool_call.success:
            key = f"{tool_call.tool_name}:{tool_call.target}"
            self.failed_attempts[key].append(tool_call)

        # Update scope if mentioned
        if "scope" in tool_call.parameters:
            self._update_scope(tool_call.parameters["scope"])

    def _update_scope(self, scope: any) -> None:
        """Update the authorized scope targets."""
        if isinstance(scope, list):
            self.scope_targets.update(scope)
        elif isinstance(scope, str):
            self.scope_targets.add(scope)

    def check_triggers(self) -> List[TriggerState]:
        """Check all trigger conditions and return active triggers."""
        active_triggers = []

        # Check each trigger type
        rabbit_hole = self._detect_rabbit_hole()
        if rabbit_hole:
            active_triggers.append(rabbit_hole)

        bad_approach = self._detect_known_bad_approach()
        if bad_approach:
            active_triggers.append(bad_approach)

        scope_drift = self._detect_scope_drift()
        if scope_drift:
            active_triggers.append(scope_drift)

        reward_hacking = self._detect_reward_hacking()
        if reward_hacking:
            active_triggers.append(reward_hacking)

        overthinking = self._detect_overthinking()
        if overthinking:
            active_triggers.append(overthinking)

        perfectionism = self._detect_perfectionism()
        if perfectionism:
            active_triggers.append(perfectionism)

        return active_triggers

    def _detect_rabbit_hole(self) -> Optional[TriggerState]:
        """
        Detect if agent is going down a rabbit hole.

        Indicators:
        - Multiple consecutive failures with same tool/target
        - Long time spent without progress
        - Repeating similar failed commands
        """
        if len(self.tool_calls) < 3:
            return None

        # Check for repeated failures
        for key, attempts in self.failed_attempts.items():
            if len(attempts) >= self.RABBIT_HOLE_INDICATORS["repeated_failures"]:
                # Check time window
                recent = [a for a in attempts if time.time() - a.timestamp < self.RABBIT_HOLE_INDICATORS["time_threshold"]]
                if len(recent) >= self.RABBIT_HOLE_INDICATORS["repeated_failures"]:
                    # Check tool diversity (are they trying different approaches?)
                    tool_names = set(a.tool_name for a in recent)
                    if len(tool_names) >= self.RABBIT_HOLE_INDICATORS["tool_diversity_min"]:
                        evidence = [
                            f"Multiple failed attempts ({len(recent)}) for {key}",
                            f"Time window: {self.RABBIT_HOLE_INDICATORS['time_threshold']}s",
                            f"Tools used: {', '.join(tool_names)}",
                        ]
                        return TriggerState(
                            trigger_type=TriggerType.RABBIT_HOLE,
                            confidence=min(0.5 + len(recent) * 0.1, 0.95),
                            evidence=evidence,
                            context={"failed_attempts": len(recent), "key": key},
                        )

        # Check for long-running without progress
        if len(self.tool_calls) >= 5:
            recent_calls = self.tool_calls[-5:]
            time_span = recent_calls[-1].timestamp - recent_calls[0].timestamp
            if time_span > self.RABBIT_HOLE_INDICATORS["time_threshold"]:
                # Check if all recent calls failed
                if not any(c.success for c in recent_calls):
                    evidence = [
                        f"No successful operations in {time_span:.0f}s",
                        f"Last {len(recent_calls)} operations failed",
                    ]
                    return TriggerState(
                        trigger_type=TriggerType.RABBIT_HOLE,
                        confidence=0.7,
                        evidence=evidence,
                        context={"time_span": time_span},
                    )

        return None

    def _detect_known_bad_approach(self) -> Optional[TriggerState]:
        """
        Detect if agent is using known bad approaches.

        Checks for:
        - Brute forcing without trying defaults first
        - Using outdated exploits
        - Overly aggressive scanning
        """
        for approach_name, approach_info in self.KNOWN_BAD_APPROACHES.items():
            for call in self.tool_calls[-10:]:  # Check last 10 calls
                command = call.command.lower()
                for pattern in approach_info["patterns"]:
                    if re.search(pattern, command):
                        evidence = [
                            f"Detected pattern: {pattern}",
                            f"Approach: {approach_info['description']}",
                            f"Command: {call.command[:100]}",
                        ]
                        return TriggerState(
                            trigger_type=TriggerType.KNOWN_BAD_APPROACH,
                            confidence=0.8,
                            evidence=evidence,
                            context={"approach": approach_name, "pattern": pattern},
                        )

        return None

    def _detect_scope_drift(self) -> Optional[TriggerState]:
        """
        Detect if agent is drifting outside authorized scope.

        Checks for:
        - Targeting systems not in scope
        - Scanning excluded IP ranges
        - Accessing unauthorized resources
        """
        if not self.scope_targets:
            return None

        for call in self.tool_calls[-5:]:
            target = call.target.lower()
            if not target:
                continue

            # Check if target is in scope
            in_scope = any(
                scope_target.lower() in target or target in scope_target.lower()
                for scope_target in self.scope_targets
            )

            if not in_scope:
                # Check if it's a legitimate related target (e.g., same subnet)
                # For now, flag any out-of-scope target
                evidence = [
                    f"Target '{call.target}' not in authorized scope",
                    f"Authorized targets: {', '.join(list(self.scope_targets)[:5])}",
                ]
                return TriggerState(
                    trigger_type=TriggerType.SCOPE_DRIFT,
                    confidence=0.75,
                    evidence=evidence,
                    context={"target": call.target, "scope": list(self.scope_targets)},
                )

        return None

    def _detect_reward_hacking(self) -> Optional[TriggerState]:
        """
        Detect if agent is reward hacking (gaming the metrics).

        Indicators:
        - Repeatedly running same command expecting different result
        - Modifying test conditions to pass
        - Skipping verification steps
        - Focusing on quantity over quality
        """
        if len(self.tool_calls) < 5:
            return None

        # Check for repeated identical commands
        recent_commands = [c.command for c in self.tool_calls[-10:]]
        command_counts = defaultdict(int)
        for cmd in recent_commands:
            command_counts[cmd] += 1

        for cmd, count in command_counts.items():
            if count >= 3:
                evidence = [
                    f"Same command executed {count} times",
                    f"Command: {cmd[:100]}",
                    "Possible reward hacking or stuck loop",
                ]
                return TriggerState(
                    trigger_type=TriggerType.REWARD_HACKING,
                    confidence=0.6,
                    evidence=evidence,
                    context={"command": cmd, "count": count},
                )

        # Check for skipping verification (exploiting without verifying)
        exploit_calls = [c for c in self.tool_calls if "exploit" in c.tool_name.lower()]
        if len(exploit_calls) >= 2:
            # Check if verification steps follow exploitation
            last_exploit_idx = max(i for i, c in enumerate(self.tool_calls) if "exploit" in c.tool_name.lower())
            post_exploit = self.tool_calls[last_exploit_idx:]
            verification_tools = [c for c in post_exploit if any(v in c.tool_name.lower() for v in ["verify", "validate", "confirm", "check"])]
            if not verification_tools:
                evidence = [
                    "Exploitation without verification",
                    f"Last exploit: {exploit_calls[-1].command[:100]}",
                    "No verification steps detected",
                ]
                return TriggerState(
                    trigger_type=TriggerType.REWARD_HACKING,
                    confidence=0.5,
                    evidence=evidence,
                    context={"exploit_command": exploit_calls[-1].command},
                )

        return None

    def _detect_overthinking(self) -> Optional[TriggerState]:
        """
        Detect if agent is overthinking (excessive analysis without action).

        Indicators:
        - Too many reconnaissance commands without exploitation
        - Repeated information gathering
        - Long pauses between actions
        - Excessive planning without execution
        """
        if len(self.tool_calls) < 10:
            return None

        recent_calls = self.tool_calls[-10:]
        recon_tools = {"nmap", "masscan", "gobuster", "ffuf", "nikto", "dirb", "whatweb", "amass", "subfinder"}

        recon_count = sum(1 for c in recent_calls if c.tool_name.lower() in recon_tools)
        if recon_count >= 7:  # 70% of recent calls are recon
            evidence = [
                f"Excessive reconnaissance: {recon_count}/{len(recent_calls)} recent calls",
                "Possible overthinking or analysis paralysis",
            ]
            return TriggerState(
                trigger_type=TriggerType.OVERTHINKING,
                confidence=0.6,
                evidence=evidence,
                context={"recon_count": recon_count, "total_recent": len(recent_calls)},
            )

        # Check for long duration calls (overthinking)
        long_calls = [c for c in recent_calls if c.duration > 60]  # Calls > 60 seconds
        if len(long_calls) >= 3:
            evidence = [
                f"Multiple long-running operations: {len(long_calls)}",
                f"Average duration: {sum(c.duration for c in long_calls)/len(long_calls):.1f}s",
            ]
            return TriggerState(
                trigger_type=TriggerType.OVERTHINKING,
                confidence=0.5,
                evidence=evidence,
                context={"long_calls": len(long_calls)},
            )

        return None

    def _detect_perfectionism(self) -> Optional[TriggerState]:
        """
        Detect if agent is being overly perfectionist.

        Indicators:
        - Repeatedly refining same output
        - Excessive validation steps
        - Not moving forward due to minor issues
        - Over-engineering solutions
        """
        if len(self.tool_calls) < 8:
            return None

        # Check for repeated similar commands (refinement)
        recent_commands = [c.command for c in self.tool_calls[-8:]]
        # Group by tool name
        tool_commands = defaultdict(list)
        for c in self.tool_calls[-8:]:
            tool_commands[c.tool_name].append(c.command)

        for tool, commands in tool_commands.items():
            if len(commands) >= 4:
                # Check if commands are similar (refining)
                # Simple check: same command with minor variations
                base_cmd = commands[0][:50]  # First 50 chars
                similar = sum(1 for c in commands if c[:50] == base_cmd)
                if similar >= 3:
                    evidence = [
                        f"Repeated refinement of {tool} commands",
                        f"Similar commands: {similar}/{len(commands)}",
                        "Possible perfectionism or stuck loop",
                    ]
                    return TriggerState(
                        trigger_type=TriggerType.PERFECTIONISM,
                        confidence=0.55,
                        evidence=evidence,
                        context={"tool": tool, "similar_commands": similar},
                    )

        return None

    def get_intervention(self) -> Optional[Dict]:
        """
        Get intervention recommendation based on detected triggers.

        Returns:
            Dictionary with intervention details or None if no intervention needed.
        """
        triggers = self.check_triggers()

        if not triggers:
            return None

        # Sort by confidence
        triggers.sort(key=lambda t: t.confidence, reverse=True)
        primary_trigger = triggers[0]

        interventions = {
            TriggerType.RABBIT_HOLE: {
                "message": "You appear to be stuck in a rabbit hole. Consider:",
                "suggestions": [
                    "Take a step back and reassess your approach",
                    "Try a different tool or technique",
                    "Consult documentation or references",
                    "Consider if this attack path is viable",
                    "Move to a different target or service",
                ],
                "action": "redirect",
            },
            TriggerType.KNOWN_BAD_APPROACH: {
                "message": "You are using a known ineffective approach. Consider:",
                "suggestions": [
                    "Try default credentials first before brute forcing",
                    "Check for patches before using old exploits",
                    "Use less aggressive scanning options",
                    "Verify target is in scope before proceeding",
                ],
                "action": "correct",
            },
            TriggerType.SCOPE_DRIFT: {
                "message": "You may be operating outside authorized scope. Consider:",
                "suggestions": [
                    "Verify target is in authorized scope",
                    "Check scope documentation",
                    "Confirm with engagement lead if unsure",
                    "Document any scope changes",
                ],
                "action": "halt",
            },
            TriggerType.REWARD_HACKING: {
                "message": "You may be gaming the metrics. Consider:",
                "suggestions": [
                    "Focus on quality over quantity",
                    "Verify findings before reporting",
                    "Follow proper methodology",
                    "Document your process",
                ],
                "action": "redirect",
            },
            TriggerType.OVERTHINKING: {
                "message": "You may be overthinking. Consider:",
                "suggestions": [
                    "Take action with available information",
                    "You can always gather more data later",
                    "Focus on high-probability attack paths",
                    "Set a time limit for analysis",
                ],
                "action": "encourage",
            },
            TriggerType.PERFECTIONISM: {
                "message": "You may be overly perfectionist. Consider:",
                "suggestions": [
                    "Good enough is often sufficient",
                    "You can refine later if needed",
                    "Focus on completing the objective",
                    "Don't let perfect be the enemy of good",
                ],
                "action": "encourage",
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
        }


class TechniqueClassifier:
    """Classifies penetration testing techniques from tool calls."""

    TECHNIQUE_PATTERNS = {
        "reconnaissance": [
            r"nmap", r"masscan", r"amass", r"subfinder", r"whatweb",
            r"dnsenum", r"theharvester", r"shodan", r"censys"
        ],
        "enumeration": [
            r"gobuster", r"ffuf", r"dirb", r"nikto", r"enum4linux",
            r"smbmap", r"ldapsearch", r"rpcclient"
        ],
        "vulnerability_scanning": [
            r"nuclei", r"nessus", r"openvas", r"nexpose", r"qualys"
        ],
        "exploitation": [
            r"metasploit", r"msfconsole", r"exploit", r"sqlmap",
            r"beef", r"responder", r"impacket"
        ],
        "post_exploitation": [
            r"mimikatz", r"secretsdump", r"psexec", r"wmiexec",
            r"smbexec", r"getsystem", r"token"
        ],
        "password_attacks": [
            r"hydra", r"medusa", r"john", r"hashcat", r"cewl",
            r"crunch", r"rcrack"
        ],
        "wireless_attacks": [
            r"aircrack", r"reaver", r"wifite", r"fluxion", r"airgeddon"
        ],
        "web_attacks": [
            r"burp", r"zap", r"sqlmap", r"xsstrike", r"commix",
            r"wpscan", r"joomscan"
        ],
        "social_engineering": [
            r"setoolkit", r"gophish", r"evilginx", r"phishing"
        ],
        "reporting": [
            r"cherrytree", r"keepnote", r"dradis", r"serpico"
        ],
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
