"""
Step 7 — Streamlit UI for Support Ticket Triage Desk.

The page lets you paste a NEW ticket, then runs the same RAG loop:
retrieve similar chunks -> ask Qwen -> show structured triage.
"""

from pathlib import Path

import streamlit as st

from step4_embed import CHROMA_DIR
from step6_generate import triage_ticket


# Demo tickets for LinkedIn / portfolio testing (all fake NovaDesk cases).
DEMO_TICKETS = {
    "1) Late cash refund (policy conflict)": """
Customer bought NovaDesk annual plan 30 days ago.
They want a full cash refund to their credit card now.
Please triage this ticket.
""".strip(),
    "2) Password reset email missing": """
I am a paid workspace admin. I clicked Forgot password six times.
No reset email in inbox or spam for alex@oakline.co.
I cannot log in to help my team.
""".strip(),
    "3) Charged twice this month": """
My card shows two identical $49 NovaDesk charges on the same day
for one Team seat. Please reverse the duplicate charge.
""".strip(),
    "4) Need CSV export for audit": """
I am the workspace owner. Our compliance team needs a CSV export
of all tickets and comments within 24 hours for an internal audit.
""".strip(),
    "5) Whole product seems down": """
Since 09:15 nobody on our company can open NovaDesk login or tickets.
It looks like a full outage for us. Please treat as urgent.
""".strip(),
    "6) Dark mode feature request": """
Night-shift agents want a dark mode theme in the inbox.
Is this on the roadmap? Not a bug — just a request.
""".strip(),
    "7) Delete workspace after leaving": """
I am the owner. We are leaving NovaDesk. Please delete our workspace
and all ticket history. Also tell me if billing stops automatically.
""".strip(),
}


st.set_page_config(
    page_title="Support Ticket Triage Desk",
    page_icon="🎫",
    layout="centered",
)

st.title("Support Ticket Triage Desk")
st.caption(
    "Paste a new support ticket. The app retrieves similar old tickets and "
    "policy chunks, then Qwen drafts a grounded triage."
)

# Quick check so the UI fails clearly if Step 4 was never run.
if not CHROMA_DIR.exists():
    st.error(
        "No vector store found. In PowerShell run: "
        "`.\\.venv\\Scripts\\python.exe step4_embed.py`"
    )
    st.stop()

sample_name = st.selectbox(
    "Demo sample (for LinkedIn / testing)",
    options=list(DEMO_TICKETS.keys()),
)

if "ticket_text" not in st.session_state:
    st.session_state.ticket_text = DEMO_TICKETS[sample_name]

if st.button("Load selected sample"):
    st.session_state.ticket_text = DEMO_TICKETS[sample_name]

ticket_text = st.text_area(
    "New support ticket",
    key="ticket_text",
    height=180,
    help="Pick a demo sample or type your own ticket.",
)

run = st.button("Triage ticket", type="primary")

if run:
    if not ticket_text.strip():
        st.warning("Please paste a ticket first.")
    else:
        with st.spinner("Retrieving chunks, then asking Qwen..."):
            try:
                result, chunks = triage_ticket(ticket_text)
            except SystemExit as exc:
                st.error(str(exc))
                st.stop()
            except Exception as exc:
                st.error(f"Triage failed: {exc}")
                st.stop()

        st.subheader("Triage result")
        col1, col2 = st.columns(2)
        col1.metric("Category", result.category)
        col2.metric("Priority", result.priority)

        st.write(
            "**Similar ticket ids:** "
            + (", ".join(result.similar_ticket_ids) if result.similar_ticket_ids else "(none)")
        )

        st.markdown("**Draft reply**")
        st.write(result.draft_reply)

        st.markdown("**Quotes from retrieved text**")
        for quote in result.quotes:
            st.markdown(f'- "{quote}"')

        st.markdown("**Notes**")
        st.write(result.notes)

        # Show the evidence pack so you can see this is real RAG, not dumping.
        with st.expander("Retrieved chunks (evidence)"):
            for i, (doc, score) in enumerate(chunks, start=1):
                source = Path(doc.metadata.get("source", "unknown")).name
                st.markdown(f"**{i}. {source}** — distance `{score:.4f}`")
                st.code(doc.page_content, language="text")
