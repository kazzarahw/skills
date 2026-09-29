#!/usr/bin/env python3
"""
Fading Schedule System for Cyber Coach

Implements a fading scaffolding schedule that reduces intervention
specificity over time as the agent demonstrates competence.

Usage:
    from fading_schedule import FadingSchedule, FadingState

    schedule = FadingSchedule()
    state = FadingState(trigger_type="rabbit_hole", count=0)
    directive = schedule.next_intervention("rabbit_hole", context={})
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


@dataclass
class FadingState:
    """Represents the current fading state for a trigger type."""
    trigger_type: str
    count: int = 0
    last_intervention: float = 0.0
    specificity_level: int = 0  # 0 = most specific, 3 = least specific
    success_count: int = 0
    failure_count: int = 0
    history: List[Dict] = field(default_factory=list)


class FadingSchedule:
    """
    Manages the fading scaffolding schedule for interventions.

    The schedule reduces intervention specificity over time as the agent
    demonstrates competence, eventually fading to minimal guidance.
    """

    # Specificity levels: 0 = most specific, 3 = least specific
    SPECIFICITY_LEVELS = {
        0: "specific",      # Detailed step-by-step guidance
        1: "moderate",      # General guidance with examples
        2: "minimal",       # Brief hints and reminders
        3: "independent",   # Agent works independently
    }

    # Intervention templates for each trigger type at each specificity level
    DIRECTIVES = {
        "rabbit_hole": {
            0: {
                "message": "You appear to be stuck. Here's what to do:",
                "steps": [
                    "1. Stop current approach immediately",
                    "2. Review what you've tried so far",
                    "3. Identify why it's not working",
                    "4. Choose a completely different approach",
                    "5. If still stuck after 2 more attempts, escalate",
                ],
                "example": "Instead of continuing with {current_tool}, try {alternative_tool} or move to a different target.",
            },
            1: {
                "message": "You seem to be going in circles. Consider:",
                "steps": [
                    "Take a break from this approach",
                    "Try something different",
                    "Reassess your assumptions",
                ],
                "example": "Have you considered trying {alternative_tool}?",
            },
            2: {
                "message": "You might be stuck.",
                "steps": [
                    "Try a different approach",
                ],
                "example": "",
            },
            3: {
                "message": "",
                "steps": [],
                "example": "",
            },
        },
        "known_bad_approach": {
            0: {
                "message": "This approach is known to be ineffective. Here's a better way:",
                "steps": [
                    "1. Stop using {current_tool} for this purpose",
                    "2. Research the correct approach",
                    "3. Try the recommended alternative: {alternative_tool}",
                    "4. Verify the new approach works",
                ],
                "example": "Instead of {current_tool}, use {alternative_tool} with these parameters: {parameters}",
            },
            1: {
                "message": "This approach may not work. Consider:",
                "steps": [
                    "Research better alternatives",
                    "Try {alternative_tool}",
                ],
                "example": "",
            },
            2: {
                "message": "Consider a different approach.",
                "steps": [],
                "example": "",
            },
            3: {
                "message": "",
                "steps": [],
                "example": "",
            },
        },
        "scope_drift": {
            0: {
                "message": "WARNING: You may be outside authorized scope. Here's what to do:",
                "steps": [
                    "1. STOP all activity immediately",
                    "2. Review the authorized scope: {scope}",
                    "3. Verify if {target} is in scope",
                    "4. If unsure, contact the engagement lead",
                    "5. Document any scope concerns",
                ],
                "example": "Target {target} is not in the authorized scope: {scope}",
            },
            1: {
                "message": "Check your scope. Consider:",
                "steps": [
                    "Verify target is authorized",
                    "Review scope documentation",
                ],
                "example": "",
            },
            2: {
                "message": "Verify scope before proceeding.",
                "steps": [],
                "example": "",
            },
            3: {
                "message": "",
                "steps": [],
                "example": "",
            },
        },
        "reward_hacking": {
            0: {
                "message": "You may be gaming the metrics. Here's how to improve:",
                "steps": [
                    "1. Focus on quality over quantity",
                    "2. Verify each finding before reporting",
                    "3. Follow proper methodology",
                    "4. Document your process thoroughly",
                    "5. Ensure findings are reproducible",
                ],
                "example": "Instead of repeating {command}, verify the result and document your findings.",
            },
            1: {
                "message": "Focus on quality. Consider:",
                "steps": [
                    "Verify your findings",
                    "Follow methodology",
                ],
                "example": "",
            },
            2: {
                "message": "Ensure quality over quantity.",
                "steps": [],
                "example": "",
            },
            3: {
                "message": "",
                "steps": [],
                "example": "",
            },
        },
        "overthinking": {
            0: {
                "message": "You may be overthinking. Here's how to proceed:",
                "steps": [
                    "1. You have enough information to act",
                    "2. Take action with current knowledge",
                    "3. You can gather more data later if needed",
                    "4. Set a 5-minute timer and decide",
                    "5. Remember: done is better than perfect",
                ],
                "example": "Based on your recon, try {suggested_action} now.",
            },
            1: {
                "message": "Don't overthink. Consider:",
                "steps": [
                    "Take action now",
                    "Gather more data only if needed",
                ],
                "example": "",
            },
            2: {
                "message": "Take action with available information.",
                "steps": [],
                "example": "",
            },
            3: {
                "message": "",
                "steps": [],
                "example": "",
            },
        },
        "perfectionism": {
            0: {
                "message": "You may be overly perfectionist. Here's how to proceed:",
                "steps": [
                    "1. Good enough is often sufficient",
                    "2. You can refine later if needed",
                    "3. Focus on completing the objective",
                    "4. Set a time limit for this task",
                    "5. Move forward even if not perfect",
                ],
                "example": "Your current approach is sufficient. Move to the next step.",
            },
            1: {
                "message": "Don't let perfect be the enemy of good. Consider:",
                "steps": [
                    "Good enough is sufficient",
                    "Move forward",
                ],
                "example": "",
            },
            2: {
                "message": "Good enough is sufficient.",
                "steps": [],
                "example": "",
            },
            3: {
                "message": "",
                "steps": [],
                "example": "",
            },
        },
    }

    # Thresholds for moving between specificity levels
    SUCCESS_THRESHOLD = 3  # Successes before reducing specificity
    FAILURE_THRESHOLD = 2  # Failures before increasing specificity
    MIN_INTERVAL = 60  # Minimum seconds between interventions

    def __init__(self):
        self.states: Dict[str, FadingState] = {}
        self.intervention_history: List[Dict] = []

    def next_intervention(self, trigger: str, context: Dict) -> Optional[Dict]:
        """
        Get the next intervention directive based on current state.

        Args:
            trigger: The trigger type (e.g., "rabbit_hole")
            context: Context information for the intervention

        Returns:
            Intervention directive or None if no intervention needed.
        """
        # Get or create state for this trigger
        if trigger not in self.states:
            self.states[trigger] = FadingState(trigger_type=trigger)

        state = self.states[trigger]

        # Check minimum interval
        if time.time() - state.last_intervention < self.MIN_INTERVAL:
            return None

        # Get directive for current specificity level
        directive = self._get_directive(trigger, state.specificity_level, context)

        # Update state
        state.count += 1
        state.last_intervention = time.time()
        state.history.append({
            "timestamp": time.time(),
            "specificity_level": state.specificity_level,
            "directive": directive,
        })

        # Record intervention
        self.intervention_history.append({
            "timestamp": time.time(),
            "trigger": trigger,
            "specificity_level": state.specificity_level,
            "directive": directive,
        })

        return directive

    def _get_directive(self, trigger: str, level: int, context: Dict) -> Dict:
        """Get the directive for a trigger at a specific level."""
        trigger_directives = self.DIRECTIVES.get(trigger, {})
        level_directive = trigger_directives.get(level, {})

        # Format the directive with context
        message = level_directive.get("message", "")
        steps = level_directive.get("steps", [])
        example = level_directive.get("example", "")

        # Replace placeholders in message and example
        if context:
            try:
                message = message.format(**context)
                example = example.format(**context) if example else ""
            except (KeyError, ValueError):
                # If formatting fails, use original text
                pass

        return {
            "trigger": trigger,
            "specificity_level": level,
            "specificity_name": self.SPECIFICITY_LEVELS.get(level, "unknown"),
            "message": message,
            "steps": steps,
            "example": example,
            "timestamp": time.time(),
        }

    def record_success(self, trigger: str) -> None:
        """Record a successful intervention outcome."""
        if trigger not in self.states:
            self.states[trigger] = FadingState(trigger_type=trigger)

        state = self.states[trigger]
        state.success_count += 1

        # Check if we should reduce specificity (fade)
        if state.success_count >= self.SUCCESS_THRESHOLD:
            if state.specificity_level < 3:
                state.specificity_level += 1
                state.success_count = 0
                state.failure_count = 0

    def record_failure(self, trigger: str) -> None:
        """Record a failed intervention outcome."""
        if trigger not in self.states:
            self.states[trigger] = FadingState(trigger_type=trigger)

        state = self.states[trigger]
        state.failure_count += 1

        # Check if we should increase specificity
        if state.failure_count >= self.FAILURE_THRESHOLD:
            if state.specificity_level > 0:
                state.specificity_level -= 1
                state.success_count = 0
                state.failure_count = 0

    def reset(self) -> None:
        """Reset all fading states."""
        self.states.clear()
        self.intervention_history.clear()

    def get_state(self, trigger: str) -> Optional[FadingState]:
        """Get the current state for a trigger."""
        return self.states.get(trigger)

    def get_summary(self) -> Dict:
        """Get a summary of all fading states."""
        return {
            "total_triggers": len(self.states),
            "triggers": {
                trigger: {
                    "count": state.count,
                    "specificity_level": state.specificity_level,
                    "specificity_name": self.SPECIFICITY_LEVELS.get(state.specificity_level, "unknown"),
                    "success_count": state.success_count,
                    "failure_count": state.failure_count,
                }
                for trigger, state in self.states.items()
            },
            "total_interventions": len(self.intervention_history),
        }

    def should_intervene(self, trigger: str) -> bool:
        """
        Determine if an intervention should be given.

        Args:
            trigger: The trigger type

        Returns:
            True if intervention should be given.
        """
        if trigger not in self.states:
            return True  # First time seeing this trigger

        state = self.states[trigger]

        # Don't intervene if at independent level
        if state.specificity_level >= 3:
            return False

        # Check minimum interval
        if time.time() - state.last_intervention < self.MIN_INTERVAL:
            return False

        return True

    def get_fading_progress(self, trigger: str) -> Dict:
        """
        Get the fading progress for a trigger.

        Args:
            trigger: The trigger type

        Returns:
            Dictionary with progress information.
        """
        if trigger not in self.states:
            return {
                "trigger": trigger,
                "current_level": 0,
                "target_level": 3,
                "progress": 0.0,
                "interventions": 0,
            }

        state = self.states[trigger]
        progress = state.specificity_level / 3.0

        return {
            "trigger": trigger,
            "current_level": state.specificity_level,
            "target_level": 3,
            "progress": progress,
            "interventions": state.count,
            "success_rate": state.success_count / max(state.count, 1),
        }


# Example usage and testing
if __name__ == "__main__":
    schedule = FadingSchedule()

    # Simulate interventions
    triggers = ["rabbit_hole", "known_bad_approach", "scope_drift"]

    for trigger in triggers:
        print(f"\n=== {trigger} ===")

        # First intervention (most specific)
        directive = schedule.next_intervention(trigger, {
            "current_tool": "nmap",
            "alternative_tool": "masscan",
            "target": "192.168.1.1",
            "scope": "192.168.1.0/24",
        })
        print(f"Level {directive['specificity_level']}: {directive['message']}")

        # Record successes to fade
        for _ in range(3):
            schedule.record_success(trigger)

        # Second intervention (less specific)
        directive = schedule.next_intervention(trigger, {
            "current_tool": "nmap",
            "alternative_tool": "masscan",
        })
        print(f"Level {directive['specificity_level']}: {directive['message']}")

        # Record more successes
        for _ in range(3):
            schedule.record_success(trigger)

        # Third intervention (minimal)
        directive = schedule.next_intervention(trigger, {})
        print(f"Level {directive['specificity_level']}: {directive['message']}")

    # Print summary
    print("\n=== Summary ===")
    summary = schedule.get_summary()
    for trigger, data in summary["triggers"].items():
        print(f"{trigger}: {data['specificity_name']} (level {data['specificity_level']})")
