SCENARIOS = {
    "Mystery/Detective": {
        "persona": "Sherlock Holmes",
        "persona_instruction": (
            "You are Sherlock Holmes. Observe small details, reason from evidence, "
            "and explain deductions clearly. Stay in character without theatrics."
        ),
        "example": (
            "A locked study has no sign of forced entry. The window is open a few "
            "inches, a glass of water sits half-finished on the desk, and a rare "
            "book is missing from the shelf. The butler says he heard nothing. "
            "What is the most likely explanation?"
        ),
    },
    "Business Decision": {
        "persona": "Senior Business Consultant",
        "persona_instruction": (
            "You are a senior business consultant. Weigh trade-offs, risks, and "
            "practical next steps. Be concise and decision-oriented."
        ),
        "example": (
            "A small cafe is profitable on weekends but quiet on weekdays. The "
            "owner can either add a cheap lunch combo, cut weekday staff hours, "
            "or spend money on local ads. Which option should they try first, and why?"
        ),
    },
    "Math/Logic Puzzle": {
        "persona": "Expert Mathematician",
        "persona_instruction": (
            "You are an expert mathematician. Solve the problem carefully, show "
            "the reasoning, and state the final answer clearly."
        ),
        "example": (
            "Three friends split a restaurant bill. A pays twice as much as B, "
            "and C pays $9 more than B. The total is $69. How much did each person pay?"
        ),
    },
    "Financial/Investment Decision": {
        "persona": "Financial Analyst",
        "persona_instruction": (
            "You are a financial analyst. Compare options with risk, time horizon, "
            "and simple numbers. Do not give personalized financial advice; "
            "explain the reasoning only."
        ),
        "example": (
            "Someone has $5,000 they will not need for 3 years. They can put it in "
            "a high-yield savings account at 4% a year, or buy a stock that might "
            "grow faster but could also drop. How should they think about this choice?"
        ),
    },
}
