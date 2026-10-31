"""Runs unchanged locally or as trusted program INSIDE a Daytona sandbox.

Only synthetic JSON data arrives as a base64 CLI argument. Data is never executed.
No network access, secrets, or installed packages are needed inside the sandbox.
"""
import base64
import hashlib
import json
import re
import sys

ALLOWED = ("id", "incident_date", "incident_type", "estimated_loss_sgd",
           "payment_account", "witness_contact", "repair_partner")
# Lightweight warning heuristic, not a guarantee of injection detection.
UNTRUSTED_INSTRUCTIONS = re.compile(
    r"ignore (?:all |any |the )?(?:previous |prior |system )?instructions|"
    r"approve (?:this |the )?claim immediately|"
    r"bypass (?:policy|rules|checks)", re.I
)


def normalize_claim(claim):
    if not isinstance(claim, dict):
        raise ValueError("Claim must be an object")
    raw_evidence = claim.get("evidence_text", "")
    if not isinstance(raw_evidence, str) or len(raw_evidence) > 12000:
        raise ValueError("Evidence must be text of at most 12,000 characters")
    if not isinstance(claim.get("id"), str) or len(claim["id"]) > 50:
        raise ValueError("Invalid claim ID")
    facts = {key: claim.get(key) for key in ALLOWED}
    return {
        "claim_id": claim["id"],
        "facts": facts,
        "evidence_sha256": hashlib.sha256(raw_evidence.encode("utf-8")).hexdigest(),
        "evidence_preview": raw_evidence[:240],
        "untrusted_instruction_detected": bool(UNTRUSTED_INSTRUCTIONS.search(raw_evidence)),
        "source": "synthetic_evidence_text",
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Expected base64-encoded JSON payload")
    encoded = sys.argv[1]
    if len(encoded) > 25000:
        raise SystemExit("Input too large")
    claim = json.loads(base64.b64decode(encoded, validate=True).decode("utf-8"))
    print(json.dumps(normalize_claim(claim), ensure_ascii=True))


if __name__ == "__main__":
    main()
