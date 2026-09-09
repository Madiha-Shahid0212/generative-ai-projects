import streamlit as st

from gemini_client import generate_text
from scenarios import SCENARIOS
from theme import apply_theme

FORMAT_NOTE = (
    " Reply in clear markdown with short headings and bullet lists. "
    "Do not use LaTeX or backslash math such as \\times or \\mathbf."
)


def prepare_display_text(text):
    cleaned = (
        text.replace("\\times", "×")
        .replace("\\cdot", "·")
        .replace("\\mathbf", "")
        .replace("\\textbf", "")
        .replace("{", "")
        .replace("}", "")
    )
    return cleaned.replace("$", r"\$")


def render_response(text):
    st.markdown(prepare_display_text(text))

st.set_page_config(
    page_title="CoT + Persona Reasoning Comparator",
    layout="wide",
)

apply_theme()

st.title("Chain-of-Thought + Persona Reasoning Comparator")
st.caption("Compare a plain answer with a persona-based step-by-step answer.")

category = st.selectbox(
    "Scenario category",
    options=list(SCENARIOS.keys()),
)

st.text(f"Persona: {SCENARIOS[category]['persona']}")

st.text_area(
    "Scenario",
    value=SCENARIOS[category]["example"],
    height=180,
    key=f"scenario_{category}",
)

if "plain_response" not in st.session_state:
    st.session_state.plain_response = None
    st.session_state.cot_response = None

if "error_message" not in st.session_state:
    st.session_state.error_message = None

if st.button("Compare", type="primary"):
    scenario_text = st.session_state[f"scenario_{category}"].strip()
    persona_instruction = SCENARIOS[category]["persona_instruction"]
    st.session_state.error_message = None

    if not scenario_text:
        st.session_state.error_message = "Please enter a scenario before comparing."
    else:
        try:
            with st.spinner("Generating both answers..."):
                prompt = scenario_text + FORMAT_NOTE
                plain_response = generate_text(prompt)
                cot_response = generate_text(
                    prompt,
                    system_instruction=(
                        f"{persona_instruction} "
                        "Think step by step before you give the answer."
                    ),
                )
            st.session_state.plain_response = plain_response
            st.session_state.cot_response = cot_response
        except Exception as exc:
            st.session_state.error_message = (
                "Could not get answers from Gemini. "
                "Check your API key and internet connection, then try again. "
                f"Details: {exc}"
            )

if st.session_state.error_message:
    st.error(st.session_state.error_message)

if st.session_state.plain_response and st.session_state.cot_response:
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Plain response")
        render_response(st.session_state.plain_response)

    with right_col:
        st.subheader("Chain-of-Thought + Persona")
        render_response(st.session_state.cot_response)
