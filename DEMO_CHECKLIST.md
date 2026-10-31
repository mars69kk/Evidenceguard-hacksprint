# EvidenceGuard — Prize-oriented final checklist

## P0 (must pass before the judging demo)

- [ ] Venue entrance QR code / correct location confirmed.
- [ ] `.env` filled in locally (never committed or displayed).
- [ ] `python -m unittest discover -s tests -v` all green.
- [ ] `python scripts/doctor.py --verify` shows PASS for Daytona, Neo4j, and Nosana.
- [ ] `python scripts/smoke.py --live` returns `execution: LIVE`, three LIVE statuses and an actual Daytona sandbox ID.
- [ ] Daytona sandbox deletion checked in dashboard; cloud spend controlled.
- [ ] App launched via `streamlit run app.py`; sidebar set to **Live sponsors**.
- [ ] CLM-101 demo: 3 graph connections, shared payment with CLM-102.
- [ ] CLM-102 demo: instruction-like text is flagged and not obeyed.
- [ ] Nosana result shown alongside the actual model ID and audit trace.
- [ ] Demo rehearsed to 3 minutes. Screenshots and terminal backup available.

## P1 (if sufficient time remains)

- [ ] Add a single clean screenshot or short recording of LIVE statuses for backup.
- [ ] Capture a Daytona dashboard image proving sandbox execution and lifecycle.
- [ ] Capture Neo4j Browser view of `EGClaim` → `EGIdentifier` graph.
- [ ] Confirm whether organizer expects GitHub submission / public repo; provide sanitized repository only.
- [ ] Confirm if all three sponsors are strictly mandatory and whether prebuilt starter code is permitted.

## Prizes rubric mapping

**Completeness:** CLM-101 must execute end-to-end in LIVE mode, show graph and AI output.

**Innovation:** Safe, disposable computers for untrusted attachments + cross-case graph intelligence + LLM summaries that remain traceable to graph evidence.

**Real-world problem:** Claim handlers need to see relationships across cases without automatically penalizing individuals.

**Sponsor usage:** Real Daytona sandbox and cleanup; actual Neo4j insert/query; real Nosana `chat.completions` response. No mock passing as live.

## Planned scope exclusions

No real insurance customer information, no OCR/video processing, no production IAM, no calibrated fraud probability, no automatic payment or denial, and no claims of complete prompt-injection defense.
