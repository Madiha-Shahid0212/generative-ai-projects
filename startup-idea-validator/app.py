import streamlit as st

from pipeline import run_validation_pipeline
from sample_idea import EXAMPLE_IDEA
from theme import apply_theme, render_pipeline_flow, render_validation_results


def friendly_api_error(exc):
    text = str(exc)
    if "503" in text or "UNAVAILABLE" in text or "high demand" in text.lower():
        return (
            "Gemini is busy right now (high demand on Google's side). "
            "Your API key is fine. Wait 30–60 seconds, then click "
            "Validate Idea again."
        )
    if "429" in text or "RESOURCE_EXHAUSTED" in text or "quota" in text.lower():
        return (
            "Gemini free-tier quota ran out for the current model "
            "(this one allows 20 requests per day). Wait a minute and try "
            "again, or wait until the daily quota resets. "
            "A pipeline uses 3 requests (one per agent)."
        )
    return (
        "Could not finish the agent pipeline. Check your API key and "
        f"internet, then try again. Details: {exc}"
    )

st.set_page_config(
    page_title="Startup Idea Validator",
    layout="wide",
)

apply_theme()

if "idea_text" not in st.session_state:
    st.session_state.idea_text = ""
if "result" not in st.session_state:
    st.session_state.result = None
if "do_validate" not in st.session_state:
    st.session_state.do_validate = False
if "error_message" not in st.session_state:
    st.session_state.error_message = None


def load_example_idea():
    st.session_state.idea_text = EXAMPLE_IDEA
    st.session_state.error_message = None


def request_validate():
    st.session_state.do_validate = True


st.title("Startup Idea Validator")
st.caption("Describe your startup idea. Three agents will review it.")
render_pipeline_flow()

st.text_area(
    "Your startup idea",
    placeholder="Write 2–5 lines about your startup idea...",
    height=160,
    key="idea_text",
)

example_col, validate_col = st.columns(2)
with example_col:
    st.button(
        "Try Example Idea",
        use_container_width=True,
        on_click=load_example_idea,
        key="example_btn",
    )
with validate_col:
    st.button(
        "Validate Idea",
        type="primary",
        use_container_width=True,
        on_click=request_validate,
        key="validate_btn",
    )

if st.session_state.do_validate:
    st.session_state.do_validate = False
    idea_text = (st.session_state.idea_text or "").strip()
    st.session_state.error_message = None

    if not idea_text:
        st.session_state.result = None
        st.session_state.error_message = (
            "Please write a startup idea, or click Try Example Idea first."
        )
    else:
        status_box = st.status("Starting multi-agent pipeline...", expanded=True)

        def on_status(message):
            status_box.update(label=message, state="running")
            status_box.write(message)

        try:
            st.session_state.result = run_validation_pipeline(
                idea_text,
                on_status=on_status,
            )
            status_box.update(label="Pipeline complete.", state="complete")
        except Exception as exc:
            st.session_state.result = None
            status_box.update(label="Pipeline failed.", state="error")
            st.session_state.error_message = friendly_api_error(exc)

if st.session_state.error_message:
    st.error(st.session_state.error_message)

if st.session_state.result:
    render_validation_results(st.session_state.result)
