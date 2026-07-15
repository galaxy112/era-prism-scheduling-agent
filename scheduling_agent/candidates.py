from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .baseline import schedule_batches_downtime_aware, schedule_batches_earliest, shift_past_downtime
from .models import Problem, Schedule, ScheduledStep, ValidationIssue


@dataclass(frozen=True)
class Candidate:
    name: str
    era_note: str
    run: Callable[[Problem, list[ValidationIssue] | None], Schedule]


def naive_batch_order(problem: Problem, previous_issues: list[ValidationIssue] | None = None) -> Schedule:
    return schedule_batches_earliest(problem, problem.batches)


def downtime_aware_earliest(problem: Problem, previous_issues: list[ValidationIssue] | None = None) -> Schedule:
    return schedule_batches_downtime_aware(problem, problem.batches)


def deadline_priority(problem: Problem, previous_issues: list[ValidationIssue] | None = None) -> Schedule:
    batches = sorted(problem.batches, key=lambda batch: (batch.deadline, batch.batch_id))
    return schedule_batches_downtime_aware(problem, batches)


def repair_conflicts(problem: Problem, previous_issues: list[ValidationIssue] | None = None) -> Schedule:
    """Feedback-driven candidate: start from baseline, then rebuild with known hard constraints."""
    schedule = schedule_batches_earliest(problem, problem.batches)
    if not previous_issues:
        return schedule

    if any(issue.kind == "downtime_conflict" for issue in previous_issues):
        schedule = _repair_downtime(schedule, problem)

    # Rebuilding after downtime repair is simpler and safer than trying to
    # preserve every local offset in this tiny demo.
    if previous_issues:
        schedule = schedule_batches_downtime_aware(problem, problem.batches)
    return schedule


def _repair_downtime(schedule: Schedule, problem: Problem) -> Schedule:
    repaired: Schedule = []
    for step in schedule:
        start = shift_past_downtime(problem, step.resource, step.start, step.duration)
        repaired.append(
            ScheduledStep(
                batch_id=step.batch_id,
                step_index=step.step_index,
                resource=step.resource,
                duration=step.duration,
                start=start,
                end=start + step.duration,
                deadline=step.deadline,
            )
        )
    return repaired


def candidate_library() -> list[Candidate]:
    return [
        Candidate(
            name="naive_batch_order",
            era_note="Initial generated candidate: greedy by input order, no downtime handling.",
            run=naive_batch_order,
        ),
        Candidate(
            name="repair_conflicts",
            era_note="Feedback rewrite: use validator feedback to add downtime-aware repair.",
            run=repair_conflicts,
        ),
        Candidate(
            name="downtime_aware_earliest",
            era_note="Candidate rewrite: keep input order but right-shift operations past downtime.",
            run=downtime_aware_earliest,
        ),
        Candidate(
            name="deadline_priority",
            era_note="Search variation: prioritize batches with earlier deadlines.",
            run=deadline_priority,
        ),
    ]
