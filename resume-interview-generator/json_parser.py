import json
import re

REQUIRED_KEYS = {
    "candidate_name",
    "skills",
    "weak_areas",
    "suggested_questions",
    "difficulty_level",
}

ALLOWED_DIFFICULTY = {"Beginner", "Intermediate", "Advanced"}

LIST_KEYS = ("skills", "weak_areas", "suggested_questions")

USER_PARSE_ERROR = (
    "Could not read the AI reply as valid JSON. Please try again."
)

USER_SCHEMA_ERROR = (
    "The AI reply was missing required fields or used the wrong format. "
    "Please try again."
)


class InterviewJsonError(Exception):
    """Raised when the model output cannot be used as interview JSON."""


def _strip_code_fences(text):
    stripped = text.strip()
    match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", stripped, re.DOTALL)
    if match:
        return match.group(1).strip()
    return stripped


def parse_interview_json(raw_text):
    if raw_text is None or not str(raw_text).strip():
        raise InterviewJsonError(USER_PARSE_ERROR)

    cleaned = _strip_code_fences(str(raw_text))

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise InterviewJsonError(USER_PARSE_ERROR) from exc

    if not isinstance(data, dict):
        raise InterviewJsonError(USER_SCHEMA_ERROR)

    missing = REQUIRED_KEYS - set(data)
    if missing:
        raise InterviewJsonError(USER_SCHEMA_ERROR)

    if not isinstance(data["candidate_name"], str) or not data["candidate_name"].strip():
        raise InterviewJsonError(USER_SCHEMA_ERROR)

    for key in LIST_KEYS:
        value = data[key]
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise InterviewJsonError(USER_SCHEMA_ERROR)

    question_count = len(data["suggested_questions"])
    if question_count < 5 or question_count > 7:
        raise InterviewJsonError(USER_SCHEMA_ERROR)

    if data["difficulty_level"] not in ALLOWED_DIFFICULTY:
        raise InterviewJsonError(USER_SCHEMA_ERROR)

    return data
