import base64
import json
import subprocess
import sys
import unittest

from evidence_guard.data import CLAIMS
from evidence_guard.graph import links_for_claim_local, review_priority
from evidence_guard.worker import normalize_claim
from evidence_guard.workflow import run_investigation


class EvidenceGuardTests(unittest.TestCase):
    def test_hidden_account_link(self):
        links = links_for_claim_local("CLM-101", CLAIMS)
        self.assertIn({"other_id": "CLM-102", "kind": "payment_account", "value": "DEMO-ACC-431"}, links)
        self.assertEqual(len(links), 3)

    def test_no_link_control(self):
        self.assertEqual(links_for_claim_local("CLM-104", CLAIMS), [])
        self.assertEqual(review_priority([]), (0, "Low"))

    def test_untrusted_text_detected_without_execution(self):
        parsed = normalize_claim(CLAIMS[1])
        self.assertTrue(parsed["untrusted_instruction_detected"])
        self.assertIn("approve claim immediately", parsed["evidence_preview"])

    def test_worker_cli_same_as_local(self):
        payload = base64.b64encode(json.dumps(CLAIMS[0]).encode()).decode()
        completed = subprocess.run([sys.executable, "-m", "evidence_guard.worker", payload],
                                   capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(completed.stdout), normalize_claim(CLAIMS[0]))

    def test_local_end_to_end_and_explicit_status(self):
        outcome = run_investigation(CLAIMS[0], CLAIMS, live=False)
        self.assertEqual(outcome["execution"], "DEMO")
        self.assertEqual(outcome["score"], 100)
        self.assertEqual(outcome["priority"], "High")
        for name in ("Daytona", "Neo4j", "Nosana"):
            self.assertIn("DEMO", outcome["statuses"][name])

    def test_live_requires_all_credentials(self):
        from unittest.mock import patch
        with patch("evidence_guard.workflow.missing_credentials", return_value=["NOSANA_API_KEY"]):
            with self.assertRaisesRegex(ValueError, "NOSANA_API_KEY"):
                run_investigation(CLAIMS[0], CLAIMS, live=True)


if __name__ == "__main__":
    unittest.main()
