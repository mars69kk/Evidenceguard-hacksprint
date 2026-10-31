"""Mocked integration contract checks: no sponsor credentials/network used."""
import json
import os
import shlex
import subprocess
import sys
import types
import unittest
from unittest.mock import patch

from evidence_guard.data import CLAIMS
from evidence_guard.daytona_runner import process_with_daytona
from evidence_guard.nosana import summarize_with_nosana


class DaytonaSandboxContract(unittest.TestCase):
    def test_trusted_worker_executes_and_cleanup_runs(self):
        fake_sandbox = types.SimpleNamespace(id="fake-daytona-sandbox", deleted=False)

        def execute(command, timeout):
            self.assertTrue(command.startswith("python3 -c "))
            self.assertEqual(timeout, 35)
            words = shlex.split(command)
            # Contract-only test: locally executes the exact trusted worker
            # source and data that would be supplied to Daytona's exec API.
            run = subprocess.run([sys.executable] + words[1:], capture_output=True, text=True)
            return types.SimpleNamespace(exit_code=run.returncode, result=run.stdout if run.returncode == 0 else run.stderr)

        fake_sandbox.process = types.SimpleNamespace(exec=execute)
        fake_sandbox.delete = lambda: setattr(fake_sandbox, "deleted", True)
        fake_client = types.SimpleNamespace(create=lambda: fake_sandbox, close=lambda: None)
        fake_sdk = types.SimpleNamespace(Daytona=lambda: fake_client)
        with patch.dict(sys.modules, {"daytona": fake_sdk}):
            output, sandbox_id = process_with_daytona(CLAIMS[1])
        self.assertEqual(sandbox_id, fake_sandbox.id)
        self.assertTrue(fake_sandbox.deleted)
        self.assertTrue(output["untrusted_instruction_detected"])


class NosanaInferenceContract(unittest.TestCase):
    def test_discovers_available_model_and_uses_grounded_prompt(self):
        seen = {}
        model = types.SimpleNamespace(id="fictional-test-model", available=True)
        fake_client = types.SimpleNamespace(
            models=types.SimpleNamespace(list=lambda: types.SimpleNamespace(data=[model])),
            chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda **kw: seen.update(kw) or types.SimpleNamespace(
                choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="Human review required."))]))),
        )
        fake_sdk = types.SimpleNamespace(OpenAI=lambda **kwargs: fake_client)
        with patch.dict(sys.modules, {"openai": fake_sdk}), patch.dict(os.environ, {"NOSANA_API_KEY": "test-key", "NOSANA_MODEL": ""}):
            answer, model_id = summarize_with_nosana({"id": "CLM-101"}, [], False)
        self.assertEqual(model_id, "fictional-test-model")
        self.assertEqual(seen["model"], model_id)
        self.assertEqual(answer, "Human review required.")
        self.assertIn("untrusted", seen["messages"][0]["content"])


if __name__ == "__main__":
    unittest.main()
