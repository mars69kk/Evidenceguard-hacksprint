# EvidenceGuard — Daytona HackSprint Singapore / SWITCH Edition (31 Oct 2026)

**Three-minute pitch:** An insurance investigator receives untrusted evidence. A Daytona sandbox parses the evidence without executing embedded instructions. Neo4j identifies shared accounts, witnesses and vendors across fictional claims. A Nosana GPU-backed LLM generates an explainable *review briefing* for a human supervisor. The app never labels people guilty of fraud or auto-denies claims.

## Fast start (Windows 11 PowerShell)

Requirement: Python 3.11+ and an internet connection for package installation. All demo content is synthetic.

```powershell
cd C:\Projects\evidenceguard-hacksprint
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python -m unittest discover -s tests -v
python scripts/smoke.py
streamlit run app.py
```

If you installed a different supported Python version, replace `py -3.11` with `py -3.12` or `python` as appropriate. If PowerShell blocks activation, use `\.venv\Scripts\python.exe -m pip install -r requirements.txt` and `\.venv\Scripts\python.exe -m streamlit run app.py` without activating.

Open http://localhost:8501. In **Local demo** mode, the app requires no API keys and does *not* claim real sponsor calls.

## Enable actual sponsor integrations

1. **Daytona** — create an API key in https://app.daytona.io/dashboard/keys; put it in `DAYTONA_API_KEY`.
2. **Neo4j** — create a free AuraDB database at https://console.neo4j.io; save the connection URI, username, password and database name in `.env`. Our app creates *namespaced* `EGClaim` and `EGIdentifier` nodes without clearing the database.
3. **Nosana** — obtain an API key via https://learn.nosana.com/llm/ and set `NOSANA_API_KEY`. Available model IDs are queried at runtime; you may override with `NOSANA_MODEL`.
4. Run `python scripts/doctor.py --verify` and `python scripts/smoke.py --live` first. Confirm all three statuses say LIVE. Then choose **Live sponsors** inside the Streamlit sidebar and run an investigation.

**Do not paste credentials into public hackathon demo chats or commit `.env`.** For live mode, all three credentials are required; failures surface as errors rather than being replaced silently by simulated output. Sandbox deletion is requested in a `finally` block; verify its eventual state in the Daytona console. Leaving running sandboxes may incur costs.

For quick event-day checks, see [DEMO_CHECKLIST.md](DEMO_CHECKLIST.md).

## The judge-friendly scenario

1. Open **CLM-101**. An apparently ordinary fictional collision claim is presented.
2. Click **Run investigation**. In live mode, demonstrate the Daytona sandbox ID and hash of synthetic evidence.
3. Display the graph: **CLM-102** shares a payment destination; **CLM-103** shares a witness reference and repair vendor.
4. Show the Nosana-generated human review summary: the links justify review, not an automatic fraud verdict.
5. Switch to **CLM-102** and run again. Its evidence contains malicious-looking instructions; the trusted sandbox worker flags them without obeying them.
6. Switch to **CLM-104** as a control case: no cross-claim links. Emphasize interpretability and explicit execution trace.

### Three-minute speaking script

| Time | Script / on-screen action |
|---|---|
| 0:00–0:25 | **Problem:** Insurance evidence is messy and untrusted. Traditional reviews miss relationships across multiple claims and risk exposing agents to unsafe instructions. |
| 0:25–0:45 | **Product:** EvidenceGuard combines isolated evidence-processing, graph intelligence and explainable AI to surface *human-review candidates*. |
| 0:45–1:15 | **Daytona:** Click Run. Show that a fresh sandbox processed synthetic evidence, returned a SHA-256, and was scheduled for deletion. |
| 1:15–1:50 | **Neo4j:** Show a shared payment destination linking CLM-101 and CLM-102, plus the witness/vendor link to CLM-103. These cross-claim paths are query results, not an LLM guess. |
| 1:50–2:20 | **Nosana:** Read a concise AI briefing, which points the human reviewer to evidence but does not accuse or deny. |
| 2:20–2:45 | **Safety surprise:** Open CLM-102's injection-like text. Show that it is treated as untrusted evidence. |
| 2:45–3:00 | **Close:** Real sponsor calls, working workflow, clear audit output, and an immediate use case in insurance operations. |

## Architecture

```text
Synthetic claim & untrusted notes
                |
        Streamlit UI (app.py)
                |
    Daytona sandbox (Python trusted worker)
    -> normalized facts + evidence SHA256 + injection-like text flag
                |
    Neo4j AuraDB (parameterized Cypher)
    -> shared-payment/witness/vendor relationships
                |
    Nosana /v1/chat/completions (currently available model)
    -> grounded human-review briefing
                |
       Evidence trace + relationship graph + supervisor decision guidance
```

Local mode runs the same worker logic within Python, computes in-memory relationships, and outputs a deterministic narrative. It is **not** proof of Daytona/Neo4j/Nosana integration. Live mode calls the services in order and marks successes; it does not silently fall back.

## Engineering constraints / truthfulness

- The MVP uses **text evidence**, not OCR, PDF ingestion, an external claims API, real data scraping, or production financial adjudication.
- Notes are inert data, not executed. The pattern-based injection flag is illustrative and not a comprehensive detector; the isolation boundary protects code execution, not all prompt-injection vectors.
- The scorer is a transparent, **illustrative triage heuristic** with no statistical calibration; it is not a probability of fraud.
- The deterministic briefings in demo mode are local. The Nosana briefings in live mode are generative and can be wrong; validate output.
- Synthetic cases and names are fictional. Do not send real policyholder or personal data to services without authorization, appropriate privacy safeguards, and data retention review.
- The code has automated local unit tests but has **not** been exercised against your own live sponsor credentials.

## Reference links

- Daytona SDK: https://www.daytona.io/docs/en/python-sdk/
- Daytona sandbox lifecycle: https://www.daytona.com/docs/sandboxes
- Neo4j driver: https://neo4j.com/docs/python-manual/current/
- Nosana inference: https://learn.nosana.com/llm/
- Event: https://luma.com/daytonasg1031

## If anything fails on demo day

| Failure | Recovery |
|---|---|
| Missing / invalid Daytona API key | Check `.env`, account credits, and key permission; use `python scripts/smoke.py --live` for the full error. |
| Daytona sandbox permission denied on delete | Inspect Daytona console and manually delete it; do **not** claim it was destroyed. |
| Neo4j URI or AuraDB paused | Wake instance in Aura console, verify URI/password and `NEO4J_DATABASE`; rerun smoke test. |
| Nosana model unavailable | Leave `NOSANA_MODEL=` blank to list currently served models dynamically. |
| Network outage | Switch explicitly to **Local demo** mode, say sponsor integrations could not be verified live, and demonstrate end-to-end workflow honestly. |
