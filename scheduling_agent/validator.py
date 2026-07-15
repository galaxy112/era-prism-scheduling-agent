from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .models import DowntimeWindow, Problem, Schedule, ScheduledStep, ValidationIssue


def overlaps(left_start: int, left_end: int, right_start: int, right_end: int) -> bool:
    return left_start < right_end and left_end > right_start


def validate_schedule(schedule: Schedule, problem: Problem) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues.extend(_validate_resource_conflicts(schedule))
    issues.extend(_validate_step_order(schedule))
    issues.extend(_validate_downtime(schedule, problem.downtimes))
    return issues


def _validate_resource_conflicts(schedule: Schedule) -> Iterable[ValidationIssue]:
    by_resource: dict[str, list[ScheduledStep]] = defaultdict(list)
    for step in schedule:
        by_resource[step.resource].append(step)

    for resource, steps in by_resource.items():
        ordered = sorted(steps, key=lambda item: (item.start, item.end, item.batch_id))
        for previous, current in zip(ordered, ordered[1:]):
            if overlaps(previous.start, previous.end, current.start, current.end):
                yield ValidationIssue(
                    kind="resource_conflict",
                    message=f"{resource} is double-booked by {previous.label()} and {current.label()}",
                    steps=[previous.label(), current.label()],
                )


def _validate_step_order(schedule: Schedule) -> Iterable[ValidationIssue]:
    by_batch: dict[str, list[ScheduledStep]] = defaultdict(list)
    for step in schedule:
        by_batch[step.batch_id].append(step)

    for batch_id, steps in by_batch.items():
        ordered = sorted(steps, key=lambda item: item.step_index)
        for previous, current in zip(ordered, ordered[1:]):
            if current.start < previous.end:
                yield ValidationIssue(
                    kind="step_order",
                    message=(
                        f"Batch {batch_id} step {current.step_index} starts before "
                        f"step {previous.step_index} finishes"
                    ),
                    steps=[previous.label(), current.label()],
                )


def _validate_downtime(
    schedule: Schedule, downtimes: Iterable[DowntimeWindow]
) -> Iterable[ValidationIssue]:
    for step in schedule:
        for window in downtimes:
            if step.resource == window.resource and overlaps(step.start, step.end, window.start, window.end):
                yield ValidationIssue(
                    kind="downtime_conflict",
                    message=(
                        f"{step.label()} overlaps {window.resource} downtime "
                        f"[{window.start},{window.end})"
                    ),
                    steps=[step.label()],
                )
