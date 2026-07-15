import unittest
from contextlib import redirect_stdout
from io import StringIO

from scheduling_agent.experiment import run_experiment


class ClosedLoopTests(unittest.TestCase):
    def test_closed_loop_improves_after_failed_candidate(self):
        with redirect_stdout(StringIO()):
            results = run_experiment("examples/lab_problem.json")
        self.assertGreater(results[0].score.hard_errors, 0)
        self.assertLess(min(item.score.score for item in results[1:]), results[0].score.score)
        self.assertEqual(min(item.score.hard_errors for item in results), 0)


if __name__ == "__main__":
    unittest.main()
