# Resume to Interview Questions Generator

Paste a resume as plain text. Gemini returns a structured JSON analysis, and the app shows it in a dark neon UI: candidate name, skills, weak areas, interview questions, and difficulty.

This is a **prompting + structured JSON output** project (not RAG). The full resume is sent to the model. There is no document search or vector store.

## Features

- Paste resume text (no file upload required)
- **Try Example Resume** fills a sample CV
- **Generate** calls Gemini and stores a validated JSON result
- Pretty result card: skill tags, weak-area box, numbered questions, difficulty badge
- **Gemini JSON** shows the same result as formatted JSON and scrolls to it
- Loading spinner and clear error messages if the reply is empty, invalid, or the API fails

## JSON schema

Gemini is instructed to return only this shape:

```json
{
  "candidate_name": "string",
  "skills": ["string"],
  "weak_areas": ["string"],
  "suggested_questions": ["string"],
  "difficulty_level": "Beginner"
}
```

`difficulty_level` must be `Beginner`, `Intermediate`, or `Advanced`. `suggested_questions` must contain 5–7 items. Invalid replies are rejected in `json_parser.py`.

## Tech stack

| Piece | Tool |
| --- | --- |
| UI | Streamlit |
| Model | Google Gemini (`gemini-3.6-flash`) |
| Secrets | `python-dotenv` (`.env`) |

## Project layout

```
resume-interview-generator/
  app.py              # Streamlit UI and generate flow
  theme.py            # Dark neon CSS and result card
  prompts.py          # JSON schema instructions
  gemini_client.py    # Gemini API client
  json_parser.py      # Parse and validate JSON
  sample_resume.py    # Example resume for Try Example
  requirements.txt
  .env                # GEMINI_API_KEY (not committed)
  .gitignore
```

## Prerequisites

- Python 3.12+ (developed with Python 3.14)
- A [Google AI Studio](https://aistudio.google.com/) API key

## Setup

From the `resume-interview-generator` folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file next to `requirements.txt`:

```
GEMINI_API_KEY=your_key_here
```

Do not commit `.env`. It is listed in `.gitignore`.

## Run locally

```powershell
.\.venv\Scripts\streamlit.exe run app.py --server.port 8502
```

Open [http://localhost:8502](http://localhost:8502).

## How it works

1. The user pastes a resume (or loads the sample).
2. `prompts.py` builds a strict “JSON only” instruction plus the resume text.
3. `gemini_client.py` calls Gemini with JSON response mode.
4. `json_parser.py` checks that the reply is valid JSON and matches the schema.
5. `app.py` keeps the result in Streamlit session state and renders the card (and optional JSON view).

## License

Use and share as part of this portfolio repository.
