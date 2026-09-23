"""
Step 4 — Embed chunks with Hugging Face, store in Chroma.

Embeddings turn text into a list of numbers (a vector).
Similar meaning => similar numbers. That is how search finds related chunks later.
We do NOT call Qwen here. Embeddings only.
"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from step3_chunk import chunk_documents
from step2_load import load_all_documents


# Small, fast sentence-transformers model. Output size is 384 numbers.
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# Local folder where Chroma saves the vectors on disk.
CHROMA_DIR = Path(__file__).resolve().parent / "chroma_db"


def build_embeddings():
    """Create the Hugging Face embedding model (runs on your PC)."""
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL)


def build_vector_store(chunks, embeddings):
    """
    Put every chunk into Chroma.

    Chroma keeps: the chunk text + its vector + metadata (like source path).
    We delete any old DB folder content by rebuilding fresh each Step 4 run.
    """
    if CHROMA_DIR.exists():
        # Fresh rebuild so repeated runs do not duplicate the same chunks.
        import shutil

        shutil.rmtree(CHROMA_DIR)

    store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    return store


def main():
    docs = load_all_documents()
    chunks = chunk_documents(docs)
    embeddings = build_embeddings()

    # Embed ONE short string first so we can print the vector length clearly.
    sample_vector = embeddings.embed_query("password reset email")
    print(f"Embedding model: {EMBED_MODEL}")
    print(f"Vector length (dimensions): {len(sample_vector)}")
    print(f"First 5 numbers: {sample_vector[:5]}")
    print()

    store = build_vector_store(chunks, embeddings)
    count = store._collection.count()
    print(f"Chunks embedded and stored in Chroma: {count}")
    print(f"Saved under: {CHROMA_DIR}")


if __name__ == "__main__":
    main()
