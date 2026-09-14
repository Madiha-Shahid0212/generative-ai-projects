import html

import streamlit as st

NEON_THEME_CSS = """
<style>
    @import url("https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Orbitron:wght@600;700&display=swap");

    :root {
        --bg: #07060d;
        --bg-elevated: #12101c;
        --panel: rgba(22, 16, 42, 0.72);
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
            radial-gradient(800px 500px at 50% 110%, rgba(255, 43, 214, 0.12) 0%, transparent 45%),
            linear-gradient(180deg, #120b22 0%, var(--bg) 42%, #0a0814 100%);
        color: var(--text);
        font-family: "Outfit", sans-serif;
    }

    .stApp::before {
        content: "";
        pointer-events: none;
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(rgba(0, 240, 255, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(155, 109, 255, 0.05) 1px, transparent 1px);
        background-size: 48px 48px;
        mask-image: radial-gradient(ellipse at center, black 20%, transparent 78%);
        z-index: -1;
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
        max-width: 860px;
        position: relative;
        z-index: 1;
    }

    h1 {
        font-family: "Orbitron", sans-serif !important;
        color: #ffffff !important;
        letter-spacing: 0.04em;
        text-shadow:
            0 0 14px var(--cyan-glow),
            0 0 28px var(--purple-glow);
        margin-bottom: 0.4rem !important;
        text-align: center;
    }

    [data-testid="stCaption"] {
        color: var(--muted) !important;
        font-size: 1.02rem !important;
        margin-bottom: 1.1rem !important;
        text-align: center;
    }

    .neon-pills {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.7rem;
        margin: 0.4rem 0 1.6rem;
    }

    .neon-pills span {
        display: inline-block;
        padding: 0.55rem 1.15rem;
        border-radius: 999px;
        background: rgba(24, 18, 48, 0.9);
        border: 1px solid rgba(155, 109, 255, 0.55);
        color: var(--text);
        font-size: 0.92rem;
        font-weight: 500;
        box-shadow: 0 0 16px rgba(155, 109, 255, 0.18);
    }

    .neon-pills span.accent {
        border-color: rgba(0, 240, 255, 0.7);
        box-shadow: 0 0 18px var(--cyan-glow);
    }

    label, [data-testid="stWidgetLabel"] p {
        color: var(--text) !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em;
    }

    [data-testid="stTextArea"] textarea {
        background-color: var(--bg-elevated) !important;
        color: var(--text) !important;
        border: 1px solid rgba(155, 109, 255, 0.45) !important;
        border-radius: 18px !important;
        font-size: 0.98rem !important;
        line-height: 1.55 !important;
        box-shadow: inset 0 0 24px rgba(155, 109, 255, 0.08);
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--cyan) !important;
        box-shadow:
            0 0 0 1px var(--cyan),
            0 0 22px var(--cyan-glow) !important;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        background: rgba(24, 18, 48, 0.95) !important;
        color: var(--text) !important;
        border: 1px solid var(--purple) !important;
        border-radius: 999px !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        padding: 0.7rem 1.2rem !important;
        box-shadow: 0 0 16px var(--purple-glow);
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        border-color: var(--magenta) !important;
        color: #ffffff !important;
        box-shadow: 0 0 22px var(--magenta-glow);
    }

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {
        background: linear-gradient(90deg, #7a3cff 0%, #00c8e0 100%) !important;
        color: #07060d !important;
        border: none !important;
        box-shadow:
            0 0 18px var(--cyan-glow),
            0 0 28px var(--purple-glow);
    }

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover {
        background: linear-gradient(90deg, #ff2bd6 0%, #00f0ff 100%) !important;
        color: #07060d !important;
        box-shadow: 0 0 26px var(--magenta-glow);
    }

    [data-testid="stHorizontalBlock"] {
        gap: 1rem;
        margin-top: 0.6rem;
    }

    [data-testid="stSpinner"] {
        text-align: center;
        color: var(--cyan) !important;
    }

    [data-testid="stAlert"] {
        background-color: rgba(36, 12, 28, 0.92) !important;
        border: 1px solid var(--magenta) !important;
        border-radius: 16px !important;
        color: #ffd6e2 !important;
        margin-top: 1rem;
        box-shadow: 0 0 18px var(--magenta-glow);
    }

    .result-card {
        margin-top: 1.8rem;
        padding: 1.4rem 1.5rem 1.6rem;
        border-radius: 22px;
        background: rgba(18, 14, 36, 0.82);
        border: 1px solid rgba(155, 109, 255, 0.4);
        box-shadow: 0 0 28px rgba(155, 109, 255, 0.14);
    }

    .result-card h2 {
        font-family: "Orbitron", sans-serif;
        font-size: 1.45rem;
        color: #ffffff;
        text-align: center;
        margin: 0 0 0.85rem;
        text-shadow: 0 0 16px var(--cyan-glow);
    }

    .result-card h3 {
        font-family: "Outfit", sans-serif;
        font-size: 1.02rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--cyan);
        margin: 1.2rem 0 0.7rem;
    }

    .level-row {
        display: flex;
        justify-content: center;
        margin-bottom: 0.4rem;
    }

    .level-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.88rem;
        letter-spacing: 0.04em;
    }

    .level-beginner {
        color: #041016;
        background: #7CFFB2;
        box-shadow: 0 0 16px rgba(124, 255, 178, 0.35);
    }

    .level-intermediate {
        color: #041016;
        background: var(--cyan);
        box-shadow: 0 0 16px var(--cyan-glow);
    }

    .level-advanced {
        color: #ffffff;
        background: var(--magenta);
        box-shadow: 0 0 16px var(--magenta-glow);
    }

    .skill-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
    }

    .skill-badge {
        display: inline-block;
        padding: 0.4rem 0.9rem;
        border-radius: 999px;
        background: rgba(24, 18, 48, 0.95);
        border: 1px solid rgba(0, 240, 255, 0.55);
        color: var(--text);
        font-size: 0.9rem;
        box-shadow: 0 0 12px var(--cyan-glow);
    }

    .weak-box {
        background: rgba(255, 43, 214, 0.1);
        border: 1px solid rgba(255, 43, 214, 0.55);
        border-radius: 16px;
        padding: 0.9rem 1.1rem;
        box-shadow: 0 0 18px var(--magenta-glow);
    }

    .weak-box ul,
    .question-list {
        margin: 0;
        padding-left: 1.15rem;
        color: var(--text);
        line-height: 1.65;
    }

    .question-list li {
        margin-bottom: 0.45rem;
    }

    .json-card {
        margin-top: 1.4rem;
        padding: 1.3rem 1.4rem 1.5rem;
        border-radius: 22px;
        background: rgba(18, 14, 36, 0.82);
        border: 1px solid rgba(0, 240, 255, 0.45);
        box-shadow: 0 0 28px rgba(0, 240, 255, 0.14);
        scroll-margin-top: 1.4rem;
    }

    .json-card h3 {
        font-family: "Orbitron", sans-serif;
        font-size: 1.05rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--cyan);
        margin: 0 0 0.9rem;
        text-shadow: 0 0 14px var(--cyan-glow);
    }

    .json-card pre {
        margin: 0;
        overflow-x: auto;
        color: #e8e4ff;
        background: #0c0a16;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        border: 1px solid rgba(155, 109, 255, 0.28);
        font-size: 0.9rem;
        line-height: 1.55;
        white-space: pre-wrap;
        word-break: break-word;
    }

    iframe[height="0"] {
        display: none;
    }
</style>
"""


