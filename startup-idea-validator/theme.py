import html
import re

import streamlit as st

from prompts import AGENT_PROMPTS, FOUNDER_AGENT_KEY, INVESTOR_AGENT_KEY, MARKET_ANALYST_AGENT_KEY

THEME_CSS = """
<style>
    @import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap");

    :root {
        --bg: #0d0d0d;
        --bg-elevated: #161616;
        --text: #e8eef5;
        --muted: #9aa7b5;
        --accent: #3b82f6;
        --accent-dim: rgba(59, 130, 246, 0.28);
        --founder: #3b82f6;
        --investor: #f59e0b;
        --market: #a78bfa;
    }

    .stApp {
        background:
            radial-gradient(900px 420px at 12% -10%, rgba(59, 130, 246, 0.18) 0%, transparent 50%),
            radial-gradient(700px 380px at 90% 0%, rgba(167, 139, 250, 0.12) 0%, transparent 48%),
            linear-gradient(180deg, #121212 0%, var(--bg) 40%, #0a0a0a 100%);
        color: var(--text);
        font-family: "DM Sans", sans-serif;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stToolbar"] {
        visibility: hidden;
        height: 0;
    }

    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    h1 {
        font-family: "Space Grotesk", sans-serif !important;
        color: #ffffff !important;
        letter-spacing: 0.02em;
        margin-bottom: 0.35rem !important;
    }

    [data-testid="stCaption"] {
        color: var(--muted) !important;
        font-size: 1.02rem !important;
        margin-bottom: 1.4rem !important;
    }

    label, [data-testid="stWidgetLabel"] p {
        color: var(--text) !important;
        font-weight: 600 !important;
    }

    [data-testid="stTextArea"] textarea {
        background-color: var(--bg-elevated) !important;
        color: var(--text) !important;
        border: 1px solid #2a3340 !important;
        border-radius: 14px !important;
        font-size: 0.98rem !important;
        line-height: 1.55 !important;
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent), 0 0 16px var(--accent-dim) !important;
    }

    .stButton > button {
        background: #1a1a1a !important;
        color: var(--text) !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.03em !important;
        padding: 0.65rem 1.2rem !important;
    }

    .stButton > button:hover {
        border-color: #60a5fa !important;
        box-shadow: 0 0 16px var(--accent-dim);
    }

    .stButton > button[kind="primary"] {
        background: #3b82f6 !important;
        color: #0d0d0d !important;
        border: none !important;
        box-shadow: 0 0 18px var(--accent-dim);
    }

    .stButton > button[kind="primary"]:hover {
        background: #60a5fa !important;
        color: #0d0d0d !important;
    }

    [data-testid="stHorizontalBlock"] {
        gap: 1rem;
        margin-top: 0.7rem;
    }

    .agent-card {
        background: #141414;
        border-radius: 16px;
        padding: 1.15rem 1.25rem 1.3rem;
        border: 1px solid #2a2a2a;
        margin-bottom: 0.2rem;
        height: 100%;
    }

    .agent-card.founder {
        border-left: 4px solid var(--founder);
        box-shadow: 0 0 18px rgba(59, 130, 246, 0.16);
    }

    .agent-card.investor {
        border-left: 4px solid var(--investor);
        box-shadow: 0 0 18px rgba(245, 158, 11, 0.16);
    }

    .agent-card.market_analyst {
        border-left: 4px solid var(--market);
        box-shadow: 0 0 18px rgba(167, 139, 250, 0.16);
    }

    .agent-card h3 {
        font-family: "Space Grotesk", sans-serif;
        margin: 0 0 0.85rem;
        font-size: 1.08rem;
        color: #ffffff;
    }

    .agent-card.founder h3 { color: var(--founder); }
    .agent-card.investor h3 { color: var(--investor); }
    .agent-card.market_analyst h3 { color: var(--market); }

    .agent-card h4 {
        font-family: "Space Grotesk", sans-serif;
        margin: 1rem 0 0.45rem;
        font-size: 0.95rem;
        color: #ffffff;
        letter-spacing: 0.02em;
    }

    .agent-card .agent-body {
        color: var(--text);
        font-size: 0.9rem;
        line-height: 1.55;
        max-height: 62vh;
        overflow-y: auto;
        padding-right: 0.35rem;
    }

    .agent-card .agent-body p {
        margin: 0 0 0.55rem;
        color: var(--text);
        font-size: 0.94rem;
    }

    .results-wrap {
        margin-top: 1.6rem;
    }

    .pipeline-flow {
        margin: 0.4rem 0 1.4rem;
        padding: 1rem 1.15rem 1.1rem;
        border-radius: 16px;
        background: #141414;
        border: 1px solid #2a3340;
        box-shadow: 0 0 18px rgba(59, 130, 246, 0.12);
    }

    .pipeline-flow .pipeline-label {
        font-family: "Space Grotesk", sans-serif;
        font-size: 0.82rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #9aa7b5;
        margin-bottom: 0.7rem;
    }

    .pipeline-flow .pipeline-steps {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.45rem 0.55rem;
        color: #e8eef5;
        font-size: 0.95rem;
        font-weight: 600;
    }

    .pipeline-chip {
        display: inline-block;
        padding: 0.4rem 0.75rem;
        border-radius: 999px;
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
    }

    .pipeline-chip.idea { border-color: #64748b; }
    .pipeline-chip.founder { border-color: #3b82f6; color: #93c5fd; }
    .pipeline-chip.investor { border-color: #f59e0b; color: #fbbf24; }
    .pipeline-chip.market { border-color: #a78bfa; color: #c4b5fd; }

    .pipeline-arrow {
        color: #64748b;
        font-weight: 700;
    }

    .pipeline-note {
        margin-top: 0.65rem;
        color: #9aa7b5;
        font-size: 0.86rem;
    }

    [data-testid="stAlert"] {
        background-color: #241016 !important;
        border: 1px solid #ff5c8a !important;
        border-radius: 12px !important;
        color: #ffd6e2 !important;
        margin-top: 1rem;
    }

    [data-testid="stSpinner"] {
        color: #93c5fd !important;
    }
</style>
"""

