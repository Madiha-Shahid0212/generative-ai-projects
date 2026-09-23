"""
Step 5 — Retrieve only (no Qwen).

We embed the NEW ticket the same way, then ask Chroma:
"Which stored chunks are closest in meaning?"
That shortlist is retrieval. Generation comes in Step 6.
"""

from pathlib import Path

from langchain_chroma import Chroma

from step4_embed import CHROMA_DIR, build_embeddings


# How many closest chunks to return.
TOP_K = 5

# A fake NEW support ticket — not already saved as T-01..T-10.
NEW_TICKET = """
Customer bought NovaDesk annual plan 30 days ago.
They want a full cash refund to their credit card now.
Please triage this ticket.
"""


def open_vector_store():
    """Open the Chroma folder we built in Step 4 (do not rebuild)."""
    if not CHROMA_DIR.exists():
        raise FileNotFoundError(
            f"No Chroma DB at {CHROMA_DIR}. Run step4_embed.py first."
        )

    embeddings = build_embeddings()
    return Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
    )


def retrieve_chunks(store, query: str, k: int = TOP_K):
    """
    Embed the query and return the k most similar chunks.

    similarity_search_with_score gives (Document, distance).
    Lower distance => closer match for this store setup.
    """
    return store.similarity_search_with_score(query, k=k)


def main():
    store = open_vector_store()
    results = retrieve_chunks(store, NEW_TICKET, k=TOP_K)

    print("NEW TICKET (query)")
    print("-" * 60)
    print(NEW_TICKET.strip())
    print()
    print(f"Top {TOP_K} retrieved chunks:\n")

    for i, (doc, score) in enumerate(results, start=1):
        source = doc.metadata.get("source", "unknown")
        short_name = Path(source).name
        print("=" * 60)
        print(f"Rank {i}")
        print(f"Source: {short_name}")
        print(f"Distance score: {score:.4f}  (lower = closer)")
        print("-" * 60)
        print(doc.page_content)
        print()


if __name__ == "__main__":
    main()
