"""Generate Madiha M. Shahid's resume in the original simple template."""

from pathlib import Path

from reportlab.lib.colors import black, HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

OUT = Path(__file__).with_name("Madiha_Shahid_Resume.pdf")

W, H = letter
LEFT = 0.55 * inch
RIGHT = W - 0.55 * inch
TOP = H - 0.42 * inch
MAX_W = RIGHT - LEFT
GRAY = HexColor("#333333")

LINKEDIN = "https://www.linkedin.com/in/madiha-shahid-a64091308/"
GITHUB = "https://github.com/Madiha-Shahid0212"
EMAIL = "madihashahid212@gmail.com"

NAME = "Times-Bold"
BODY = "Times-Roman"
ITAL = "Times-Italic"


def wrap(text, max_width, font, size):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if pdfmetrics.stringWidth(trial, font, size) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def section(c, y, title):
    c.setFillColor(black)
    c.setFont(NAME, 10.5)
    c.drawString(LEFT, y, title.upper())
    y -= 3.5
    c.setStrokeColor(black)
    c.setLineWidth(0.7)
    c.line(LEFT, y, RIGHT, y)
    return y - 9


def play_bullet(c, x, y):
    """Original resume used a right-pointing triangle (▸)."""
    p = c.beginPath()
    p.moveTo(x, y - 0.4)
    p.lineTo(x + 4.2, y + 2.2)
    p.lineTo(x, y + 4.8)
    p.close()
    c.setFillColor(black)
    c.drawPath(p, fill=1, stroke=0)


def bullets(c, y, items, size=9.15, leading=10.7):
    text_w = MAX_W - 16
    for item in items:
        lines = wrap(item, text_w, BODY, size)
        play_bullet(c, LEFT + 2, y)
        c.setFillColor(black)
        c.setFont(BODY, size)
        for i, line in enumerate(lines):
            c.drawString(LEFT + 14, y, line)
            y -= leading
    return y - 1


def para(c, y, text, size=9.15, leading=10.7):
    c.setFillColor(black)
    c.setFont(BODY, size)
    for line in wrap(text, MAX_W, BODY, size):
        c.drawString(LEFT, y, line)
        y -= leading
    return y


def labeled(c, y, label, value, size=9.15, leading=10.7):
    c.setFont(NAME, size)
    c.setFillColor(black)
    c.drawString(LEFT, y, label)
    label_w = pdfmetrics.stringWidth(label + " ", NAME, size)
    c.setFont(BODY, size)
    first = True
    remain = MAX_W - label_w
    for line in wrap(value, remain if first else MAX_W, BODY, size):
        c.drawString(LEFT + label_w if first else LEFT, y, line)
        first = False
        y -= leading
    return y


def job_header(c, y, role_company, dates):
    c.setFont(NAME, 10)
    c.setFillColor(black)
    c.drawString(LEFT, y, role_company)
    c.setFont(BODY, 10)
    c.drawRightString(RIGHT, y, dates)
    return y - 11.2


def location_line(c, y, place):
    c.setFont(ITAL, 9.2)
    c.setFillColor(GRAY)
    c.drawString(LEFT, y, place)
    return y - 11.2


def project_header(c, y, name, stack):
    c.setFont(NAME, 10)
    c.setFillColor(black)
    c.drawString(LEFT, y, name)
    name_w = pdfmetrics.stringWidth(name + "  ", NAME, 10)
    c.setFont(BODY, 9.2)
    c.setFillColor(GRAY)
    c.drawString(LEFT + name_w, y, stack)
    return y - 11.2


