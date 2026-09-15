"""Generate Madiha M. Shahid's one-page AI/ML resume (ATS-friendly PDF)."""

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

OUT = Path(__file__).with_name("Madiha_Shahid_Resume.pdf")

NAVY = HexColor("#1B365D")
TEAL = HexColor("#0F6C8C")
BODY = HexColor("#222222")
MUTED = HexColor("#4A4A4A")

W, H = letter
LEFT = 0.52 * inch
RIGHT = W - 0.52 * inch
TOP = H - 0.38 * inch
MAX_W = RIGHT - LEFT

LINKEDIN = "https://www.linkedin.com/in/madiha-shahid-a64091308/"
GITHUB = "https://github.com/Madiha-Shahid0212"
EMAIL = "madihashahid212@gmail.com"
PHONE = "+923218997716"


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
    c.setFillColor(NAVY)
    c.rect(LEFT, y - 2, MAX_W, 14.2, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8.6)
    c.drawString(LEFT + 6, y + 1.8, title.upper())
    return y - 15


def bullets(c, y, items, width):
    c.setFillColor(BODY)
    size = 8.15
    for item in items:
        lines = wrap(item, width - 12, "Helvetica", size)
        c.setFont("Helvetica", size)
        c.drawString(LEFT + 4, y, "-")
        for line in lines:
            c.drawString(LEFT + 14, y, line)
            y -= 10.35
        y -= 0.4
    return y


def para(c, y, text, size=8.2, leading=10.45):
    c.setFillColor(BODY)
    c.setFont("Helvetica", size)
    for line in wrap(text, MAX_W, "Helvetica", size):
        c.drawString(LEFT, y, line)
        y -= leading
    return y


def labeled(c, y, label, value):
    c.setFont("Helvetica-Bold", 8.15)
    c.setFillColor(NAVY)
    c.drawString(LEFT, y, label)
    label_w = pdfmetrics.stringWidth(label + "  ", "Helvetica-Bold", 8.15)
    c.setFont("Helvetica", 8.15)
    c.setFillColor(BODY)
    first = True
    x = LEFT + label_w
    remain = MAX_W - label_w
    for line in wrap(value, remain if first else MAX_W, "Helvetica", 8.15):
        c.drawString(x if first else LEFT, y, line)
        first = False
        x = LEFT
        y -= 10.35
    return y - 0.6


def role_line(c, y, left, right):
    c.setFont("Helvetica-Bold", 8.55)
    c.setFillColor(NAVY)
    c.drawString(LEFT, y, left)
    c.setFont("Helvetica", 8.0)
    c.setFillColor(MUTED)
    c.drawRightString(RIGHT, y, right)
    return y - 10.5


def project_line(c, y, name, stack):
    c.setFont("Helvetica-Bold", 8.55)
    c.setFillColor(NAVY)
    c.drawString(LEFT, y, name)
    name_w = pdfmetrics.stringWidth(name + "   ", "Helvetica-Bold", 8.55)
    c.setFont("Helvetica-Oblique", 7.55)
    c.setFillColor(TEAL)
    c.drawString(LEFT + name_w, y, stack)
    return y - 10.5


