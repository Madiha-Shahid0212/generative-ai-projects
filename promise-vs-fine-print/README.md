# Promise vs Fine Print

A small RAG app. You give it two PDFs: a **Promise** (brochure / ads) and **Fine print** (contract / handbook). You ask a question such as “Is a laptop included?”

The app does **not** send the whole PDFs to Gemini. It splits text into chunks, searches for the closest chunks from **both** sources, then asks Gemini to write:

- a Promise quote
- a Fine-print quote
- a verdict: **Match**, **Conflict**, or **Missing**
- which chunk was used (file + page)

## Why this is RAG

**RAG** means Retrieval-Augmented Generation: **search first, then generate**.

This project is RAG because:

1. PDFs are split into chunks.
2. Each chunk is turned into a vector (a list of numbers for meaning).
3. The question becomes a vector too. Numpy picks the top matching chunks from Promise and from Fine print (cosine similarity).
4. Gemini sees **only those chunks** plus the question. It does not search. It only writes the quotes and verdict.

This would **not** be RAG if we pasted both full PDFs into the prompt. That is a long-context dump. There is no search over chunks.

Gemini is used in two narrow ways:

- **Embeddings:** turn text into vectors (not “reading the contract”).
- **Generate:** write the grounded answer from retrieved text.

The search step is Python + numpy, not the chat model.

## Sample documents

Original dummy PDFs (not a real company’s papers):

- `sample_docs/promise_brochure.pdf` — says a laptop is included, and a 30-day refund
- `sample_docs/fine_print_terms.pdf` — says hardware is sold separately, and refunds are 7 days only

They **agree** on Friday live Q and A. Rebuild them with:

```powershell
python sample_docs\make_sample_pdfs.py
```

Try these questions:

- `Is a laptop included?` → Conflict
- `Is there a 30-day refund?` → Conflict
- `Is there live Q and A on Friday?` → Match

## Tech stack

| Piece | Tool |
| --- | --- |
| UI | Streamlit |
| PDF text | pypdf |
| Vectors + search | numpy (cosine similarity) |
| Embeddings + answer | Google Gemini |
| Secrets | `.env` (`GEMINI_API_KEY`) |

## Project layout

```
promise-vs-fine-print/
  app.py                 # Streamlit UI
  extract_text.py        # PDF → page text
  chunk_text.py          # pages → overlapping chunks
  embed_store.py         # chunks → numpy vectors
  retrieve.py            # question → top chunks per source
  generate_answer.py     # retrieved chunks → quotes + verdict
  gemini_client.py       # embed + generate
  theme.py
  sample_docs/
  requirements.txt
  .env.example
```

`.env` and `.venv/` are gitignored. Do not commit your API key.

## Setup

You need Python 3.12+ and a [Google AI Studio](https://aistudio.google.com/) API key.

```powershell
cd C:\Users\Administrator\Documents\GitHub\generative-ai-projects\promise-vs-fine-print
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and put your key in:

```
GEMINI_API_KEY=your_key_here
```

## Run the app

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

Upload two PDFs, or tick **Use the sample Harbor Study Pack PDFs**. Type a question. Click **Compare**.

The expander **Chunks sent to Gemini** shows the retrieved text only.

## Practice the pipeline in the terminal

```powershell
python extract_text.py
python chunk_text.py
python embed_store.py
python retrieve.py "Is a laptop included?"
python generate_answer.py "Is a laptop included?"
```

Each script is one step: extract, chunk, embed, retrieve, generate.

## License

Use and share as part of this portfolio repository.
