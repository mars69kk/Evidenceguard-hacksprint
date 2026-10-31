"""Sponsor connectivity diagnostic. Never prints API keys or passwords."""
import argparse
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--verify", action="store_true", help="Make real network calls (Daytona creates/deletes an ephemeral sandbox)")
args = parser.parse_args()

requirements = {
    "Daytona": ["DAYTONA_API_KEY"],
    "Neo4j": ["NEO4J_URI", "NEO4J_PASSWORD"],
    "Nosana": ["NOSANA_API_KEY"],
}
failures = []
for sponsor, keys in requirements.items():
    missing = [key for key in keys if not os.environ.get(key)]
    if missing:
        print(f"[MISSING] {sponsor}: " + ", ".join(missing))
        failures.append(sponsor)
    else:
        print(f"[CONFIGURED] {sponsor}: credential variables present (not yet authenticated)")

if args.verify:
    if "Daytona" not in failures:
        sandbox = None
        daytona = None
        try:
            from daytona import Daytona
            daytona = Daytona()
            sandbox = daytona.create()
            r = sandbox.process.exec("python3 -c 'print(2026)'", timeout=20)
            if r.exit_code != 0 or "2026" not in r.result:
                raise RuntimeError("Sandbox failed code execution")
            print("[PASS] Daytona: real sandbox successfully executed code")
        except Exception as e:
            print(f"[FAIL] Daytona: {type(e).__name__}: {e}")
            failures.append("Daytona")
        finally:
            if sandbox is not None:
                try:
                    sandbox.delete()
                    print("[CLEANUP] Daytona: sandbox deletion requested; confirm in console")
                except Exception as e:
                    print(f"[CLEANUP ERROR] Daytona: sandbox {sandbox.id}: {e}")
                    failures.append("Daytona cleanup")
            if daytona is not None:
                close = getattr(daytona, "close", None)
                if callable(close):
                    close()
    if "Neo4j" not in failures:
        try:
            from neo4j import GraphDatabase
            with GraphDatabase.driver(os.environ["NEO4J_URI"],
                                      auth=(os.getenv("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"])) as driver:
                driver.verify_connectivity()
                records, _, _ = driver.execute_query("RETURN 1 AS ok", database_=os.getenv("NEO4J_DATABASE", "neo4j"))
                assert records[0]["ok"] == 1
            print("[PASS] Neo4j: authenticated and queried database")
        except Exception as e:
            print(f"[FAIL] Neo4j: {type(e).__name__}: {e}")
            failures.append("Neo4j")
    if "Nosana" not in failures:
        try:
            from openai import OpenAI
            client = OpenAI(base_url="https://inference.nosana.com/v1",
                            api_key=os.environ["NOSANA_API_KEY"], timeout=25.0, max_retries=0)
            ids = [m.id for m in client.models.list().data if getattr(m, "available", True)]
            if not ids:
                raise RuntimeError("No currently served models")
            print(f"[PASS] Nosana: API authenticated, {len(ids)} available models; first: {ids[0]}")
        except Exception as e:
            print(f"[FAIL] Nosana: {type(e).__name__}: {e}")
            failures.append("Nosana")
else:
    print("Run `python scripts/doctor.py --verify` to authenticate and verify real calls.")
if failures:
    print("Action required:", ", ".join(failures))
    sys.exit(1)
print("Diagnostic complete: configured sponsors " + ("verified." if args.verify else "found."))
