"""Quick local and live verification. Run from repository root."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
from evidence_guard.data import CLAIMS
from evidence_guard.workflow import run_investigation

load_dotenv()
parser = argparse.ArgumentParser()
parser.add_argument("--live", action="store_true", help="Make real Daytona/Neo4j/Nosana calls")
parser.add_argument("--claim", choices=[c["id"] for c in CLAIMS], default="CLM-101")
args = parser.parse_args()
claim = next(c for c in CLAIMS if c["id"] == args.claim)
r = run_investigation(claim, CLAIMS, live=args.live)
print(json.dumps({
    "claim": r["claim"]["id"], "execution": r["execution"],
    "score": r["score"], "priority": r["priority"],
    "links": r["links"], "statuses": r["statuses"],
    "sandbox_id": r["sandbox_id"], "timings": r["timings"],
    "narrative": r["narrative"],
}, indent=2))
