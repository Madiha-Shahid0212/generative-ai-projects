"""
Step 6 — Generate with Qwen (OpenRouter), using retrieved chunks only.

Flow: new ticket -> retrieve top-k chunks -> send ONLY those chunks + ticket to Qwen.
Qwen must return structured JSON and quote only from retrieved text.
"""

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from step5_retrieve import NEW_TICKET, TOP_K, open_vector_store, retrieve_chunks


# Load .env from this project folder (OPENROUTER_API_KEY, OPENROUTER_MODEL).
load_dotenv(Path(__file__).resolve().parent / ".env")


class TriageResult(BaseModel):
    """Shape of the answer we want from Qwen."""

    category: str = Field(description="One short category, e.g. billing, access, bug")
    priority: str = Field(description="Low, Medium, High, or Critical")
    similar_ticket_ids: list[str] = Field(
        description="Ticket ids found in retrieved text, e.g. T-07"
    )
    draft_reply: str = Field(description="Short reply an agent could send")
    quotes: list[str] = Field(
        description="Short quotes copied from the retrieved chunks only"
    )
    notes: str = Field(
        description="Any conflict or policy warning grounded in the chunks"
    )


SYSTEM_RULES = """
You are a support ticket triage helper for NovaDesk.
Use ONLY the retrieved chunks below. Do not invent policy or ticket facts.
If something is missing from the chunks, say it is not in the retrieved text.
Prefer policy rules over a bad agent promise when they conflict.

You must reply with a single JSON object (and only JSON) with these keys:
category, priority, similar_ticket_ids, draft_reply, quotes, notes.
"""


def build_qwen():
    """OpenRouter is OpenAI-compatible, so we use ChatOpenAI with a custom base URL."""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    # OpenRouter deprecated qwen/qwen3.6-plus:free — use qwen/qwen3.6-plus.
    model = os.getenv("OPENROUTER_MODEL", "qwen/qwen3.6-plus").strip()

    if not api_key or api_key == "your_openrouter_api_key_here":
        raise SystemExit(
            "OPENROUTER_API_KEY is missing.\n"
            "Open the .env file and paste your key yourself. "
            "Do not paste the key into chat."
        )

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
        # Enough room for a short JSON answer; keep low for small credit balances.
        max_tokens=1500,
        # Turn off long "thinking" so tokens are used for the JSON answer.
        extra_body={"reasoning": {"effort": "none"}},
    )


def format_chunks_for_prompt(results):
    """Turn retrieved (doc, score) pairs into plain text for the prompt."""
    blocks = []
    for i, (doc, score) in enumerate(results, start=1):
        source = Path(doc.metadata.get("source", "unknown")).name
        blocks.append(
            f"[Chunk {i} | source={source} | distance={score:.4f}]\n{doc.page_content}"
        )
    return "\n\n".join(blocks)


def parse_json_from_text(text: str) -> dict:
    """Pull a JSON object from the model reply (allows optional markdown fences)."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def triage_ticket(new_ticket: str) -> tuple[TriageResult, list]:
    """Retrieve first, then ask Qwen with question + chunks only.

    Returns (structured result, retrieved chunk pairs) so a UI can show sources.
    """
    store = open_vector_store()
    results = retrieve_chunks(store, new_ticket, k=TOP_K)
    context = format_chunks_for_prompt(results)

    user_prompt = f"""NEW SUPPORT TICKET:
{new_ticket.strip()}

RETRIEVED CHUNKS (only source of truth):
{context}

Return JSON only. Quotes must be copied from the retrieved chunks.
"""

    llm = build_qwen()
    raw = llm.invoke(
        [
            {"role": "system", "content": SYSTEM_RULES},
            {"role": "user", "content": user_prompt},
        ]
    )
    data = parse_json_from_text(raw.content)
    return TriageResult.model_validate(data), results


def main():
    print("Running retrieve + Qwen triage...\n")
    result, _chunks = triage_ticket(NEW_TICKET)

    print("STRUCTURED OUTPUT")
    print("=" * 60)
    print(f"Category: {result.category}")
    print(f"Priority: {result.priority}")
    print(f"Similar ticket ids: {', '.join(result.similar_ticket_ids) or '(none)'}")
    print()
    print("Draft reply:")
    print(result.draft_reply)
    print()
    print("Quotes from retrieved text:")
    for q in result.quotes:
        print(f'  - "{q}"')
    print()
    print("Notes:")
    print(result.notes)


if __name__ == "__main__":
    main()
