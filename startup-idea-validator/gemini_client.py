import os
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv(override=True)

GEMINI_MODEL = "gemini-3.6-flash"
FALLBACK_MODELS = (
    "gemini-3.6-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
)
MAX_ATTEMPTS_PER_MODEL = 3


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from the .env file.")
    return genai.Client(api_key=api_key)


def _error_text(exc):
    return str(exc)


def _is_quota_error(exc):
    text = _error_text(exc)
    return "429" in text or "RESOURCE_EXHAUSTED" in text or "quota" in text.lower()


def _is_overload_error(exc):
    text = _error_text(exc)
    return (
        "503" in text
        or "UNAVAILABLE" in text
        or "high demand" in text.lower()
    )


def _is_missing_model(exc):
    text = _error_text(exc)
    return (
        "404" in text
        or "NOT_FOUND" in text
        or "no longer available" in text.lower()
    )


def _is_daily_model_quota(exc):
    text = _error_text(exc)
    return "PerDay" in text or "generate_content_free_tier_requests" in text


def _retry_seconds(exc, attempt):
    match = re.search(r"retry in ([0-9.]+)s", _error_text(exc), re.IGNORECASE)
    if match:
        return min(int(float(match.group(1))) + 1, 30)
    if _is_overload_error(exc):
        return min(8 * attempt, 24)
    return min(4 * attempt, 12)


def generate_text(prompt, system_instruction=None):
    config_kwargs = {
        "automatic_function_calling": types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    }
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction

    last_error = None
    for model_name in FALLBACK_MODELS:
        for attempt in range(1, MAX_ATTEMPTS_PER_MODEL + 1):
            try:
                client = get_client()
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(**config_kwargs),
                )
                return response.text
            except (errors.ClientError, errors.ServerError, errors.APIError) as exc:
                last_error = exc
                if _is_missing_model(exc) or _is_daily_model_quota(exc):
                    break
                if _is_overload_error(exc) or _is_quota_error(exc):
                    if attempt < MAX_ATTEMPTS_PER_MODEL:
                        time.sleep(_retry_seconds(exc, attempt))
                        continue
                    break
                raise

    raise last_error
