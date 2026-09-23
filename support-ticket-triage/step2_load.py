"""
Step 2 — Load raw text with LangChain.

A loader opens files and turns each file into a Document object.
A Document is just: page_content (the text) + metadata (extra facts like the file path).
"""

from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader


def load_all_documents():
    """Read every .txt file under data/tickets and data/policies."""
    base = Path(__file__).resolve().parent / "data"

    # DirectoryLoader walks a folder and uses TextLoader for each .txt file.
    ticket_loader = DirectoryLoader(
        str(base / "tickets"),
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    policy_loader = DirectoryLoader(
        str(base / "policies"),
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )

    # .load() returns a Python list of Document objects.
    tickets = ticket_loader.load()
    policies = policy_loader.load()
    return tickets + policies


def main():
    docs = load_all_documents()
    print(f"Loaded {len(docs)} documents\n")

    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "unknown")
        print("=" * 60)
        print(f"Document {i}")
        print(f"Source: {source}")
        print("-" * 60)
        # page_content is the raw text from the file — nothing chunked yet.
        print(doc.page_content)
        print()


if __name__ == "__main__":
    main()