AGENT_CARD_CLASS = {
    "founder": "founder",
    "investor": "investor",
    "market_analyst": "market_analyst",
}


def apply_theme():
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def render_pipeline_flow():
    st.markdown(
        """
        <div class="pipeline-flow">
            <div class="pipeline-label">Multi-agent pipeline</div>
            <div class="pipeline-steps">
                <span class="pipeline-chip idea">💡 Your idea</span>
                <span class="pipeline-arrow">→</span>
                <span class="pipeline-chip founder">🚀 Founder Agent</span>
                <span class="pipeline-arrow">→</span>
                <span class="pipeline-chip investor">💼 Investor Agent</span>
                <span class="pipeline-arrow">&amp;</span>
                <span class="pipeline-chip market">📊 Market Analyst Agent</span>
            </div>
            <div class="pipeline-note">
                Founder expands the idea first. Investor and Market Analyst both
                read that expanded idea — they do not read each other.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_agent_body(text):
    escaped = html.escape(text.strip())
    escaped = re.sub(r"^## (.+)$", r"<h4>\1</h4>", escaped, flags=re.MULTILINE)
    escaped = escaped.replace("**", "")
    paragraphs = escaped.split("\n")
    html_parts = []
    for line in paragraphs:
        if line.startswith("<h4>"):
            html_parts.append(line)
        elif line.strip() == "":
            continue
        else:
            html_parts.append(f"<p>{line}</p>")
    return "".join(html_parts)


def render_agent_card(agent_key, body):
    agent = AGENT_PROMPTS[agent_key]
    css_class = AGENT_CARD_CLASS[agent_key]
    body_html = _format_agent_body(body)
    st.markdown(
        f"""
        <div class="agent-card {css_class}">
            <h3>{agent["emoji"]} {agent["name"]}</h3>
            <div class="agent-body">{body_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_validation_results(result):
    founder_col, investor_col, market_col = st.columns(3, gap="medium")
    with founder_col:
        render_agent_card(FOUNDER_AGENT_KEY, result["founder"])
    with investor_col:
        render_agent_card(INVESTOR_AGENT_KEY, result["investor"])
    with market_col:
        render_agent_card(MARKET_ANALYST_AGENT_KEY, result["market_analyst"])
