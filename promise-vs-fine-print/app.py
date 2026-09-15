import html

import streamlit as st

from embed_store import index_pdfs
from extract_text import FINE_PRINT_PDF, PROMISE_PDF
from generate_answer import answer_question, citation_line
from theme import apply_theme

st.set_page_config(page_title="Promise vs Fine Print", layout="centered")
apply_theme()

if "store" not in st.session_state:
    st.session_state.store = None
if "store_key" not in st.session_state:
    st.session_state.store_key = None
if "result" not in st.session_state:
    st.session_state.result = None
if "error_message" not in st.session_state:
    st.session_state.error_message = None


def file_key(uploaded):
    if uploaded is None:
        return None
    return (uploaded.name, uploaded.size)


def verdict_class(verdict):
    value = (verdict or "").strip().lower()
    if value == "match":
        return "verdict-match"
    if value == "conflict":
        return "verdict-conflict"
    return "verdict-missing"


def render_hits(title, hits):
    st.markdown(f"**{title}**")
    if not hits:
        st.write("None")
        return
    for rank, (_index, score, chunk) in enumerate(hits, start=1):
        st.caption(
            f"#{rank}  score={score:.3f}  |  {chunk['source_file']}  |  page {chunk['page']}"
        )
        st.write(chunk["text"])


def render_result_card(question, data, id_map):
    verdict = html.escape(str(data.get("verdict") or "Missing"))
    promise_quote = html.escape(data.get("promise_quote") or "(none)")
    fine_quote = html.escape(data.get("fine_print_quote") or "(none)")
    reason = html.escape(data.get("reason") or "")
    promise_cite = html.escape(
        citation_line(data.get("promise_chunk_id"), id_map)
    )
    fine_cite = html.escape(
        citation_line(data.get("fine_print_chunk_id"), id_map)
    )
    q = html.escape(question)
    badge = verdict_class(data.get("verdict"))
    st.markdown(
        f"""
        <div class="result-card">
            <h2>Result</h2>
            <p>{q}</p>
            <div style="text-align:center;margin:0.8rem 0 0.4rem;">
                <span class="verdict {badge}">{verdict}</span>
            </div>
            <h3>Promise quote</h3>
            <div class="quote-box">{promise_quote}</div>
            <div class="cite">Used: {promise_cite}</div>
            <h3>Fine-print quote</h3>
            <div class="quote-box">{fine_quote}</div>
            <div class="cite">Used: {fine_cite}</div>
            <h3>Why</h3>
            <p>{reason}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.title("Promise vs Fine Print")
st.caption("RAG: retrieve chunks from both PDFs, then generate a verdict.")

col1, col2 = st.columns(2)
with col1:
    promise_file = st.file_uploader("1. Promise PDF (brochure / ads)", type=["pdf"])
with col2:
    fine_file = st.file_uploader("2. Fine print PDF (contract / T&Cs)", type=["pdf"])

use_samples = st.checkbox("Use the sample Harbor Study Pack PDFs", value=False)

question = st.text_input(
    "Question",
    placeholder="Is a laptop included?",
)

if st.button("Compare", type="primary", use_container_width=True):
    st.session_state.error_message = None
    st.session_state.result = None
    question_text = (question or "").strip()

    if not question_text:
        st.session_state.error_message = "Type a question first."
    elif not use_samples and (promise_file is None or fine_file is None):
        st.session_state.error_message = (
            "Upload both PDFs, or tick the sample PDFs checkbox."
        )
    else:
        try:
            if use_samples:
                store_key = ("sample", "sample")
                promise_source, fine_source = PROMISE_PDF, FINE_PRINT_PDF
                promise_name = fine_name = None
            else:
                store_key = (file_key(promise_file), file_key(fine_file))
                promise_source, fine_source = promise_file, fine_file
                promise_name = promise_file.name
                fine_name = fine_file.name

            if st.session_state.store_key != store_key or st.session_state.store is None:
                with st.spinner("Chunking and embedding (search index)..."):
                    matrix, chunks = index_pdfs(
                        promise_source,
                        fine_source,
                        promise_name,
                        fine_name,
                    )
                st.session_state.store = (matrix, chunks)
                st.session_state.store_key = store_key

            matrix, chunks = st.session_state.store
            with st.spinner("Retrieve, then generate from those chunks only..."):
                retrieval, data, id_map = answer_question(
                    question_text,
                    matrix=matrix,
                    chunks=chunks,
                )
            st.session_state.result = {
                "question": question_text,
                "retrieval": retrieval,
                "data": data,
                "id_map": id_map,
            }
        except Exception as exc:
            st.session_state.result = None
            st.session_state.error_message = (
                "Could not finish RAG. Check GEMINI_API_KEY and the PDFs. "
                f"Details: {exc}"
            )

if st.session_state.error_message:
    st.error(st.session_state.error_message)

if st.session_state.result:
    packed = st.session_state.result
    render_result_card(packed["question"], packed["data"], packed["id_map"])
    with st.expander("Chunks sent to Gemini (not the full PDFs)"):
        render_hits("Promise", packed["retrieval"]["promise"])
        render_hits("Fine print", packed["retrieval"]["fine_print"])
