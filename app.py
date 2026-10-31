"""EvidenceGuard hackathon UI: launch with streamlit run app.py."""
import json
import os

import streamlit as st
from dotenv import load_dotenv

from evidence_guard.data import CLAIMS, LABELS
from evidence_guard.workflow import missing_credentials, run_investigation

load_dotenv()
st.set_page_config(page_title="EvidenceGuard | AI Investigation", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
  .block-container { padding-top: 1.25rem; max-width: 1250px; }
  h1, h2, h3 { letter-spacing: -0.025em; }
  .eyebrow {color: #42E7C2; font-size: 0.80rem; font-weight: 700; letter-spacing: .15em; }
  .hero { background: linear-gradient(115deg,#0e2531,#10253c); border: 1px solid #1d4b59;
      padding: 22px 26px; border-radius: 16px; margin-bottom: 14px; }
  .hero h1 {font-size: 2.05rem; margin: 6px 0 4px 0; color: #f4faff;}
  .hero p { color: #b9cad7; margin: 0; }
  .stMetric {background-color: #0c202c; border-radius: 12px; padding: 14px; border: 1px solid #173f4d;}
  [data-testid="stSidebar"] { border-right: 1px solid #244556; }
  .smallnote {color: #a1b3c2; font-size: .86rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero"><div class="eyebrow">EVIDENCEGUARD / HACKSPRINT SINGAPORE</div>
<h1>Untrusted evidence. Trusted investigation.</h1>
<p>Isolated processing · Relationship intelligence · Human-supervised decisions</p></div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Investigation control")
    selected_id = st.selectbox("Synthetic case", [c["id"] for c in CLAIMS], index=0,
                               format_func=lambda x: f"{x} — {next(c['incident_type'] for c in CLAIMS if c['id']==x)}")
    claim = next(c for c in CLAIMS if c["id"] == selected_id)
    execution = st.radio("Execution mode", ["Local demo", "Live sponsors"], index=0,
                         help="Local demo uses no sponsor infrastructure. Live mode calls all three sponsors.")
    live = execution == "Live sponsors"
    missing = missing_credentials()
    if live and missing:
        st.warning("Missing credentials: " + ", ".join(missing))
    elif live:
        st.info("Credentials present; connectivity is verified on execution.")
    else:
        st.caption("Local mode demonstrates behavior without claiming cloud usage.")
    run = st.button("▶ Run investigation", type="primary", use_container_width=True,
                    disabled=bool(live and missing))
    st.divider()
    st.caption("All people, accounts, businesses, and incidents shown here are fictional. Signals require human verification.")

if run:
    with st.spinner("Processing evidence and discovering claim relationships..."):
        try:
            st.session_state["analysis"] = run_investigation(claim, CLAIMS, live=live)
            st.session_state.pop("analysis_error", None)
        except Exception as exc:
            st.session_state.pop("analysis", None)
            st.session_state["analysis_error"] = str(exc)

if "analysis_error" in st.session_state:
    st.error("Investigation failed; no successful sponsor usage is claimed. " + st.session_state["analysis_error"])

case_col, context_col = st.columns([2.0, 1.0], gap="large")
with case_col:
    st.subheader(f"Case {claim['id']}")
    a, b, c = st.columns(3)
    a.metric("Estimated loss", f"S${claim['estimated_loss_sgd']:,}")
    b.metric("Incident", claim["incident_date"])
    c.metric("Case type", claim["incident_type"])
    st.markdown("**Evidence provided (untrusted)**")
    st.code(claim["evidence_text"], language=None, wrap_lines=True)
with context_col:
    st.subheader("Evidence identity")
    st.write("**Claimant:**", claim["claimant"])
    st.write("**Payment reference:**", claim["payment_account"])
    st.write("**Witness reference:**", claim["witness_contact"])
    st.write("**Repair vendor:**", claim["repair_partner"])
    st.caption("Invented demo identifiers. Not connected to actual customers or claims.")

result = st.session_state.get("analysis")
if result and (result["claim"]["id"] != selected_id or (result["execution"] == "LIVE") != live):
    result = None

st.divider()
if not result:
    st.info("Choose a synthetic case and click **Run investigation**. CLM-101 has three cross-claim links; CLM-104 is the low-signal control case.")
else:
    st.subheader("Investigation outcome")
    x, y, z, w = st.columns(4)
    x.metric("Review priority", result["priority"])
    y.metric("Triage score*", str(result["score"]) + "/100")
    z.metric("Shared identifiers", len(result["links"]))
    w.metric("Pipeline latency", f"{result['timings']['total']:.2f}s")
    st.caption("*Illustrative heuristic triage score, **not** probability of fraud or an automated claim decision.")
    left, right = st.columns([1.12, 1.0], gap="large")
    with left:
        st.markdown("#### Cross-claim relationship map")
        edges = result["links"]
        if edges:
            graph_lines = [
                "digraph Investigation {", "rankdir=LR;", "bgcolor=transparent;",
                'node [shape=box style="rounded,filled" fontname="Arial" fontsize=12 color="#2c7482" fontcolor="#eff9ff" fillcolor="#173645"];',
                'edge [color="#4de6bd" fontcolor="#bdeee4" fontsize=10];',
            ]
            graph_lines.append(f"{json.dumps(selected_id)} [fillcolor=\"#11685d\" label={json.dumps(selected_id + ' (selected)')}];")
            for i, edge in enumerate(edges):
                identifier_node = f"identifier_{i}"
                graph_lines.append(f"{json.dumps(identifier_node)} [shape=ellipse label={json.dumps(LABELS[edge['kind']] + ': ' + edge['value'])}];")
                graph_lines.append(f"{json.dumps(edge['other_id'])} [label={json.dumps(edge['other_id'])}];")
                graph_lines.append(f"{json.dumps(selected_id)} -> {json.dumps(identifier_node)};")
                graph_lines.append(f"{json.dumps(identifier_node)} -> {json.dumps(edge['other_id'])};")
            graph_lines.append("}")
            st.graphviz_chart("\n".join(graph_lines), use_container_width=True)
            for edge in edges:
                st.write(f"**{edge['other_id']}** — {LABELS[edge['kind']]}: `{edge['value']}`")
        else:
            st.success("No matching identifiers in the synthetic four-case sample.")
        if result["processed"]["untrusted_instruction_detected"]:
            st.warning("Instruction-like language detected in untrusted evidence. It was not treated as an agent command.")
    with right:
        st.markdown("#### AI investigation briefing")
        st.markdown(result["narrative"])
        st.caption(f"Generator: {result['model']}")
        st.markdown("#### Execution evidence")
        for sponsor in ("Daytona", "Neo4j", "Nosana"):
            st.write("**" + sponsor + ":** " + result["statuses"][sponsor])
        if result["sandbox_id"]:
            st.code("Daytona sandbox ID: " + str(result["sandbox_id"]), language=None)
        st.write("**Evidence SHA-256:**")
        st.code(result["processed"]["evidence_sha256"])
        st.caption("A real sandbox is ephemeral and deletion is requested after processing. Check the Daytona console to confirm deletion.")
    with st.expander("Evidence trace: structured output and timing"):
        st.json({"processed": result["processed"], "graph_links": result["links"],
                 "duration_seconds": result["timings"], "execution": result["execution"]})
    st.divider()
    st.markdown("**Human review action:** Verify the shared identifiers independently. Do not automatically approve, deny, or label any claimant as fraudulent.")
