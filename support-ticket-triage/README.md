# Support Ticket Triage Desk

A real **RAG** (Retrieval-Augmented Generation) app for support ticket triage.

You paste a **new** support ticket. The app:

1. Searches similar **old tickets** and **product policy** chunks
2. Sends **only those chunks** (plus the new ticket) to **Qwen** via OpenRouter
3. Returns: category, priority, similar ticket ids, a short draft reply, and quotes from the retrieved text

It does **not** dump every ticket and policy into the model. That would be a long prompt, not RAG.

## Why this is RAG

**RAG** means: **search first, then generate**.

| Step | What happens here |
| --- | --- |
| Chunk | Tickets and policies are split into small pieces |
| Embed | Each piece becomes a vector (list of numbers for meaning) |
| Retrieve | The new ticket is embedded; Chroma returns the closest chunks |
| Generate | Qwen writes the triage from **those chunks only** |

This would **not** be RAG if we pasted all 10 tickets and 3 policies into one prompt every time.

## Why LangChain / Hugging Face / Qwen

| Piece | Role in this project |
| --- | --- |
| **LangChain** | Loaders, text splitters, Chroma wiring, and the OpenAI-compatible chat client path |
| **Hugging Face sentence-transformers** | **Embeddings only** (`all-MiniLM-L6-v2`). Turns text into vectors. Does **not** write the final reply |
| **Qwen via OpenRouter** | The **generator**. Reads the new ticket + retrieved chunks and returns structured triage JSON |
| **Chroma** | Local vector store for the embedded chunks |

Gemini is **not** used in this project.

## Fake data (invented for testing)

All content under `data/` is original fake **NovaDesk** support material (not real company tickets).

- `data/tickets/` — 10 past tickets (`T-01` … `T-10`)
- `data/policies/` — 3 short policies (refund, access/SLA, data export)

**Built-in conflict for demos:** ticket `T-07` has an agent promising a cash refund after 28 days, while the refund policy allows cash refunds only within **14 days**.

## Tech stack

| Piece | Tool |
| --- | --- |
| UI | Streamlit |
| Orchestration | LangChain |
| Embeddings | Hugging Face `sentence-transformers/all-MiniLM-L6-v2` |
| Vector store | Chroma (`chroma_db/`) |
| LLM | Qwen on OpenRouter (`OPENROUTER_MODEL`) |
| Secrets | `.env` (`OPENROUTER_API_KEY`, `OPENROUTER_MODEL`) |

## Project layout

```
support-ticket-triage/
  app.py                 # Streamlit UI (demo samples + triage)
  step2_load.py          # LangChain loaders → print raw docs
  step3_chunk.py         # Chunk documents → print chunks
  step4_embed.py         # Embed + save Chroma store
  step5_retrieve.py      # Retrieve top-k only (no Qwen)
  step6_generate.py      # Retrieve + Qwen structured triage
  data/
    tickets/             # Fake past tickets
    policies/            # Fake product policies
  requirements.txt
  .env.example
  .gitignore
```

`.env`, `.venv/`, and `chroma_db/` are gitignored. Do not commit your API key.

## Setup (Windows PowerShell)

You need Python 3.12+ and an [OpenRouter](https://openrouter.ai/) API key.

```powershell
cd C:\Users\TNC\Documents\GitHub\generative-ai-projects\support-ticket-triage
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` (or edit the existing `.env`) and set:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=qwen/qwen3.6-plus
```

Paste the real key into `.env` yourself. Do not paste it into chat or commit it.

> Note: OpenRouter deprecated `qwen/qwen3.6-plus:free`. This project uses `qwen/qwen3.6-plus`. The generate step turns off long “thinking” (`reasoning.effort = none`) so tokens go to the JSON answer.

## Build the vector store (once)

Before the UI or Step 5/6, build embeddings:

```powershell
.\.venv\Scripts\python.exe step4_embed.py
```

You should see vector length **384** and **44** chunks stored under `chroma_db/`.

## Run the app

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

1. Pick a **demo sample** (or paste your own ticket)
2. Click **Load selected sample** if you changed the dropdown
3. Click **Triage ticket**
4. Open **Retrieved chunks (evidence)** to see the RAG shortlist

## Practice the pipeline in the terminal

Each script is one learning step:

```powershell
.\.venv\Scripts\python.exe step2_load.py
.\.venv\Scripts\python.exe step3_chunk.py
.\.venv\Scripts\python.exe step4_embed.py
.\.venv\Scripts\python.exe step5_retrieve.py
.\.venv\Scripts\python.exe step6_generate.py
```

| Script | What you should see |
| --- | --- |
| `step2_load.py` | 13 documents (10 tickets + 3 policies), raw text |
| `step3_chunk.py` | Many smaller chunks with source file names |
| `step4_embed.py` | Vector length 384; chunks saved in Chroma |
| `step5_retrieve.py` | Top-k chunks + sources for a sample new ticket (no Qwen) |
| `step6_generate.py` | Structured triage: category, priority, ids, reply, quotes |

## Example demo inputs

Strong LinkedIn / portfolio cases:

- Late cash refund after 30 days → expect policy quotes + similar `T-07`
- Missing password-reset email → expect access tickets / SLA policy
- Full product outage → expect Critical-style guidance + `T-08`

More samples are built into the Streamlit dropdown.

## License

Use and share as part of this portfolio repository.