def apply_theme():
    st.markdown(NEON_THEME_CSS, unsafe_allow_html=True)


LEVEL_CLASS = {
    "Beginner": "level-beginner",
    "Intermediate": "level-intermediate",
    "Advanced": "level-advanced",
}


def render_hero_pills():
    st.markdown(
        """
        <div class="neon-pills">
            <span>Resume analysis</span>
            <span class="accent">Interview questions</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_interview_result(result):
    name = html.escape(result["candidate_name"])
    level = result["difficulty_level"]
    level_class = LEVEL_CLASS.get(level, "level-beginner")
    skills_html = "".join(
        f'<span class="skill-badge">{html.escape(skill)}</span>'
        for skill in result["skills"]
    )
    weak_html = "".join(
        f"<li>{html.escape(area)}</li>" for area in result["weak_areas"]
    )
    questions_html = "".join(
        f"<li>{html.escape(question)}</li>"
        for question in result["suggested_questions"]
    )

    st.markdown(
        f"""
        <div class="result-card">
            <h2>{name}</h2>
            <div class="level-row">
                <span class="level-badge {level_class}">{html.escape(level)}</span>
            </div>
            <h3>Skills</h3>
            <div class="skill-wrap">{skills_html}</div>
            <h3>Weak areas</h3>
            <div class="weak-box"><ul>{weak_html}</ul></div>
            <h3>Suggested questions</h3>
            <ol class="question-list">{questions_html}</ol>
        </div>
        """,
        unsafe_allow_html=True,
    )