def main():
    c = canvas.Canvas(str(OUT), pagesize=letter)
    c.setTitle("Madiha M. Shahid - AI/ML Engineer Resume")
    c.setAuthor("Madiha M. Shahid")
    c.setSubject("Resume for AI/ML and Generative AI roles")
    y = TOP

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 17.4)
    c.drawCentredString(W / 2, y, "MADIHA M. SHAHID")
    y -= 13.2
    c.setFont("Helvetica-Bold", 9.4)
    c.setFillColor(TEAL)
    c.drawCentredString(W / 2, y, "AI / ML Engineer  |  Generative AI")
    y -= 12.2

    c.setFont("Helvetica", 7.7)
    c.setFillColor(MUTED)
    contact = "Karachi, Pakistan   |   "
    x = (W - pdfmetrics.stringWidth(
        contact + EMAIL + "   |   +92 321 8997716   |   LinkedIn   |   GitHub",
        "Helvetica",
        7.7,
    )) / 2
    c.drawString(x, y, contact)
    x += pdfmetrics.stringWidth(contact, "Helvetica", 7.7)
    c.setFillColor(TEAL)
    ew = pdfmetrics.stringWidth(EMAIL, "Helvetica", 7.7)
    c.drawString(x, y, EMAIL)
    c.linkURL(f"mailto:{EMAIL}", (x, y - 2, x + ew, y + 9), relative=0)
    x += ew
    c.setFillColor(MUTED)
    mid = "   |   +92 321 8997716   |   "
    c.drawString(x, y, mid)
    x += pdfmetrics.stringWidth(mid, "Helvetica", 7.7)
    c.setFillColor(TEAL)
    lw = pdfmetrics.stringWidth("LinkedIn", "Helvetica", 7.7)
    c.drawString(x, y, "LinkedIn")
    c.linkURL(LINKEDIN, (x, y - 2, x + lw, y + 9), relative=0)
    x += lw
    c.setFillColor(MUTED)
    sep = "   |   "
    c.drawString(x, y, sep)
    x += pdfmetrics.stringWidth(sep, "Helvetica", 7.7)
    c.setFillColor(TEAL)
    gw = pdfmetrics.stringWidth("GitHub", "Helvetica", 7.7)
    c.drawString(x, y, "GitHub")
    c.linkURL(GITHUB, (x, y - 2, x + gw, y + 9), relative=0)

    y -= 16
    y = section(c, y, "Professional Summary")
    y -= 3.2
    y = para(
        c,
        y,
        "Final-year BS Computer Science student at KIET (CGPA 3.6/4.0) with 6+ months of industry "
        "experience building and deploying AI systems. Hands-on with Generative AI (LLMs, prompt "
        "engineering, structured JSON output, Chain-of-Thought, Gemini API), Google Vertex AI "
        "chatbots, computer vision, and full-stack Python apps (Django, React, Streamlit). "
        "Actively building a portfolio in RAG, LangChain, and Hugging Face Transformers. "
        "Seeking internship or junior roles in Generative AI, AI/ML Engineering, or Applied NLP.",
    )
    y -= 6.5

    y = section(c, y, "Education")
    y -= 3.2
    y = role_line(c, y, "BS Computer Science - KIET University, Karachi", "Expected 2027")
    c.setFont("Helvetica", 8.05)
    c.setFillColor(BODY)
    c.drawString(LEFT, y, "CGPA: 3.6 / 4.0")
    y -= 11
    y = role_line(c, y, "Intermediate (Computer Science) - NCR CET College, Karachi", "2021 - 2022")
    y = role_line(c, y, "Matriculation - The Educators, Karachi", "2020")
    y -= 2.5

    y = section(c, y, "Technical Skills")
    y -= 3.2
    y = labeled(
        c,
        y,
        "Generative AI:",
        "LLMs, Prompt Engineering, RAG, LangChain, Hugging Face Transformers, Google Gemini API, "
        "Vertex AI, Chain-of-Thought, Structured JSON Output, Embeddings, n8n AI workflows",
    )
    y = labeled(
        c,
        y,
        "Machine Learning:",
        "PyTorch, TensorFlow Lite, scikit-learn, Pandas, NumPy, Matplotlib, OpenCV, Computer Vision, "
        "NLP, Feature Engineering, Model Evaluation",
    )
    y = labeled(c, y, "Languages:", "Python, JavaScript, Java, C#, SQL")
    y = labeled(
        c,
        y,
        "Web / Apps:",
        "React.js, Django, Node.js, Streamlit, REST APIs, HTML, CSS, Firebase",
    )
    y = labeled(c, y, "Databases:", "MySQL, Microsoft SQL Server")
    y = labeled(
        c,
        y,
        "Tools:",
        "Git, GitHub, Docker, Jupyter Notebook, VS Code, Postman, Android Studio",
    )
    y -= 4.5

    y = section(c, y, "Work Experience")
    y -= 3.2
    y = role_line(c, y, "Junior AI/ML Developer  |  Swag Kicks, Karachi", "Jan 2026 - Apr 2026")
    y = bullets(
        c,
        y,
        [
            "Built and deployed an AI chatbot on Google Vertex AI, covering conversation design, model integration, and end-to-end testing.",
            "Trained and evaluated Vertex AI models; used performance metrics to iterate configuration before production release.",
            "Labeled computer-vision datasets (bounding boxes) and ran pre-deployment tests to catch failure cases.",
        ],
        MAX_W,
    )
    y -= 1.4
    y = role_line(c, y, "AI/ML Intern  |  Swag Kicks, Karachi", "Nov 2025 - Dec 2025")
    y = bullets(
        c,
        y,
        [
            "Trained scikit-learn classification models with preprocessing, feature extraction, and benchmark comparisons.",
            "Integrated model outputs into the product layer using React.js and Node.js REST APIs.",
        ],
        MAX_W,
    )
    y -= 1.4
    y = role_line(c, y, "Machine Learning Intern  |  Elevvo (Remote)", "Sep 2025")
    y = bullets(
        c,
        y,
        [
            "Benchmarked ML models on real-world datasets; improved results via EDA, cleaning, and hyperparameter tuning.",
            "Built preprocessing pipelines for missing values, outliers, and categorical encoding.",
        ],
        MAX_W,
    )
    y -= 4.5

    y = section(c, y, "Projects")
    y -= 3.2
    y = project_line(c, y, "Explain Like I'm a Bot", "React, Django, Gemini API, Prompt Engineering")
    y = bullets(
        c,
        y,
        [
            "Full-stack Generative AI app that explains any topic in a chosen persona (Intern, Professor, Journalist, Executive) with browser speech playback.",
            "Wrote persona system prompts and a Django REST API consumed by a React (Vite) frontend.",
        ],
        MAX_W,
    )
    y = project_line(c, y, "Resume to Interview Questions Generator", "Streamlit, Gemini, Structured JSON")
    y = bullets(
        c,
        y,
        [
            "LLM app that converts resume text into validated JSON: skills, gaps, interview questions, and difficulty, with schema checks on model output.",
        ],
        MAX_W,
    )
    y = project_line(c, y, "Chain-of-Thought + Persona Reasoning", "Streamlit, Gemini, Prompt Engineering")
    y = bullets(
        c,
        y,
        [
            "Compared direct answers vs. persona + step-by-step Chain-of-Thought on the same scenarios to study reasoning quality.",
        ],
        MAX_W,
    )
    y = project_line(c, y, "Jarvis - AI Voice Assistant", "Python, SpeechRecognition, REST APIs")
    y = bullets(
        c,
        y,
        [
            "Voice assistant with NLP intent parsing; pulls live weather/news and runs tasks from spoken commands.",
        ],
        MAX_W,
    )
    y = project_line(c, y, "Face Recognition Attendance System", "Android, FaceNet, ML Kit, TensorFlow Lite")
    y = bullets(
        c,
        y,
        [
            "Android attendance app with FaceNet embeddings, blink-based anti-spoofing, and Firebase attendance storage.",
        ],
        MAX_W,
    )
    y = project_line(c, y, "Loan Approval Prediction", "Python, scikit-learn, Pandas")
    y = bullets(
        c,
        y,
        [
            "Random Forest classifier with k-fold cross-validation and an end-to-end feature-engineering pipeline.",
        ],
        MAX_W,
    )
    y -= 4.5

    y = section(c, y, "Certifications")
    y -= 3.2
    c.setFont("Helvetica", 8.1)
    c.setFillColor(BODY)
    for cert in [
        "Google Cloud / Coursera - Introduction to AI and Machine Learning (Sep 2025)",
        "Simplilearn SkillUp - Deep Learning for Beginners (Jul 2026)",
        "Deloitte / Forage - Data Analytics Job Simulation (Jun 2026)",
        "HackerRank - Python (Basic) (Aug 2025)",
    ]:
        c.drawString(LEFT + 4, y, "-")
        c.drawString(LEFT + 14, y, cert)
        y -= 10.4

    c.save()
    print(f"Wrote {OUT} (final y={y:.1f})")


if __name__ == "__main__":
    main()
