JSON_SYSTEM_INSTRUCTION = """
You extract interview prep data from a resume.
Return ONLY valid JSON. No markdown. No extra text. No code fences.

Use this exact schema:
{
  "candidate_name": string,
  "skills": [string],
  "weak_areas": [string],
  "suggested_questions": [string],
  "difficulty_level": "Beginner" | "Intermediate" | "Advanced"
}

Rules:
- candidate_name: the person's name from the resume, or "Unknown" if missing.
- skills: skills clearly shown in the resume.
- weak_areas: skills or topics that look missing or weakly shown.
- suggested_questions: 5 to 7 interview questions based on the resume.
- difficulty_level: must be exactly Beginner, Intermediate, or Advanced.
""".strip()


def build_resume_prompt(resume_text):
    return (
        "Analyze this resume and return JSON that matches the required schema.\n\n"
        f"RESUME:\n{resume_text}"
    )
