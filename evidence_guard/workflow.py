"""Strict demo vs live execution. Errors are never disguised as success."""
import os
import time
from .worker import normalize_claim
from .daytona_runner import process_with_daytona
from .graph import links_for_claim_local, links_for_claim_neo4j, review_priority
from .nosana import deterministic_summary, summarize_with_nosana


def missing_credentials():
    required = ("DAYTONA_API_KEY", "NEO4J_URI", "NEO4J_PASSWORD", "NOSANA_API_KEY")
    return [name for name in required if not os.getenv(name)]


def run_investigation(claim, all_claims, live=False):
    if live and missing_credentials():
        raise ValueError("Missing credentials: " + ", ".join(missing_credentials()))
    timings = {}
    statuses = {}
    started = time.perf_counter()
    if live:
        processed, sandbox_id = process_with_daytona(claim)
        statuses["Daytona"] = "LIVE: isolated sandbox executed and deletion requested"
    else:
        processed = normalize_claim(claim)
        sandbox_id = None
        statuses["Daytona"] = "DEMO: local Python worker, not a Daytona sandbox"
    timings["evidence"] = round(time.perf_counter() - started, 3)

    tick = time.perf_counter()
    if live:
        links = links_for_claim_neo4j(claim["id"], all_claims)
        statuses["Neo4j"] = "LIVE: graph write and relationship query succeeded"
    else:
        links = links_for_claim_local(claim["id"], all_claims)
        statuses["Neo4j"] = "DEMO: in-memory graph matching, not Neo4j"
    timings["graph"] = round(time.perf_counter() - tick, 3)

    score, priority = review_priority(links, processed["untrusted_instruction_detected"])
    tick = time.perf_counter()
    if live:
        # Live mode never silently substitutes an offline answer.
        narrative, model = summarize_with_nosana(
            processed["facts"], links, processed["untrusted_instruction_detected"]
        )
        statuses["Nosana"] = f"LIVE: inference completed with {model}"
    else:
        narrative = deterministic_summary(
            processed["facts"], links, processed["untrusted_instruction_detected"]
        )
        model = "local rule-based narrative"
        statuses["Nosana"] = "DEMO: deterministic narrative, not GPU inference"
    timings["narrative"] = round(time.perf_counter() - tick, 3)
    timings["total"] = round(time.perf_counter() - started, 3)
    return {
        "claim": claim, "processed": processed, "links": links, "score": score,
        "priority": priority, "narrative": narrative, "model": model,
        "sandbox_id": sandbox_id, "timings": timings, "statuses": statuses,
        "execution": "LIVE" if live else "DEMO",
    }
