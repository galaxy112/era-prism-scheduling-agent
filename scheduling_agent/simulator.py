from __future__ import annotations

from .models import Problem, ScheduledStep, ValidationIssue
from .validator import validate_schedule


def simulate_protocol(protocol_steps: list[dict], problem: Problem) -> list[ValidationIssue]:
    """Rehydrate structured protocol steps and run the same hard-constraint checks."""
    schedule = [
        ScheduledStep(
            batch_id=str(item["batch_id"]),
            step_index=int(item["step_index"]),
            resource=str(item["resource"]),
            duration=int(item["duration"]),
            start=int(item["start"]),
            end=int(item["end"]),
            deadline=int(item["deadline"]),
        )
        for item in protocol_steps
    ]
    return validate_schedule(schedule, problem)
