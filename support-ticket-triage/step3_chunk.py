"""
Step 3 — Chunk documents into smaller pieces.

Chunking cuts long text into short pieces so search can find the right paragraph,
not only the whole file.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

# Reuse the loader from Step 2 (same documents, new step).
from step2_load import load_all_documents


def chunk_documents(docs):
    """
    Split each Document into smaller Documents.

    chunk_size = max characters in one chunk
    chunk_overlap = how many characters to repeat at the border
                   so a sentence cut in half still keeps context
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=40,
        # Prefer splitting on blank lines, then newlines, then spaces.
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(docs)


def main():
    docs = load_all_documents()
    chunks = chunk_documents(docs)

    print(f"Loaded {len(docs)} documents")
    print(f"Created {len(chunks)} chunks\n")

    for i, chunk in enumerate(chunks, start=1):
        source = chunk.metadata.get("source", "unknown")
        # Keep only the file name so the print is easier to read.
        short_name = source.replace("\\", "/").split("/")[-1]
        text = chunk.page_content

        print("=" * 60)
        print(f"Chunk {i}")
        print(f"Source file: {short_name}")
        print(f"Length: {len(text)} characters")
        print("-" * 60)
        print(text)
        print()


if __name__ == "__main__":
    main()
