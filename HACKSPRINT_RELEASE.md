# EvidenceGuard HackSprint Release Checkpoint

This branch records the working Daytona HackSprint MVP checkpoint.

## Verified live integrations

- Daytona: isolated sandbox creation, code execution, and cleanup request
- Neo4j: authenticated graph write/query path
- Nosana: authenticated live inference using `qwen/qwen3.8-27b`

## Demo path

Run `CLM-101` in live mode to demonstrate cross-claim relationship discovery and a human-review investigation brief.

## Safety and decisioning

EvidenceGuard surfaces investigation signals and review priority. It does not make autonomous fraud determinations, claim denials, or payment decisions.

## Repository hygiene

Secrets are expected to remain local or in deployment secret storage. The committed `.env.example` is a template only.
