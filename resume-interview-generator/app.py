import html
import json

import streamlit as st
import streamlit.components.v1 as components

from gemini_client import generate_text
from json_parser import InterviewJsonError, parse_interview_json
from prompts import JSON_SYSTEM_INSTRUCTION, build_resume_prompt
from sample_resume import SAMPLE_RESUME
from theme import apply_theme, render_hero_pills, render_interview_result

st.set_page_config(
    page_title="Resume to Interview Questions Generator",
    layout="centered",
)

apply_theme()

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "result" not in st.session_state:
    st.session_state.result = None
if "error_message" not in st.session_state:
    st.session_state.error_message = None
if "do_generate" not in st.session_state:
    st.session_state.do_generate = False
if "show_json" not in st.session_state:
    st.session_state.show_json = False


def load_example_resume():
    st.session_state.resume_text = SAMPLE_RESUME
    st.session_state.error_message = None


def request_generate():
    st.session_state.do_generate = True


def show_gemini_json():
    st.session_state.show_json = True


def render_gemini_json(result):
    payload = html.escape(json.dumps(result, indent=2))
    st.markdown(
        f"""
        <div id="gemini-json-panel" class="json-card">
            <h3>Gemini JSON</h3>
            <pre>{payload}</pre>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.title("Resume to Interview Questions Generator")
st.caption("Paste a resume and generate interview questions.")
render_hero_pills()

st.text_area(
    "Resume",
    placeholder="Paste your resume text here...",
    height=260,
    key="resume_text",
)

left_col, right_col = st.columns(2)
with left_col:
    st.button(
        "Try Example Resume",
        use_container_width=True,
        on_click=load_example_resume,
        key="example_btn",
    )
with right_col:
    st.button(
        "Generate",
        type="primary",
        use_container_width=True,
        on_click=request_generate,
        key="generate_btn",
    )

st.button(
    "Gemini JSON",
    use_container_width=True,
    on_click=show_gemini_json,
    key="gemini_json_btn",
)

if st.session_state.do_generate:
    st.session_state.do_generate = False
    st.session_state.show_json = False
    resume_text = (st.session_state.resume_text or "").strip()
    st.session_state.error_message = None

    if not resume_text:
        st.session_state.result = None
        st.session_state.error_message = (
            "Please paste a resume, or click Try Example Resume first."
        )
    else:
        try:
            with st.spinner("Generating interview questions..."):
                raw_text = generate_text(
                    build_resume_prompt(resume_text),
                    system_instruction=JSON_SYSTEM_INSTRUCTION,
                    json_mode=True,
                )
                st.session_state.result = parse_interview_json(raw_text)
        except InterviewJsonError as exc:
            st.session_state.result = None
            st.session_state.error_message = str(exc)
        except Exception as exc:
            st.session_state.result = None
            st.session_state.error_message = (
                "Could not reach Gemini. Check your API key and internet, then try again. "
                f"Details: {exc}"
            )

if st.session_state.error_message:
    st.error(st.session_state.error_message)

if st.session_state.result:
    render_interview_result(st.session_state.result)

if st.session_state.show_json:
    if st.session_state.result:
        render_gemini_json(st.session_state.result)
        components.html(
            """
            <script>
              const el = window.parent.document.getElementById("gemini-json-panel");
              if (el) {
                el.scrollIntoView({ behavior: "smooth", block: "center" });
              }
            </script>
            """,
            height=0,
        )
    else:
        st.info("Generate interview questions first, then click Gemini JSON.")
