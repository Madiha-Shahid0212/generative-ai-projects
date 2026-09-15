"""Generate a verdict from retrieved chunks only. This completes the RAG loop."""

import json
import re
import sys

from gemini_client import generate_text
from retrieve import print_hits, retrieve

SYSTEM = """
You compare a marketing Promise with Fine Print.
Use ONLY the retrieved chunks in the user message. Never use outside knowledge.
Never assume you have the full PDFs.

Return JSON with keys:
- promise_quote: short quote copied from a Promise chunk, or ""
- promise_chunk_id: like "P0", or null if nothing relevant
- fine_print_quote: short quote copied from a Fine Print chunk, or ""
- fine_print_chunk_id: like "F0", or null if nothing relevant
- verdict: exactly one of Match, Conflict, Missing
- reason: one or two sentences

Verdict rules:
- Match: both sides speak to the question and agree
- Conflict: both sides speak to the question and disagree
- Missing: one or both sides do not speak to the question
""".strip()


def format_chunk_block(hits, prefix):
    lines = []
    id_to_chunk = {}
    for i, (_index, score, chunk) in enumerate(hits):
        chunk_id = f"{prefix}{i}"
        id_to_chunk[chunk_id] = {"score": score, **chunk}
        lines.append(
            f"[{chunk_id}] file={chunk['source_file']} page={chunk['page']} "
            f"score={score:.3f}\n{chunk['text']}"
        )
    return "\n\n".join(lines), id_to_chunk


def build_prompt(question, retrieval):
    promise_block, promise_ids = format_chunk_block(retrieval["promise"], "P")
    fine_block, fine_ids = format_chunk_block(retrieval["fine_print"], "F")
    prompt = f"""Question: {question}

PROMISE CHUNKS (retrieved only):
{promise_block}

FINE PRINT CHUNKS (retrieved only):
{fine_block}
"""
    return prompt, {**promise_ids, **fine_ids}


def parse_json(raw_text):
    text = (raw_text or "").strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError("Gemini did not return valid JSON.") from error


def citation_line(chunk_id, id_map):
    if not chunk_id or chunk_id not in id_map:
        return "no matching retrieved chunk"
    chunk = id_map[chunk_id]
    return (
        f"{chunk_id} | {chunk['source_file']} | page {chunk['page']} "
        f"| score={chunk['score']:.3f}"
    )


def print_answer(question, data, id_map):
    print("=" * 60)
    print("GROUNDED ANSWER (retrieved chunks only)")
    print("=" * 60)
    print(f"\nQuestion: {question}")
    print(f"\nPromise quote:\n  {data.get('promise_quote') or '(none)'}")
    print(f"  used: {citation_line(data.get('promise_chunk_id'), id_map)}")
    print(f"\nFine-print quote:\n  {data.get('fine_print_quote') or '(none)'}")
    print(f"  used: {citation_line(data.get('fine_print_chunk_id'), id_map)}")
    print(f"\nVerdict: {data.get('verdict')}")
    print(f"Reason: {data.get('reason')}")
    print()


def answer_question(question, matrix=None, chunks=None):
    retrieval = retrieve(question, matrix=matrix, chunks=chunks)
    prompt, id_map = build_prompt(question, retrieval)
    raw = generate_text(prompt, system_instruction=SYSTEM)
    data = parse_json(raw)
    return retrieval, data, id_map


if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:]).strip()
    else:
        question = input("Question: ").strip()

    if not question:
        raise SystemExit("Please type a question.")

    retrieval, data, id_map = answer_question(question)
    print("\nThese chunks went to Gemini — not the full PDFs.\n")
    print_hits("RETRIEVED PROMISE", retrieval["promise"])
    print_hits("RETRIEVED FINE PRINT", retrieval["fine_print"])
    print_answer(question, data, id_map)
    print("This is retrieve-then-generate. That is RAG.")
