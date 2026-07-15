import unittest

from scheduling_agent.models import ScheduledStep, ValidationIssue
from scheduling_agent.scorer import score_schedule


class ScorerTests(unittest.TestCase):
    def test_score_breakdown(self):
        schedule = [
            ScheduledStep("A", 0, "MIXER", 4, 0, 4, 5),
            ScheduledStep("A", 1, "READER", 4, 4, 8, 5),
            ScheduledStep("B", 0, "MIXER", 2, 8, 10, 10),
        ]
        issues = [ValidationIssue("resource_conflict", "x")]
        score = score_schedule(schedule, issues)
        self.assertEqual(score.hard_errors, 1)
        self.assertEqual(score.makespan, 10)
        self.assertEqual(score.total_tardiness, 3)
        self.assertEqual(score.score, 1019)


if __name__ == "__main__":
    unittest.main()
