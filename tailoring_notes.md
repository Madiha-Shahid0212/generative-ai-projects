# Novo AI tailoring notes

## Source of truth

- Original CV (first extracted `MadihaShahid.pdf` in this engagement) plus later user-confirmed SwagKicks / Novo brief facts.
- In-repo evidence: `support-ticket-triage`, `promise-vs-fine-print`, `startup-idea-validator`, `resume-interview-generator`.
- Family-business API work, phone number, Intermediate education, and certifications were on later confirmed CVs, not in this repo. Confirm before submitting if any should be dropped.
- Job Aggregator is from prior GitHub/CV evidence (`n8n-Automation-`); the workflow file is not in this checkout.

## Recruiter corrections applied

- Removed HITL / "human in review" product language. Summary now states the app returns a cited draft when evidence is missing or conflicting.
- Removed defensive "not a production / not medical / not self-improving" closers from project bullets. Those caveats stay here.
- Replaced "crash the app" with fence-strip + schema reject (matches triage / interview-generator parsers).
- Replaced Sheets "audited" with "logged".
- Restored Resume to Interview Questions Generator (Novo priority project; structured JSON extract + reject-invalid).
- Added evidenced tools: Streamlit, Pydantic, Git/GitHub.
- Normalized all dates and cert separators to ASCII hyphens so PDF and DOCX extract the same text.
- Education date restored to original CV: Expected 2027 (not June 2027).
- LinkedIn, GitHub, and email are clickable in PDF and DOCX.

## Novo AI requirements vs background

### Strong matches
- Structured outputs from unstructured text (triage JSON; Promise vs Fine Print JSON; interview-generator schema).
- Multi-step AI workflows (retrieve -> generate; n8n retrieve -> score -> decide -> log; founder -> investor/analyst agents).
- RAG / document retrieval with citations (Chroma + Qwen; PDF chunk/embed/retrieve + Gemini).
- Validation and error handling of model JSON (Pydantic / custom parsers; reject invalid replies).
- API integration (REST-backed product screens; job APIs; Gemini / Groq / Qwen).
- Model evaluation on local samples (SwagKicks pass/fail review; policy-conflict test case).

### Partial matches
- Document intelligence: Promise vs Fine Print extracts and compares PDFs. It is not medical invoices or healthcare records.
- Agent pipelines that evaluate outputs: Startup validator uses separate critic agents; triage prefers policy over a conflicting ticket. Neither pipeline autonomously improves itself in production.
- Querying structured data: Job Aggregator and Google Sheets logging; SQL listed as a skill. No autonomous warehouse investigation.
- Production reliability / monitoring: local model review and draft-for-human patterns only. No production agent monitoring, anomaly detection service, or rollback system.

### No evidence (do not claim)
- Healthcare AI, medical billing, insurance, or clinical document expertise.
- Production agents serving real customers at Novo-like scale.
- Automated rollback, observability platforms, or self-improving production agents.
- Kubernetes, Docker, AWS/Azure, distributed systems.
- TensorFlow.
- 1-2 years of professional experience (Intern Nov-Dec 2025, Junior Jan-Apr 2026, Elevvo Sep 2025).

## Projects selected

1. Support Ticket Triage Desk - strongest LLM + RAG + structured JSON + validation evidence in-repo.
2. Promise vs Fine Print - closest transferable document-intelligence project.
3. Job Aggregator - multi-step automation + API + LLM decision + logged state.
4. Startup Idea Validator - multi-agent handoff with separate evaluation roles.
5. Resume to Interview Questions Generator - structured extract from unstructured text + schema reject.

## Projects not used
- Explain Like I'm a Bot: full-stack Gemini app; weaker fit than document/RAG/agent workflows.

## Needs confirmation
- Official SwagKicks title: Novo brief uses Junior AI/ML Engineer. Original CV used Junior AI/ML Developer.
- Vertex AI Edge: on the Novo brief and later user notes, not on the original PDF (original said Google Vertex AI).
- Family-business role, phone, Intermediate, and the four certifications.
- Job Aggregator details if the GitHub workflow has changed.
