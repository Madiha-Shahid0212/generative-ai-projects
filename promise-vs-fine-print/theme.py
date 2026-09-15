import streamlit as st

NEON_THEME_CSS = """
<style>
    @import url("https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Orbitron:wght@600;700&display=swap");

    :root {
        --bg: #07060d;
        --text: #f4f1ff;
        --muted: #b7a8d9;
        --cyan: #00f0ff;
        --magenta: #ff2bd6;
        --purple: #9b6dff;
        --cyan-glow: rgba(0, 240, 255, 0.28);
        --magenta-glow: rgba(255, 43, 214, 0.28);
        --purple-glow: rgba(155, 109, 255, 0.35);
    }

    .stApp {
        background:
            radial-gradient(900px 420px at 8% -8%, rgba(155, 109, 255, 0.28) 0%, transparent 55%),
            radial-gradient(700px 380px at 92% 8%, rgba(0, 240, 255, 0.16) 0%, transparent 50%),
            linear-gradient(180deg, #120b22 0%, var(--bg) 42%, #0a0814 100%);
        color: var(--text);
        font-family: "Outfit", sans-serif;
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { visibility: hidden; height: 0; }

    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 3rem;
        max-width: 860px;
    }

    h1 {
        font-family: "Orbitron", sans-serif !important;
        color: #ffffff !important;
        letter-spacing: 0.04em;
        text-shadow: 0 0 14px var(--cyan-glow), 0 0 28px var(--purple-glow);
        text-align: center;
    }

    [data-testid="stCaption"] {
        color: var(--muted) !important;
        text-align: center;
        font-size: 1.02rem !important;
    }

    label, [data-testid="stWidgetLabel"] p {
        color: var(--text) !important;
        font-weight: 600 !important;
    }

    [data-testid="stTextInput"] input {
        background-color: #12101c !important;
        color: var(--text) !important;
        border: 1px solid rgba(155, 109, 255, 0.45) !important;
        border-radius: 14px !important;
    }

    .stButton > button {
        border-radius: 999px !important;
        font-weight: 700 !important;
        border: 1px solid var(--purple) !important;
        background: rgba(24, 18, 48, 0.95) !important;
        color: var(--text) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #7a3cff 0%, #00c8e0 100%) !important;
        color: #07060d !important;
        border: none !important;
    }

    [data-testid="stAlert"] {
        border-radius: 16px !important;
    }

    .result-card {
        margin-top: 1.4rem;
        padding: 1.4rem 1.5rem 1.6rem;
        border-radius: 22px;
        background: rgba(18, 14, 36, 0.82);
        border: 1px solid rgba(155, 109, 255, 0.4);
        box-shadow: 0 0 28px rgba(155, 109, 255, 0.14);
    }

    .result-card h2 {
        font-family: "Orbitron", sans-serif;
        font-size: 1.2rem;
        color: #ffffff;
        text-align: center;
        margin: 0 0 1rem;
    }

    .result-card h3 {
        font-size: 0.92rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--cyan);
        margin: 1.1rem 0 0.45rem;
    }

    .quote-box {
        background: rgba(12, 10, 22, 0.9);
        border: 1px solid rgba(0, 240, 255, 0.3);
        border-radius: 14px;
        padding: 0.85rem 1rem;
        color: var(--text);
        line-height: 1.55;
    }

    .cite {
        color: var(--muted);
        font-size: 0.88rem;
        margin-top: 0.35rem;
    }

    .verdict {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 999px;
        font-weight: 700;
        letter-spacing: 0.04em;
    }

    .verdict-match { background: #7CFFB2; color: #041016; }
    .verdict-conflict { background: var(--magenta); color: #ffffff; }
    .verdict-missing { background: #3a3450; color: #f4f1ff; }
</style>
"""


def apply_theme():
    st.markdown(NEON_THEME_CSS, unsafe_allow_html=True)
