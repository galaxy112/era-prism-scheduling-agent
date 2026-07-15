from __future__ import annotations

from collections import defaultdict

from .models import Schedule, ScoreBreakdown, ValidationIssue


def score_schedule(schedule: Schedule, issues: list[ValidationIssue]) -> ScoreBreakdown:
    makespan = max((step.end for step in schedule), default=0)
    completion_by_batch: dict[str, int] = defaultdict(int)
    deadline_by_batch: dict[str, int] = {}
    for step in schedule:
        completion_by_batch[step.batch_id] = max(completion_by_batch[step.batch_id], step.end)
        deadline_by_batch[step.batch_id] = step.deadline

    total_tardiness = sum(
        max(0, completion - deadline_by_batch[batch_id])
        for batch_id, completion in completion_by_batch.items()
    )
    hard_errors = len(issues)
    score = 1000 * hard_errors + makespan + 3 * total_tardiness
    return ScoreBreakdown(
        hard_errors=hard_errors,
        makespan=makespan,
        total_tardiness=total_tardiness,
        score=score,
    )
