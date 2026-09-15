"""Extract text from a PDF, page by page. This is not search and not RAG."""

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

SAMPLE_DIR = Path(__file__).resolve().parent / "sample_docs"
PROMISE_PDF = SAMPLE_DIR / "promise_brochure.pdf"
FINE_PRINT_PDF = SAMPLE_DIR / "fine_print_terms.pdf"


def extract_pages(pdf_source, source_name=None):
    """Return a list of dicts: source, page (1-based), text."""
    if isinstance(pdf_source, (str, Path)):
        path = Path(pdf_source)
        reader = PdfReader(str(path))
        name = source_name or path.name
    else:
        data = pdf_source.read()
        if hasattr(pdf_source, "seek"):
            pdf_source.seek(0)
        reader = PdfReader(BytesIO(data))
        name = Path(source_name or getattr(pdf_source, "name", "upload.pdf")).name

    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(
            {
                "source": name,
                "page": i,
                "text": text.strip(),
            }
        )
    return pages


def print_pages(pages, label):
    print("=" * 60)
    print(label)
    print("=" * 60)
    for page in pages:
        print(f"\n--- {page['source']} | page {page['page']} ---\n")
        print(page["text"] if page["text"] else "(no text found on this page)")
        print()


if __name__ == "__main__":
    promise_pages = extract_pages(PROMISE_PDF)
    fine_print_pages = extract_pages(FINE_PRINT_PDF)
    print_pages(promise_pages, "PROMISE (brochure / ads)")
    print_pages(fine_print_pages, "FINE PRINT (contract / handbook)")
    print("Done. This was only extraction. No chunking, no search yet.")
