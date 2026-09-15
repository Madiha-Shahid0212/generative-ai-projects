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

    y -= 18
    y = section(c, y, "Professional Summary")
    y = para(
        c,
        y,
        "Final-year BS Computer Science student (KIET) with 6+ months of industry experience in AI/ML "
        "development, computer vision, and full-stack engineering. Experienced in building ML models, "
        "deploying AI applications using Google Vertex AI, and building Generative AI apps with LLMs, "
        "prompt engineering, Gemini API, Django, and React.js. Working with RAG, LangChain, and Hugging Face "
        "Transformers. Seeking internship or junior-level roles in AI/ML Engineering, Generative AI, or "
        "Software Development.",
    )
    y -= 6

    y = section(c, y, "Education")
    y = job_header(c, y, "BS Computer Science — KIET University, Karachi", "Expected 2027")
    c.setFont(BODY, 9.2)
    c.setFillColor(black)
    c.drawString(LEFT, y, "CGPA: 3.6 / 4.0")
    y -= 11.2
    y = job_header(
        c, y, "Intermediate (Computer Science) — NCR CET College, Karachi", "2021 – 2022"
    )
    y = job_header(c, y, "Matriculation — The Educators, Karachi", "2020")
    y -= 5

    y = section(c, y, "Technical Skills")
    y = labeled(
        c,
        y,
        "Generative AI:",
        "LLMs, Prompt Engineering, RAG, LangChain, Hugging Face Transformers, Google Gemini API, "
        "Vertex AI, Chain-of-Thought, Structured JSON Output, Embeddings",
    )
    y = labeled(
        c,
        y,
        "AI / Machine Learning:",
        "Google Vertex AI, scikit-learn, Pandas, NumPy, Matplotlib, OpenCV, Computer Vision, NLP, "
        "Model Evaluation, Feature Engineering, PyTorch",
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
    y -= 5

    y = section(c, y, "Work Experience")
    y = job_header(c, y, "Junior AI/ML Developer · Swag Kicks", "Jan 2026 – Apr 2026")
    y = location_line(c, y, "Karachi, Pakistan")
    y = bullets(
        c,
        y,
        [
            "Developed and deployed an AI-powered chatbot on Google Vertex AI, handling conversation flow design, model integration, and end-to-end testing.",
            "Trained and evaluated Vertex AI models; assessed performance metrics and iterated on configuration prior to production deployment.",
            "Created and validated bounding box annotations for computer vision datasets, ensuring labeling accuracy across training samples.",
            "Led pre-deployment model testing, identified failure cases, and coordinated fixes to ensure production readiness.",
        ],
    )
    y -= 2
    y = job_header(c, y, "AI/ML Intern · Swag Kicks", "Nov 2025 – Dec 2025")
    y = location_line(c, y, "Karachi, Pakistan")
    y = bullets(
        c,
        y,
        [
            "Trained and evaluated ML classification models using scikit-learn; performed data preprocessing, feature extraction, and benchmarking.",
            "Supported React.js and Node.js development to integrate ML model outputs into the application layer.",
        ],
    )
    y -= 2
    y = job_header(c, y, "Machine Learning Intern · Elevvo", "Sep 2025")
    y = location_line(c, y, "Remote")
    y = bullets(
        c,
        y,
        [
            "Trained and benchmarked ML models on real-world datasets; improved performance through EDA, data cleaning, and hyperparameter tuning.",
            "Built structured preprocessing pipelines handling missing values, outliers, and categorical encoding.",
        ],
    )
    y -= 5

    y = section(c, y, "Projects")
    y = project_header(
        c, y, "Explain Like I'm a Bot", "React.js · Django · Gemini API · Prompt Engineering"
    )
    y = bullets(
        c,
        y,
        [
            "Built a full-stack Generative AI app that explains any topic in a chosen persona (Intern, Professor, Journalist, Executive), with spoken playback.",
            "Designed system prompts per persona and a Django REST API consumed by a React.js frontend.",
        ],
    )
    y = project_header(
        c,
        y,
        "Resume to Interview Questions Generator",
        "Streamlit · Gemini API · Structured JSON",
    )
    y = bullets(
        c,
        y,
        [
            "Built an LLM app that turns resume text into validated JSON: skills, weak areas, interview questions, and difficulty.",
            "Used strict prompt contracts and output validation so model text becomes usable structured data.",
        ],
    )
    y = project_header(
        c, y, "Chain-of-Thought + Persona Reasoning", "Streamlit · Gemini API · Prompt Engineering"
    )
    y = bullets(
        c,
        y,
        [
            "Compared plain answers with persona-based step-by-step Chain-of-Thought reasoning on the same scenarios.",
        ],
    )
    y = project_header(
        c, y, "Jarvis – AI Voice Assistant", "Python · SpeechRecognition · pyttsx3 · gTTS · REST APIs"
    )
    y = bullets(
        c,
        y,
        [
            "Built a voice-controlled AI assistant with NLP-based intent parsing and speech recognition pipeline; adopted by classmates and received positive feedback.",
            "Integrated REST APIs for live data retrieval (weather, news) and automated task execution via natural language voice commands.",
        ],
    )
    y = project_header(
        c, y, "Face Recognition Attendance System", "Android Studio · FaceNet · ML Kit · Java"
    )
    y = bullets(
        c,
        y,
        [
            "Built an Android app automating attendance via real-time face recognition using FaceNet and Google ML Kit.",
            "Achieved reliable identification across varied lighting conditions through FaceNet embedding fine-tuning.",
        ],
    )
    y = project_header(
        c, y, "Loan Approval Prediction System", "Python · scikit-learn · Pandas · NumPy"
    )
    y = bullets(
        c,
        y,
        [
            "Built Random Forest classifier achieving highest validation accuracy across LR, Decision Tree, and RF via k-fold cross-validation.",
            "Developed end-to-end preprocessing pipeline with feature engineering and missing-value imputation using scikit-learn and Pandas.",
        ],
    )
    y -= 5

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
