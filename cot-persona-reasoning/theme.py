import streamlit as st

NEON_THEME_CSS = """
<style>
    @import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap");

    :root {
        --bg: #0d0d0d;
        --bg-elevated: #161616;
        --text: #e8eef5;
        --muted: #9aa7b5;
        --neon: #00e5ff;
        --neon-dim: rgba(0, 229, 255, 0.22);
        --purple: #b388ff;
    }

    .stApp {
        background: radial-gradient(1200px 500px at 10% -10%, #1a1430 0%, var(--bg) 45%);
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
        padding-top: 2.4rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }

    h1 {
        font-family: "Space Grotesk", sans-serif !important;
        color: var(--neon) !important;
        letter-spacing: 0.02em;
        text-shadow: 0 0 18px var(--neon-dim);
        margin-bottom: 0.35rem !important;
    }

    [data-testid="stCaption"] {
        color: var(--muted) !important;
        font-size: 1rem !important;
        margin-bottom: 1.6rem !important;
    }

    label, [data-testid="stWidgetLabel"] p {
        color: var(--text) !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em;
    }

    [data-testid="stText"] {
        color: var(--purple) !important;
        margin-bottom: 0.8rem !important;
    }

    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--neon) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
        box-shadow: 0 0 12px var(--neon-dim);
    }

    [data-testid="stTextArea"] textarea {
        background-color: var(--bg-elevated) !important;
        color: var(--text) !important;
        border: 1px solid #2a3a4a !important;
        border-radius: 10px !important;
        font-size: 0.98rem !important;
        line-height: 1.55 !important;
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--neon) !important;
        box-shadow: 0 0 0 1px var(--neon), 0 0 16px var(--neon-dim) !important;
    }

    .stButton > button {
        background: var(--neon) !important;
        color: #041016 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        padding: 0.55rem 1.4rem !important;
        box-shadow: 0 0 18px var(--neon-dim);
        margin-top: 0.4rem;
    }

    .stButton > button:hover {
        background: #7cffb2 !important;
        color: #041016 !important;
        box-shadow: 0 0 22px rgba(124, 255, 178, 0.35);
    }

    [data-testid="stHorizontalBlock"] {
        gap: 1.2rem;
        margin-top: 1.4rem;
    }

    [data-testid="stHorizontalBlock"] [data-testid="stHeading"] h3 {
        font-family: "Space Grotesk", sans-serif !important;
        color: var(--neon) !important;
        font-size: 1.15rem !important;
    }

    [data-testid="stAlert"] {
        background-color: #241016 !important;
        border: 1px solid #ff5c8a !important;
        border-radius: 10px !important;
        color: #ffd6e2 !important;
        margin-top: 1rem;
    }
</style>
"""


def apply_theme():
    st.markdown(NEON_THEME_CSS, unsafe_allow_html=True)
