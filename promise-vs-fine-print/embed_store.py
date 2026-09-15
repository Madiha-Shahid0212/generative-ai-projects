"""Embed chunks and save vectors with numpy. This is not search yet."""

import json
from pathlib import Path

import numpy as np

from chunk_text import pages_to_chunks
from extract_text import FINE_PRINT_PDF, PROMISE_PDF, extract_pages
from gemini_client import embed_texts

STORE_DIR = Path(__file__).resolve().parent / "store"
VECTORS_PATH = STORE_DIR / "vectors.npy"
META_PATH = STORE_DIR / "metadata.json"


def all_chunks():
    promise = pages_to_chunks(extract_pages(PROMISE_PDF), "promise")
    fine_print = pages_to_chunks(extract_pages(FINE_PRINT_PDF), "fine_print")
    return promise + fine_print


def chunks_from_pdfs(
    promise_source,
    fine_print_source,
    promise_name=None,
    fine_print_name=None,
):
    promise = pages_to_chunks(
        extract_pages(promise_source, promise_name),
        "promise",
    )
    fine_print = pages_to_chunks(
        extract_pages(fine_print_source, fine_print_name),
        "fine_print",
    )
    chunks = promise + fine_print
    if not chunks:
        raise ValueError("No text found in the PDFs.")
    return chunks


def embed_chunks_to_matrix(chunks):
    texts = [chunk["text"] for chunk in chunks]
    vectors = embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")
    return np.array(vectors, dtype=np.float32)


def index_pdfs(
    promise_source,
    fine_print_source,
    promise_name=None,
    fine_print_name=None,
):
    chunks = chunks_from_pdfs(
        promise_source,
        fine_print_source,
        promise_name,
        fine_print_name,
    )
    return embed_chunks_to_matrix(chunks), chunks


def build_store(chunks):
    texts = [chunk["text"] for chunk in chunks]
    vectors = embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")
    matrix = np.array(vectors, dtype=np.float32)
    STORE_DIR.mkdir(exist_ok=True)
    np.save(VECTORS_PATH, matrix)
    META_PATH.write_text(json.dumps(chunks, indent=2), encoding="utf-8")
    return matrix


def load_store():
    matrix = np.load(VECTORS_PATH)
    chunks = json.loads(META_PATH.read_text(encoding="utf-8"))
    return matrix, chunks


def load_or_build_store():
    if VECTORS_PATH.exists() and META_PATH.exists():
        return load_store()
    chunks = all_chunks()
    matrix = build_store(chunks)
    return matrix, chunks


def print_vectors(matrix, chunks):
    print("=" * 60)
    print("EMBEDDINGS (numpy store)")
    print(f"{matrix.shape[0]} vectors x {matrix.shape[1]} numbers each")
    print("=" * 60)
    for i, chunk in enumerate(chunks):
        preview = ", ".join(f"{x:.4f}" for x in matrix[i][:8])
        print(
            f"\n[{i}] {chunk['source_label']} | {chunk['source_file']} | "
            f"page {chunk['page']}"
        )
        print(f"text: {chunk['text'][:90]}...")
        print(f"vector dim={matrix.shape[1]}  first 8 numbers: [{preview}, ...]")
    print(f"\nSaved {VECTORS_PATH}")
    print(f"Saved {META_PATH}")
    print("Done. Vectors are stored. We have not searched a question yet.")


if __name__ == "__main__":
    chunks = all_chunks()
    matrix = build_store(chunks)
    print_vectors(matrix, chunks)
