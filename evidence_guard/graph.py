"""Neo4j or local in-memory claim relationship analysis."""
from .data import WEIGHTS

IDENTIFIERS = ("payment_account", "witness_contact", "repair_partner")


def links_for_claim_local(claim_id, claims):
    target = next((c for c in claims if c["id"] == claim_id), None)
    if target is None:
        raise KeyError(claim_id)
    links = []
    for other in claims:
        if other["id"] == claim_id:
            continue
        for kind in IDENTIFIERS:
            if target.get(kind) and target[kind] == other.get(kind):
                links.append({"other_id": other["id"], "kind": kind, "value": target[kind]})
    return sorted(links, key=lambda x: (-WEIGHTS[x["kind"]], x["other_id"]))


def _graph_data(claims):
    return [
        {
            "id": c["id"],
            "claimant": c["claimant"],
            "identifiers": [{"kind": kind, "value": c[kind]} for kind in IDENTIFIERS if c.get(kind)],
        }
        for c in claims
    ]


def links_for_claim_neo4j(claim_id, claims):
    import os
    from neo4j import GraphDatabase

    uri = os.environ["NEO4J_URI"]
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.environ["NEO4J_PASSWORD"]
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        driver.verify_connectivity()
        # Namespace-specific constraints. No dropping or clearing existing data.
        driver.execute_query(
            "CREATE CONSTRAINT evidenceguard_claim IF NOT EXISTS FOR (c:EGClaim) REQUIRE c.id IS UNIQUE",
            database_=database,
        )
        driver.execute_query(
            "CREATE CONSTRAINT evidenceguard_identifier IF NOT EXISTS "
            "FOR (i:EGIdentifier) REQUIRE (i.kind, i.value) IS UNIQUE",
            database_=database,
        )
        driver.execute_query(
            """
            UNWIND $claims AS c
            MERGE (cl:EGClaim {id: c.id})
            SET cl.claimant = c.claimant
            WITH cl, c
            UNWIND c.identifiers AS ident
            MERGE (i:EGIdentifier {kind: ident.kind, value: ident.value})
            MERGE (cl)-[:USES_IDENTIFIER]->(i)
            """,
            claims=_graph_data(claims), database_=database,
        )
        records, _, _ = driver.execute_query(
            """
            MATCH (c:EGClaim {id: $claim_id})-[:USES_IDENTIFIER]->(i:EGIdentifier)
                  <-[:USES_IDENTIFIER]-(other:EGClaim)
            WHERE other.id <> c.id
            RETURN DISTINCT other.id AS other_id, i.kind AS kind, i.value AS value
            """,
            claim_id=claim_id, database_=database,
        )
        result = [{"other_id": r["other_id"], "kind": r["kind"], "value": r["value"]}
                  for r in records if r["kind"] in IDENTIFIERS]
    return sorted(result, key=lambda x: (-WEIGHTS[x["kind"]], x["other_id"]))


def review_priority(links, has_untrusted_instruction=False):
    # Heuristic triage priority, NOT fraud probability or an adjudication.
    score = min(100, sum(WEIGHTS.get(row["kind"], 0) for row in links)
                + (15 if has_untrusted_instruction else 0))
    label = "High" if score >= 60 else "Medium" if score >= 25 else "Low"
    return score, label
