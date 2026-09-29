#!/usr/bin/env python3
"""
Fading Schedule System for Security Coach

Manages fading scaffolding state — tracks intervention history per pattern,
determines appropriate guidance level, and handles level progression
and regression. State persists across sessions.

Usage:
    from fading_schedule import FadingSchedule, FadingState

    schedule = FadingSchedule()
    directive = schedule.next_intervention("repeated_failure", context={})
    schedule.record_outcome("repeated_failure", "success")

Batch restore:
    schedule = FadingSchedule()
    schedule.load_state("fading_state.json")
"""

import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path


class GuidanceLevel(Enum):
    """Three levels of guidance specificity."""
    SPECIFIC = 1    # Exact command or technique
    GENERAL = 2     # Direction or category
    MINIMAL = 3     # Question or prompt


@dataclass
class FadingState:
    """Represents the current fading state for a trigger pattern."""
    pattern_type: str
    intervention_count: int = 0
    current_level: int = 1  # 1=specific, 2=general, 3=minimal
    last_intervention: float = 0.0
    last_outcome: str = ""  # "success", "failure", "neutral"
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    total_successes: int = 0
    total_failures: int = 0
    history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "pattern_type": self.pattern_type,
            "intervention_count": self.intervention_count,
            "current_level": self.current_level,
            "last_intervention": self.last_intervention,
            "last_outcome": self.last_outcome,
            "consecutive_successes": self.consecutive_successes,
            "consecutive_failures": self.consecutive_failures,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FadingState":
        """Create FadingState from dictionary."""
        return cls(
            pattern_type=data.get("pattern_type", ""),
            intervention_count=data.get("intervention_count", 0),
            current_level=data.get("current_level", 1),
            last_intervention=data.get("last_intervention", 0.0),
            last_outcome=data.get("last_outcome", ""),
            consecutive_successes=data.get("consecutive_successes", 0),
            consecutive_failures=data.get("consecutive_failures", 0),
            total_successes=data.get("total_successes", 0),
            total_failures=data.get("total_failures", 0),
            history=data.get("history", []),
        )


