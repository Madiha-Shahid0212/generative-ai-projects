"""Gemini client. Embeddings turn text into vectors. Search is not done here."""

import os

from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(Path(__file__).resolve().parent / ".env")

EMBED_MODEL = "gemini-embedding-001"
GEMINI_MODEL = "gemini-3.6-flash"


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from the .env file.")
    return genai.Client(api_key=api_key)


def embed_texts(texts, task_type="RETRIEVAL_DOCUMENT"):
    """Return a list of float lists, one vector per string."""
    client = get_client()
    vectors = []
    for text in texts:
        response = client.models.embed_content(
            model=EMBED_MODEL,
            contents=text,
            config=types.EmbedContentConfig(task_type=task_type),
        )
        vectors.append(list(response.embeddings[0].values))
    return vectors


def generate_text(prompt, system_instruction=None):
    """Write an answer. This does not search documents."""
    client = get_client()
    config_kwargs = {
        "automatic_function_calling": types.AutomaticFunctionCallingConfig(
            disable=True
        ),
        "response_mime_type": "application/json",
    }
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(**config_kwargs),
    )
    return response.text
