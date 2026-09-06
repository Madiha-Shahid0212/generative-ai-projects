# Explain Like I'm a...

A small full-stack app that explains any topic in a chosen professional voice.

Pick a persona, type a topic, and Gemini returns a short English explanation. The browser can also read it aloud with a slightly different speaking style for each persona.

Built as a portfolio project: **React** frontend, **Django** backend, **Gemini API**, and the **Web Speech API**.

## Features

- Explain a topic as an **Intern**, **Professor**, **Journalist**, or **Executive**
- English-only, plain-paragraph answers (no markdown clutter)
- Spoken playback with Play / Stop
- Local CORS setup so the Vite app can call Django during development

## Tech stack

| Layer | Tools |
| --- | --- |
| Frontend | React 19, Vite |
| Backend | Django 6 |
| Model | Google Gemini (`gemini-3.6-flash`) |
| Voice | Web Speech API (`speechSynthesis`) |

## Project layout

```
explain-like-im-a-bot/
  .env                 # GEMINI_API_KEY (not committed)
  requirements.txt
  backend/
    manage.py
    config/            # Django settings and root URLs
    explain/           # API app (views, personas)
  frontend/
    src/               # React UI
```

## Prerequisites

- Python 3.12+ (this project was developed with Python 3.14)
- Node.js 18+
- A [Google AI Studio](https://aistudio.google.com/) API key

## Setup

From the `explain-like-im-a-bot` folder:

### 1. Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in `explain-like-im-a-bot/` (next to `requirements.txt`):

```
GEMINI_API_KEY=your_key_here
```

Never commit this file. It is already listed in `.gitignore`.

### 2. Frontend

```powershell
cd frontend
npm install
```

## Run locally

Use **two terminals**.

**Terminal 1 — Django** (from `explain-like-im-a-bot`):

```powershell
.\.venv\Scripts\python backend\manage.py runserver 127.0.0.1:8000
```

**Terminal 2 — React** (from `explain-like-im-a-bot/frontend`):

```powershell
npm run dev
```

Open the app at [http://localhost:5173](http://localhost:5173).

The API lives at `http://127.0.0.1:8000`. The home page of Django (`/`) has no UI on purpose — the interface is the React app.

## API

### `POST /api/explain/`

```json
{
  "topic": "photosynthesis",
  "persona": "professor"
}
```

**Personas:** `intern` · `professor` · `journalist` · `executive`

**Success:**

```json
{
  "topic": "photosynthesis",
  "persona": "professor",
  "explanation": "..."
}
```

### `GET /api/test-gemini/`

A simple hello check that Gemini and the API key are working.

## How it fits together

1. The React form sends `topic` and `persona` to Django.
2. Django builds a system prompt from `explain/personas.py` and calls Gemini.
3. The response is shown in the right-hand panel.
4. The Web Speech API reads the text, with rate and pitch tuned per persona.

## Notes

- Keep both servers running while you use the app. If Django is down, the UI cannot fetch explanations.
- Voice works best in Chrome or Edge, with system volume on.
- CORS currently allows `localhost:5173` and `localhost:3000` for local development only.
