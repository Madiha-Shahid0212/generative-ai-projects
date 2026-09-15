"""Split extracted PDF pages into overlapping text chunks. Still not RAG."""

from extract_text import FINE_PRINT_PDF, PROMISE_PDF, extract_pages

# Small chunks so laptop and refund can live in different pieces.
CHUNK_SIZE = 280
OVERLAP = 50


def split_into_chunks(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """Cut text into pieces. Overlap keeps a little context at each cut."""
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks = []
    start = 0
    length = len(cleaned)

    while start < length:
        end = min(start + chunk_size, length)
        if end < length:
            space = cleaned.rfind(" ", start, end)
            if space > start:
                end = space
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= length:
            break
        next_start = end - overlap
        if next_start <= start:
            next_start = end
        else:
            space = cleaned.find(" ", next_start, end)
            if space != -1:
                next_start = space + 1
        start = next_start

    return chunks


def pages_to_chunks(pages, source_label):
    """Each chunk keeps source + page so we can cite it later."""
    results = []
    for page in pages:
        pieces = split_into_chunks(page["text"])
        for piece in pieces:
            results.append(
                {
                    "source_label": source_label,
                    "source_file": page["source"],
                    "page": page["page"],
                    "text": piece,
                }
            )
    return results


def print_chunks(chunks, heading):
    print("=" * 60)
    print(heading)
    print(f"{len(chunks)} chunks  |  size~{CHUNK_SIZE}  overlap={OVERLAP}")
    print("=" * 60)
    for i, chunk in enumerate(chunks):
        print(
            f"\n[{heading[:1]}{i}] {chunk['source_file']} | "
            f"page {chunk['page']} | {len(chunk['text'])} chars"
        )
        print(chunk["text"])
        print()


if __name__ == "__main__":
    promise_chunks = pages_to_chunks(
        extract_pages(PROMISE_PDF),
        "promise",
    )
    fine_print_chunks = pages_to_chunks(
        extract_pages(FINE_PRINT_PDF),
        "fine_print",
    )
    print_chunks(promise_chunks, "PROMISE CHUNKS")
    print_chunks(fine_print_chunks, "FINE PRINT CHUNKS")
    print("Done. These are pieces we CAN search. We have not searched yet.")