class FadingSchedule:
    """
    Manages the fading scaffolding schedule for interventions.

    The schedule reduces intervention specificity over time as the agent
    demonstrates competence, eventually fading to minimal guidance.
    """

    # Minimum seconds between interventions for the same pattern
    MIN_INTERVAL = 300  # 5 minutes

    # Successes needed before progressing to less specific level
    SUCCESS_THRESHOLD = 2

    # Failures needed before regressing to more specific level
    FAILURE_THRESHOLD = 2

    # Maximum interventions before forced progression
    MAX_INTERVENTIONS_BEFORE_PROGRESSION = 3

    # Intervention templates for each pattern at each level
    DIRECTIVES = {
        "repeated_failure": {
            1: {
                "message": "You've tried {technique} {count} times without success. Try {alternative} instead.",
                "example": "You've tried nmap SYN scan 3 times without success. Try a UDP scan instead.",
            },
            2: {
                "message": "The current approach isn't working. Consider a different {category} technique.",
                "example": "The current approach isn't working. Consider a different network enumeration technique.",
            },
            3: {
                "message": "What fundamentally different approach haven't you tried yet?",
                "example": "What fundamentally different approach haven't you tried yet?",
            },
        },
        "no_progress": {
            1: {
                "message": "You've made {count} calls without producing a candidate output. Form a hypothesis and test it with {action}.",
                "example": "You've made 12 calls without producing a candidate output. Form a hypothesis and test it with a targeted scan.",
            },
            2: {
                "message": "Step back and map the attack surface. Identify the most likely entry point and test it.",
                "example": "Step back and map the attack surface. Identify the most likely entry point and test it.",
            },
            3: {
                "message": "What hypothesis can you test right now?",
                "example": "What hypothesis can you test right now?",
            },
        },
        "rabbit_hole": {
            1: {
                "message": "You're analyzing {target} which is outside the attack surface. Return to {in_scope_target}.",
                "example": "You're analyzing the ORM library internals which is outside the attack surface. Return to the application query construction code.",
            },
            2: {
                "message": "Focus on code paths reachable from the attacker-controlled input. The vulnerability is likely in application logic, not dependencies.",
                "example": "Focus on code paths reachable from the attacker-controlled input. The vulnerability is likely in application logic, not dependencies.",
            },
            3: {
                "message": "Is the code you're reading reachable from the attack surface?",
                "example": "Is the code you're reading reachable from the attack surface?",
            },
        },
        "known_bad_approach": {
            1: {
                "message": "{technique} is incompatible with {target_type}. Try {alternative} instead.",
                "example": "SQL injection is incompatible with a NoSQL database. Try NoSQL-specific injection techniques instead.",
            },
            2: {
                "message": "This technique cannot succeed against this target type. Consider {category} instead.",
                "example": "This technique cannot succeed against this target type. Consider client-side attack vectors instead.",
            },
            3: {
                "message": "What attack vectors are viable against this target type?",
                "example": "What attack vectors are viable against this target type?",
            },
        },
        "scope_drift": {
            1: {
                "message": "You're outside the engagement scope. Return to the in-scope targets: {scope}.",
                "example": "You're outside the engagement scope. Return to the in-scope targets: www.example.com and 192.168.1.0/24.",
            },
            2: {
                "message": "Verify your target is in scope before proceeding. The engagement only authorizes {scope_category}.",
                "example": "Verify your target is in scope before proceeding. The engagement only authorizes the production web application.",
            },
            3: {
                "message": "Is your current target in scope?",
                "example": "Is your current target in scope?",
            },
        },
        "reward_hacking": {
            1: {
                "message": "Verify your findings before reporting. Demonstrate that {claim} actually works.",
                "example": "Verify your findings before reporting. Demonstrate that the SQL injection actually extracts data.",
            },
            2: {
                "message": "Claims without evidence are not findings. Follow proper methodology and verify each step.",
                "example": "Claims without evidence are not findings. Follow proper methodology and verify each step.",
            },
            3: {
                "message": "Have you verified this finding?",
                "example": "Have you verified this finding?",
            },
        },
        "overthinking": {
            1: {
                "message": "You have enough information to act. Try {action} now and adjust based on results.",
                "example": "You have enough information to act. Try the most likely attack vector now and adjust based on results.",
            },
            2: {
                "message": "Set a 5-minute timer and commit to an approach. You can gather more data later if needed.",
                "example": "Set a 5-minute timer and commit to an approach. You can gather more data later if needed.",
            },
            3: {
                "message": "What's the next action you can take right now?",
                "example": "What's the next action you can take right now?",
            },
        },
        "perfectionism_bias": {
            1: {
                "message": "Your current approach is sufficient. Move to the next objective instead of refining.",
                "example": "Your current approach is sufficient. Move to the next objective instead of refining.",
            },
            2: {
                "message": "Good enough is sufficient. You can refine later if needed — focus on completing the task.",
                "example": "Good enough is sufficient. You can refine later if needed — focus on completing the task.",
            },
            3: {
                "message": "Is this refinement necessary for the objective?",
                "example": "Is this refinement necessary for the objective?",
            },
        },
        "confirmation_bias": {
            1: {
                "message": "Try to disprove your hypothesis. What evidence would show that {hypothesis} is wrong?",
                "example": "Try to disprove your hypothesis. What evidence would show that the vulnerability is NOT in the authentication module?",
            },
            2: {
                "message": "You've only run confirming tests. Try a test that could fail and see what happens.",
                "example": "You've only run confirming tests. Try a test that could fail and see what happens.",
            },
            3: {
                "message": "What would prove your hypothesis wrong?",
                "example": "What would prove your hypothesis wrong?",
            },
        },
        "tool_fixation": {
            1: {
                "message": "You've tried {tool} {count} times without success. Try {alternative} instead.",
                "example": "You've tried gobuster 6 times without success. Try ffuf with a different wordlist instead.",
            },
            2: {
                "message": "This tool may not be effective for this target. Consider a different {category} approach.",
                "example": "This tool may not be effective for this target. Consider a different directory enumeration approach.",
            },
            3: {
                "message": "What other tools could achieve the same objective?",
                "example": "What other tools could achieve the same objective?",
            },
        },
    }

    def __init__(self, state_file: Optional[str] = None):
        self.states: Dict[str, FadingState] = {}
        self.intervention_history: List[Dict[str, Any]] = []
        self.state_file = state_file

        if state_file and Path(state_file).exists():
            self.load_state(state_file)

    def next_intervention(self, pattern_type: str, context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Get the next intervention directive based on current state.

        Args:
            pattern_type: The trigger pattern type (e.g., "repeated_failure")
            context: Context information for template formatting

        Returns:
            Intervention directive or None if no intervention needed.
        """
        context = context or {}

        # Check if intervention should be given
        if not self.should_intervene(pattern_type):
            return None

        # Get or create state for this pattern
        if pattern_type not in self.states:
            self.states[pattern_type] = FadingState(pattern_type=pattern_type)

        state = self.states[pattern_type]

        # Check minimum interval
        if time.time() - state.last_intervention < self.MIN_INTERVAL:
            return None

        # Get directive for current level
        directive = self._generate_directive(pattern_type, state.current_level, context)

        # Update state
        state.intervention_count += 1
        state.last_intervention = time.time()
        state.history.append({
            "timestamp": time.time(),
            "level": state.current_level,
            "directive": directive,
            "outcome": "pending",
        })

        # Record intervention
        self.intervention_history.append({
            "timestamp": time.time(),
            "pattern_type": pattern_type,
            "level": state.current_level,
            "directive": directive,
        })

        # Auto-save if state file is configured
        if self.state_file:
            self.save_state(self.state_file)

        return directive

    def _generate_directive(self, pattern_type: str, level: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a directive for a pattern at a specific level."""
        pattern_directives = self.DIRECTIVES.get(pattern_type, {})
        level_directive = pattern_directives.get(level, {"message": "", "example": ""})

        message = level_directive.get("message", "")
        example = level_directive.get("example", "")

        # Format with context if provided
        if context:
            try:
                message = message.format(**context)
            except (KeyError, ValueError):
                pass  # Use template as-is if formatting fails

        return {
            "pattern_type": pattern_type,
            "level": level,
            "level_name": self._level_name(level),
            "message": message,
            "example": example,
            "timestamp": time.time(),
        }

    def _level_name(self, level: int) -> str:
        """Get the name for a guidance level."""
        names = {1: "specific", 2: "general", 3: "minimal"}
        return names.get(level, "unknown")

    def record_outcome(self, pattern_type: str, outcome: str) -> None:
        """
        Record the outcome of an intervention.

        Args:
            pattern_type: The trigger pattern type
            outcome: "success", "failure", or "neutral"
        """
        if pattern_type not in self.states:
            self.states[pattern_type] = FadingState(pattern_type=pattern_type)

        state = self.states[pattern_type]
        state.last_outcome = outcome

        # Update counters
        if outcome == "success":
            state.consecutive_successes += 1
            state.consecutive_failures = 0
            state.total_successes += 1
        elif outcome == "failure":
            state.consecutive_failures += 1
            state.consecutive_successes = 0
            state.total_failures += 1

        # Check for progression (fade out)
        if self._should_progress(state):
            if state.current_level < 3:
                state.current_level += 1
                state.consecutive_successes = 0

        # Check for regression (fade in)
        if self._should_regress(state):
            if state.current_level > 1:
                state.current_level -= 1
                state.consecutive_failures = 0

        # Update history
        if state.history:
            state.history[-1]["outcome"] = outcome

        # Auto-save if state file is configured
        if self.state_file:
            self.save_state(self.state_file)

    def _should_progress(self, state: FadingState) -> bool:
        """Determine if the level should progress (become less specific)."""
        # Progress after consecutive successes
        if state.consecutive_successes >= self.SUCCESS_THRESHOLD:
            return True

        # Force progression after max interventions
        if state.intervention_count >= self.MAX_INTERVENTIONS_BEFORE_PROGRESSION:
            if state.last_outcome != "failure":
                return True

        return False

    def _should_regress(self, state: FadingState) -> bool:
        """Determine if the level should regress (become more specific)."""
        # Regress after consecutive failures
        if state.consecutive_failures >= self.FAILURE_THRESHOLD:
            return True

        return False

    def should_intervene(self, pattern_type: str) -> bool:
        """
        Determine if an intervention should be given.

        Args:
            pattern_type: The trigger pattern type

        Returns:
            True if intervention should be given.
        """
        if pattern_type not in self.states:
            return True  # First time seeing this pattern

        state = self.states[pattern_type]

        # Don't intervene if at minimal level and agent is independent
        if state.current_level >= 3 and state.consecutive_successes >= 3:
            return False

        # Check minimum interval
        if time.time() - state.last_intervention < self.MIN_INTERVAL:
            return False

        return True

    def get_state(self, pattern_type: str) -> Optional[FadingState]:
        """Get the current state for a pattern."""
        return self.states.get(pattern_type)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all fading states."""
        return {
            "total_patterns": len(self.states),
            "patterns": {
                pattern: {
                    "intervention_count": state.intervention_count,
                    "current_level": state.current_level,
                    "level_name": self._level_name(state.current_level),
                    "consecutive_successes": state.consecutive_successes,
                    "consecutive_failures": state.consecutive_failures,
                    "total_successes": state.total_successes,
                    "total_failures": state.total_failures,
                    "success_rate": state.total_successes / max(state.intervention_count, 1),
                }
                for pattern, state in self.states.items()
            },
            "total_interventions": len(self.intervention_history),
        }

    def get_fading_progress(self, pattern_type: str) -> Dict[str, Any]:
        """
        Get the fading progress for a pattern.

        Args:
            pattern_type: The trigger pattern type

        Returns:
            Dictionary with progress information.
        """
        if pattern_type not in self.states:
            return {
                "pattern_type": pattern_type,
                "current_level": 1,
                "target_level": 3,
                "progress": 0.0,
                "interventions": 0,
            }

        state = self.states[pattern_type]
        progress = (state.current_level - 1) / 2.0  # 0.0 to 1.0

        return {
            "pattern_type": pattern_type,
            "current_level": state.current_level,
            "level_name": self._level_name(state.current_level),
            "target_level": 3,
            "progress": progress,
            "interventions": state.intervention_count,
            "success_rate": state.total_successes / max(state.intervention_count, 1),
        }

    def reset(self) -> None:
        """Reset all fading states."""
        self.states.clear()
        self.intervention_history.clear()

    def reset_pattern(self, pattern_type: str) -> None:
        """Reset state for a specific pattern."""
        if pattern_type in self.states:
            del self.states[pattern_type]

    def save_state(self, filepath: Optional[str] = None) -> None:
        """
        Save fading state to disk.

        Args:
            filepath: Path to save state file. Uses instance state_file if not provided.
        """
        path = filepath or self.state_file
        if not path:
            return

        data = {
            "states": {pattern: state.to_dict() for pattern, state in self.states.items()},
            "intervention_history": self.intervention_history,
            "saved_at": time.time(),
        }

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_state(self, filepath: Optional[str] = None) -> None:
        """
        Load fading state from disk.

        Args:
            filepath: Path to load state file. Uses instance state_file if not provided.
        """
        path = filepath or self.state_file
        if not path or not Path(path).exists():
            return

        with open(path, 'r') as f:
            data = json.load(f)

        self.states = {
            pattern: FadingState.from_dict(state_data)
            for pattern, state_data in data.get("states", {}).items()
        }
        self.intervention_history = data.get("intervention_history", [])

    def should_escalate(self, pattern_type: str) -> bool:
        """
        Determine if a pattern should be escalated to the user.

        Args:
            pattern_type: The trigger pattern type

        Returns:
            True if escalation is recommended.
        """
        if pattern_type not in self.states:
            return False

        state = self.states[pattern_type]

        # Escalate if 3+ interventions for same pattern
        if state.intervention_count >= 3:
            return True

        # Escalate if regression to specific level twice
        if state.consecutive_failures >= 2 and state.current_level == 1:
            return True

        # Escalate if no progress after multiple interventions
        if state.intervention_count >= 3 and state.total_successes == 0:
            return True

        return False


# Example usage and testing
if __name__ == "__main__":
    schedule = FadingSchedule()

    print("=== Fading Schedule Demo ===\n")

    # Simulate interventions for repeated_failure
    pattern = "repeated_failure"

    # First intervention (specific)
    directive = schedule.next_intervention(pattern, {
        "technique": "nmap SYN scan",
        "count": 3,
        "alternative": "UDP scan",
    })
    print(f"Intervention 1 ({directive['level_name']}):")
    print(f"  {directive['message']}\n")

    # Record success
    schedule.record_outcome(pattern, "success")

    # Second intervention (still specific, need 2 successes)
    directive = schedule.next_intervention(pattern, {
        "technique": "nmap SYN scan",
        "count": 3,
        "alternative": "UDP scan",
    })
    if directive:
        print(f"Intervention 2 ({directive['level_name']}):")
        print(f"  {directive['message']}\n")

    # Record another success -> should progress to general
    schedule.record_outcome(pattern, "success")

    # Third intervention (should be general)
    directive = schedule.next_intervention(pattern, {
        "technique": "nmap SYN scan",
        "count": 3,
        "alternative": "UDP scan",
    })
    if directive:
        print(f"Intervention 3 ({directive['level_name']}):")
        print(f"  {directive['message']}\n")

    # Record success -> should progress to minimal
    schedule.record_outcome(pattern, "success")

    # Fourth intervention (should be minimal)
    directive = schedule.next_intervention(pattern, {})
    if directive:
        print(f"Intervention 4 ({directive['level_name']}):")
        print(f"  {directive['message']}\n")

    # Print summary
    print("=== Summary ===")
    summary = schedule.get_summary()
    for pattern, data in summary["patterns"].items():
        print(f"{pattern}:")
        print(f"  Interventions: {data['intervention_count']}")
        print(f"  Current level: {data['level_name']} ({data['current_level']})")
        print(f"  Success rate: {data['success_rate']:.0%}")
