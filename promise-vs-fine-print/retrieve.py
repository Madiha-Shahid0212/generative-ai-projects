"""Retrieve top chunks for a question. Search happens here, not inside Gemini."""

import sys

import numpy as np

from embed_store import load_or_build_store
from gemini_client import embed_texts

TOP_K = 2


def cosine_scores(query_vector, matrix):
    query = np.array(query_vector, dtype=np.float32)
    query_norm = np.linalg.norm(query)
    if query_norm == 0:
        raise ValueError("Query embedding was all zeros.")
    query = query / query_norm

    chunk_norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    chunk_norms = np.where(chunk_norms == 0, 1.0, chunk_norms)
    normalized = matrix / chunk_norms
    return normalized @ query


def top_k_for_source(chunks, scores, source_label, k=TOP_K):
    indexed = [
        (i, float(scores[i]), chunks[i])
        for i in range(len(chunks))
        if chunks[i]["source_label"] == source_label
    ]
    indexed.sort(key=lambda row: row[1], reverse=True)
    return indexed[:k]


def retrieve(question, k=TOP_K, matrix=None, chunks=None):
    if matrix is None or chunks is None:
        matrix, chunks = load_or_build_store()
    query_vector = embed_texts([question], task_type="RETRIEVAL_QUERY")[0]
    scores = cosine_scores(query_vector, matrix)
    return {
        "question": question,
        "promise": top_k_for_source(chunks, scores, "promise", k),
        "fine_print": top_k_for_source(chunks, scores, "fine_print", k),
    }


def print_hits(label, hits):
    print("=" * 60)
    print(label)
    print("=" * 60)
    if not hits:
        print("No chunks for this source.")
        return
    for rank, (index, score, chunk) in enumerate(hits, start=1):
        print(f"\n#{rank}  score={score:.3f}  store_index={index}")
        print(f"{chunk['source_file']} | page {chunk['page']}")
        print(chunk["text"])
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:]).strip()
    else:
        question = input("Question: ").strip()

    if not question:
        raise SystemExit("Please type a question.")

    print(f"\nQuestion: {question}\n")
    print("Gemini only made a vector for the question.")
    print("Numpy picked the nearest chunks. The model did not read the PDFs.\n")

    results = retrieve(question)
    print_hits("TOP PROMISE CHUNKS", results["promise"])
    print_hits("TOP FINE PRINT CHUNKS", results["fine_print"])
    print("Retrieve done. Next step: send ONLY these chunks to Gemini to write.")
