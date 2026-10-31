"""Execute trusted evidence preprocessing in a fresh Daytona sandbox."""
import base64
import json
import shlex
from pathlib import Path


def process_with_daytona(claim):
    # Import only on live path; local mode has zero cloud dependencies.
    from daytona import Daytona

    encoded = base64.b64encode(json.dumps(claim).encode("utf-8")).decode("ascii")
    if len(encoded) > 25000:
        raise ValueError("Claim too large for sandbox command")
    worker_source = Path(__file__).with_name("worker.py").read_text(encoding="utf-8")
    command = "python3 -c " + shlex.quote(worker_source) + " " + shlex.quote(encoded)
    client = Daytona()  # DAYTONA_API_KEY from environment
    sandbox = None
    try:
        sandbox = client.create()
        sandbox_id = sandbox.id
        response = sandbox.process.exec(command, timeout=35)
        if response.exit_code != 0:
            raise RuntimeError(f"Sandbox worker failed (exit {response.exit_code}): {response.result[:300]}")
        result = json.loads(response.result.strip())
        if result.get("claim_id") != claim["id"]:
            raise RuntimeError("Sandbox result claim mismatch")
        return result, sandbox_id
    finally:
        if sandbox is not None:
            # Delete ephemeral evidence-processing environments (permissions required).
            try:
                sandbox.delete()
            except Exception as exc:
                raise RuntimeError(f"IMPORTANT: Failed to delete Daytona sandbox {sandbox.id}: {exc}") from exc
        close = getattr(client, "close", None)
        if callable(close):
            close()
