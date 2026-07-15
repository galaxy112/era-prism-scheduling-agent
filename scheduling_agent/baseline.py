from __future__ import annotations

from typing import Iterable

from .models import BatchSpec, Problem, Schedule, ScheduledStep


def schedule_batches_earliest(problem: Problem, batches: Iterable[BatchSpec]) -> Schedule:
    """Greedy resource scheduler that ignores downtime windows."""
    resource_available = {resource: 0 for resource in problem.resources}
    schedule: Schedule = []

    for batch in batches:
        batch_available = 0
        for index, step in enumerate(batch.steps):
            start = max(batch_available, resource_available[step.resource])
            end = start + step.duration
            scheduled = ScheduledStep(
                batch_id=batch.batch_id,
                step_index=index,
                resource=step.resource,
                duration=step.duration,
                start=start,
                end=end,
                deadline=batch.deadline,
            )
            schedule.append(scheduled)
            batch_available = end
            resource_available[step.resource] = end

    return schedule


def shift_past_downtime(problem: Problem, resource: str, start: int, duration: int) -> int:
    candidate = start
    changed = True
    while changed:
        changed = False
        for window in problem.downtimes:
            if window.resource != resource:
                continue
            end = candidate + duration
            if candidate < window.end and end > window.start:
                candidate = window.end
                changed = True
    return candidate


def schedule_batches_downtime_aware(problem: Problem, batches: Iterable[BatchSpec]) -> Schedule:
    """Greedy resource scheduler that right-shifts operations out of downtime."""
    resource_available = {resource: 0 for resource in problem.resources}
    schedule: Schedule = []

    for batch in batches:
        batch_available = 0
        for index, step in enumerate(batch.steps):
            start = max(batch_available, resource_available[step.resource])
            start = shift_past_downtime(problem, step.resource, start, step.duration)
            end = start + step.duration
            scheduled = ScheduledStep(
                batch_id=batch.batch_id,
                step_index=index,
                resource=step.resource,
                duration=step.duration,
                start=start,
                end=end,
                deadline=batch.deadline,
            )
            schedule.append(scheduled)
            batch_available = end
            resource_available[step.resource] = end

    return schedule
