from __future__ import annotations

import argparse
from dataclasses import dataclass

from .candidates import Candidate, candidate_library
from .problem_loader import load_problem
from .protocol import schedule_to_protocol, write_protocol
from .scorer import ScoreBreakdown, score_schedule
from .simulator import simulate_protocol
from .validator import validate_schedule


@dataclass
class CandidateResult:
    candidate: Candidate
    score: ScoreBreakdown
    issue_count: int
    issues: list
    schedule: list
    improved: bool


def run_experiment(problem_path: str, protocol_out: str | None = None) -> list[CandidateResult]:
    problem = load_problem(problem_path)
    best_score: int | None = None
    previous_issues = []
    results: list[CandidateResult] = []

    for candidate in candidate_library():
        schedule = candidate.run(problem, previous_issues)
        issues = validate_schedule(schedule, problem)
        breakdown = score_schedule(schedule, issues)
        improved = best_score is None or breakdown.score < best_score
        if improved:
            best_score = breakdown.score
        results.append(
            CandidateResult(
                candidate=candidate,
                score=breakdown,
                issue_count=len(issues),
                issues=issues,
                schedule=schedule,
                improved=improved,
            )
        )
        previous_issues = issues

    best = min(results, key=lambda item: item.score.score)
    protocol = schedule_to_protocol(best.schedule)
    sim_issues = simulate_protocol(protocol, problem)
    if protocol_out:
        write_protocol(best.schedule, protocol_out)
    _print_report(results, best, sim_issues)
    return results


def _print_report(results: list[CandidateResult], best: CandidateResult, sim_issues: list) -> None:
    print("ERA + PRISM lab scheduling demo")
    print("=" * 38)
    print("Scoring: 1000 * hard_errors + makespan + 3 * total_tardiness")
    print()

    for index, result in enumerate(results, start=1):
        marker = "IMPROVED" if result.improved else "kept previous best"
        print(f"[{index}] Candidate: {result.candidate.name} ({marker})")
        print(f"    ERA note: {result.candidate.era_note}")
        print(
            "    Score: "
            f"{result.score.score} = 1000*{result.score.hard_errors} "
            f"+ makespan {result.score.makespan} "
            f"+ 3*tardiness {result.score.total_tardiness}"
        )
        if result.issues:
            print("    Validator feedback:")
            for issue in result.issues:
                print(f"      - {issue.kind}: {issue.message}")
        else:
            print("    Validator feedback: no hard-constraint errors")
        print()

    print(f"Best candidate: {best.candidate.name}")
    print("Best schedule:")
    for step in sorted(best.schedule, key=lambda item: (item.start, item.resource, item.batch_id)):
        print(
            f"  {step.batch_id}.{step.step_index} "
            f"{step.resource:<9} [{step.start:>2},{step.end:>2}) "
            f"deadline={step.deadline}"
        )
    print()

    print("PRISM-style structured protocol simulation:")
    if sim_issues:
        print(f"  FAILED with {len(sim_issues)} issue(s):")
        for issue in sim_issues:
            print(f"    - {issue.kind}: {issue.message}")
    else:
        print("  PASSED: structured protocol replay has no hard-constraint errors")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ERA + PRISM scheduling demo.")
    parser.add_argument("--problem", default="examples/lab_problem.json")
    parser.add_argument("--protocol-out", default="examples/best_protocol.json")
    args = parser.parse_args()
    run_experiment(args.problem, args.protocol_out)


if __name__ == "__main__":
    main()
