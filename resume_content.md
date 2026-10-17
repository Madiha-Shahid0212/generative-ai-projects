# Madiha M. Shahid
**AI Engineer | LLM Applications | RAG | Structured Outputs | Multi-Step AI Workflows**

Karachi, Pakistan (Remote) | +92 321 8997716 | madihashahid212@gmail.com

[LinkedIn](https://www.linkedin.com/in/madiha-shahid-a64091308/) | [GitHub](https://github.com/Madiha-Shahid0212)

## Professional Summary

Final-year B.S. Computer Science student at KIET (CGPA 3.6/4.0) with industry experience progressing from AI/ML Intern to Junior AI/ML Engineer. Builds practical LLM applications and multi-step AI workflows that retrieve approved context, extract structured JSON, and validate model output. Returns a cited draft when retrieved evidence is missing or conflicting. Interested in reliable AI systems for document workflows, API integration, and evaluation.

## Technical Skills

- **Programming:** Python, SQL, JavaScript
- **Machine Learning:** scikit-learn, Pandas, NumPy, PyTorch, OpenCV, image classification, model evaluation
- **Generative AI:** LLMs, prompt engineering, Gemini API, Qwen, Groq, LangChain, Retrieval-Augmented Generation (RAG)
- **Data, Retrieval & Validation:** Chroma, Hugging Face embeddings, structured outputs, Pydantic, JSON / schema validation, document retrieval
- **Integration & Automation:** REST APIs, API integration, Node.js, React, Streamlit, n8n, Git, GitHub, multi-step workflow automation
- **Model Workflows:** Google Vertex AI, Vertex AI Edge, model export, local / on-device inference

## Professional Experience

### Thriftops By SwagKicks | Karachi, Pakistan

**Junior AI/ML Engineer** | January 2026 - April 2026

- Integrated AI/ML outputs into product workflows so model results could be reviewed inside application screens rather than only in notebooks.
- Retrained and validated image-classification models for product damage, components, and image angles using Google Vertex AI / Vertex AI Edge workflows.
- Exported models for local / on-device inference and evaluated the 4-class damage model on local samples against defined pass/fail checks before product use.
- Built React.js and Node.js dashboard, sidebar, and profile screens backed by REST APIs to support model-review and validation interfaces.
- Developed AI chatbot functionality that connected model outputs to day-to-day product flows.

**AI/ML Intern** | November 2025 - December 2025

- Researched computer-vision retraining on Google Vertex AI for product images (shoes and bags) and documented download, local testing, and on-device inference steps.
- Compared platform fit for CV retraining and summarized recommendations for local model deployment.
- Designed a sample React.js product dashboard to support model-review and testing workflows.
- Promoted to Junior AI/ML Engineer after the internship.

### Elevvo | Remote

**Machine Learning Intern** | September 2025

- Built Python ML workflows with Pandas, NumPy, and scikit-learn for data preprocessing, training, and evaluation.
- Handled missing values, outliers, and categorical encoding; tuned experiments and documented reusable training steps.

### Family Business | Karachi, Pakistan

**Technical Support / API Integration** | 2023 - Present (part-time)

- Troubleshot and integrated API-based services into day-to-day business workflows.
- Translated operational requirements into technical steps for connecting systems and validating request/response behavior.

## Selected Projects

### Support Ticket Triage Desk

*Python, LangChain, Hugging Face, Chroma, Qwen, Streamlit*

- Built a retrieve-then-generate RAG pipeline: chunk tickets/policies, embed with Hugging Face sentence-transformers, store in Chroma, and send only top-k chunks plus the new ticket to Qwen.
- Wrote a system prompt that forbids invented policy, requires JSON only, and prefers retrieved policy when ticket text conflicts.
- Validated replies with a Pydantic schema (category, priority, similar ticket ids, draft reply, quotes, notes); strips markdown fences and rejects schema-invalid JSON.
- Tested a built-in policy-conflict case (refund window vs. an over-promised ticket) so the draft stays grounded in retrieved text.

### Promise vs Fine Print

*Python, Streamlit, pypdf, NumPy, Gemini API*

- Built a document-comparison RAG app: extract PDF pages, chunk text, embed both sources, retrieve the closest chunks per source, then ask Gemini using only those chunks.
- Returned structured JSON with quotes, chunk ids, file/page citations, and a verdict of Match, Conflict, or Missing.
- Rejected invalid model JSON; the model never receives the full PDFs.

### Job Aggregator - Multi-Step AI Workflow

*n8n, Groq, REST APIs, Google Sheets, Gmail*

- Built a scheduled n8n workflow that retrieves jobs from APIs, normalizes fields, drops duplicates, and calls Groq to score fit, pick a resume variant, and decide the apply method.
- Logged title, company, location, score, and apply method to Google Sheets; sent Gmail only when an application email was present.
- Tested decision thresholds so weak matches were filtered before logging.

### Startup Idea Validator

*Python, Streamlit, Gemini API*

- Built a sequential multi-agent pipeline: Founder Agent expands a raw idea; Investor and Market Analyst agents then review that expansion independently.
- Gave each agent its own system prompt and role; investor and analyst do not read each other's output.

### Resume to Interview Questions Generator

*Python, Streamlit, Gemini API*

- Extracted structured JSON from unstructured resume text (candidate name, skills, weak areas, 5-7 interview questions, difficulty).
- Rejected replies that failed JSON parse, missing keys, wrong list types, or an invalid difficulty value.

## Education

**B.S. Computer Science | Karachi Institute of Economics & Technology (KIET)**

CGPA 3.6/4.0 | Expected 2027

Coursework: Machine Learning, Artificial Intelligence, Data Structures & Algorithms, Database Systems, Computer Networks, Operating Systems.

**Intermediate (CS) | NCR CET College, Karachi**

2021 - 2022

## Certifications

- Google Cloud / Coursera - Introduction to AI and Machine Learning | September 2025
- Simplilearn SkillUp - Deep Learning for Beginners | July 2026
- Deloitte / Forage - Data Analytics Job Simulation | June 2026
- HackerRank - Python (Basic) | August 2025