def main():
    c = canvas.Canvas(str(OUT), pagesize=letter)
    c.setTitle("Madiha M. Shahid")
    c.setAuthor("Madiha M. Shahid")
    y = TOP

    c.setFillColor(black)
    c.setFont(NAME, 17)
    c.drawCentredString(W / 2, y, "Madiha M. Shahid")
    y -= 15
    c.setFont(BODY, 11)
    c.drawCentredString(W / 2, y, "AI/ML Engineer")
    y -= 13

    c.setFont(BODY, 9.5)
    parts = [
        ("Karachi, Pakistan", None),
        (EMAIL, f"mailto:{EMAIL}"),
        ("+92 321 8997716", f"tel:+923218997716"),
        ("LinkedIn", LINKEDIN),
        ("GitHub", GITHUB),
    ]
    gap = "  ·  "
    full = gap.join(p[0] for p in parts)
    x = (W - pdfmetrics.stringWidth(full, BODY, 9.5)) / 2
    for i, (text, url) in enumerate(parts):
        width = pdfmetrics.stringWidth(text, BODY, 9.5)
        c.setFillColor(black)
        c.drawString(x, y, text)
        if url:
            c.linkURL(url, (x, y - 2, x + width, y + 10), relative=0)
        x += width
        if i < len(parts) - 1:
            gw = pdfmetrics.stringWidth(gap, BODY, 9.5)
            c.drawString(x, y, gap)
            x += gw

    y -= 16
    y = section(c, y, "Professional Summary")
    y = para(
        c,
        y,
        "Final-year BS Computer Science student (KIET, CGPA 3.6/4.0) with 6+ months shipping AI/ML "
        "systems. Builds Generative AI apps around LLMs: prompt engineering, system/role prompts, "
        "Chain-of-Thought, structured JSON output, and output validation (Gemini, Vertex AI). Trains "
        "classical ML models and ships them in React, Django, and Streamlit. Expanding into RAG, "
        "embeddings, LangChain, and Hugging Face Transformers. Seeking intern or junior Generative AI / AI/ML roles.",
    )
    y -= 5

    y = section(c, y, "Education")
    y = job_header(
        c, y, "BS Computer Science — KIET University, Karachi  |  CGPA 3.6 / 4.0", "Expected 2027"
    )
    y = job_header(
        c, y, "Intermediate (Computer Science) — NCR CET College, Karachi", "2021 – 2022"
    )
    y = job_header(c, y, "Matriculation — The Educators, Karachi", "2020")
    y -= 4

    y = section(c, y, "Technical Skills")
    y = labeled(
        c,
        y,
        "Generative AI concepts:",
        "LLMs, Prompt Engineering, System / Role Prompts, Chain-of-Thought (CoT), Structured Output "
        "(JSON), Output Validation, RAG, Embeddings, LangChain, Hugging Face Transformers, "
        "Google Gemini API, Vertex AI",
    )
    y = labeled(
        c,
        y,
        "AI / Machine Learning:",
        "scikit-learn, PyTorch, Pandas, NumPy, Matplotlib, OpenCV, Computer Vision, NLP, "
        "Feature Engineering, Model Evaluation",
    )
    y = labeled(c, y, "Programming Languages:", "Python, JavaScript, Java, C#")
    y = labeled(
        c, y, "Web Development:", "React.js, Django, Node.js, Streamlit, REST APIs, HTML, CSS"
    )
    y = labeled(c, y, "Databases:", "MySQL, Microsoft SQL Server")
    y = labeled(
        c,
        y,
        "Developer Tools:",
        "Git, GitHub, Docker, Jupyter Notebook, VS Code, Postman, Android Studio",
    )
    y -= 4

    y = section(c, y, "Work Experience")
    y = job_header(c, y, "Junior AI/ML Developer · Swag Kicks", "Jan 2026 – Apr 2026")
    y = location_line(c, y, "Karachi, Pakistan")
    y = bullets(
        c,
        y,
        [
            "Owned the production Vertex AI chatbot: designed conversation flow, connected the LLM, and ran end-to-end tests before release.",
            "Trained and scored Vertex AI models, then retuned prompts and model settings from quality metrics until the bot was stable enough to deploy.",
            "Labeled computer-vision data with bounding boxes and led pre-launch QA: logged failure cases, fixed them, and signed off production readiness.",
        ],
    )
    y -= 1.5
    y = job_header(c, y, "AI/ML Intern · Swag Kicks", "Nov 2025 – Dec 2025")
    y = location_line(c, y, "Karachi, Pakistan")
    y = bullets(
        c,
        y,
        [
            "Built classification models in scikit-learn from raw tables: cleaning, feature extraction, train/test splits, and accuracy benchmarking.",
            "Wired model predictions into the product through React.js and Node.js REST APIs so the UI could show live ML results.",
        ],
    )
    y -= 1.5
    y = job_header(c, y, "Machine Learning Intern · Elevvo", "Sep 2025")
    y = location_line(c, y, "Remote")
    y = bullets(
        c,
        y,
        [
            "Ran the full ML loop on real datasets — EDA, cleaning, training, and hyperparameter tuning — to raise benchmark scores.",
            "Wrote reusable preprocessing pipelines for missing values, outliers, and categorical encoding so training data stayed consistent.",
        ],
    )
    y -= 3

    y = section(c, y, "Projects")
    y = project_header(
        c, y, "Explain Like I'm a Bot", "React.js · Django · Gemini · Prompt Engineering"
    )
    y = bullets(
        c,
        y,
        [
            "Full-stack LLM app: pick a persona and topic; Gemini explains it; the browser reads it aloud (Intern, Professor, Journalist, Executive).",
            "System / role prompts: each persona has its own instruction (tone, length, no markdown) so one model speaks in four consistent voices.",
        ],
    )
    y = project_header(
        c,
        y,
        "Resume to Interview Questions Generator",
        "Streamlit · Gemini · Structured Output",
    )
    y = bullets(
        c,
        y,
        [
            "Gemini reads a resume and must return JSON only: name, skills, weak areas, 5–7 interview questions, and difficulty level.",
            "Structured output + validation: JSON-mode prompting plus a schema parser that drops hallucinated or broken replies before the UI.",
        ],
    )
    y = project_header(
        c, y, "Chain-of-Thought + Persona Reasoning", "Streamlit · Gemini · CoT Prompting"
    )
    y = bullets(
        c,
        y,
        [
            "Same problem, two Gemini calls: a short direct answer vs. a persona (e.g. Sherlock Holmes) that must reason step by step (Chain-of-Thought + role prompting) so both can be compared.",
        ],
    )
    y = project_header(
        c, y, "Jarvis – AI Voice Assistant", "Python · SpeechRecognition · pyttsx3 · REST APIs"
    )
    y = bullets(
        c,
        y,
        [
            "Voice in → speech-to-text → NLP intent parse → tool call (weather/news REST APIs) → spoken reply; classmates used it as a daily assistant.",
        ],
    )
    y = project_header(
        c, y, "Face Recognition Attendance System", "Android Studio · FaceNet · ML Kit · Java"
    )
    y = bullets(
        c,
        y,
        [
            "On-device attendance: ML Kit detects the face, FaceNet embeddings identify the student, blink check reduces spoofing; stays reliable in mixed lighting.",
        ],
    )
    y = project_header(
        c, y, "Loan Approval Prediction System", "Python · scikit-learn · Pandas · NumPy"
    )
    y = bullets(
        c,
        y,
        [
            "Compared Logistic Regression, Decision Tree, and Random Forest with k-fold CV; RF won. Pipeline handles imputation and feature engineering end-to-end.",
        ],
    )
    y -= 3

    y = section(c, y, "Certifications")
    y = bullets(
        c,
        y,
        [
            "Google Cloud / Coursera — Introduction to AI and Machine Learning (Sep 2025)",
            "Simplilearn SkillUp — Deep Learning for Beginners (Jul 2026)",
            "Deloitte / Forage — Data Analytics Job Simulation (Jun 2026)",
            "HackerRank — Python (Basic) (Aug 2025)",
        ],
    )

    print(f"final y={y:.1f}")
    if y < 36:
        print("WARNING: content may overflow the page")
    c.save()
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
