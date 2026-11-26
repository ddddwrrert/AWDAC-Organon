import unittest
from fixtures.mock_agent import MockAgent
from fixtures.mock_worker import MockWorker
from fixtures.sample_programs import BASELINE
from awdac.schemas import Candidate


class Verification(unittest.TestCase):
    def test_worker_autonomy(self):
        worker = MockWorker()
        advice = MockAgent().propose({})
        proposed = worker.create(Candidate(BASELINE), {}, advice)
        self.assertEqual(worker.advice, [advice])
        self.assertTrue(proposed.intent.rebuttal)
        self.assertEqual(proposed.intent.mode, "radical")
