from gemini_client import generate_text
from prompts import (
    AGENT_PROMPTS,
    FOUNDER_AGENT_KEY,
    INVESTOR_AGENT_KEY,
    MARKET_ANALYST_AGENT_KEY,
)


def _run_agent(agent_key, user_prompt):
    agent = AGENT_PROMPTS[agent_key]
    return generate_text(
        user_prompt,
        system_instruction=agent["system_prompt"],
    )


def run_founder_agent(raw_idea):
    prompt = (
        "Turn this raw startup idea into an expanded plan.\n\n"
        f"RAW IDEA:\n{raw_idea}"
    )
    return _run_agent(FOUNDER_AGENT_KEY, prompt)


def run_investor_agent(expanded_idea):
    prompt = (
        "Review this expanded startup idea as a skeptical investor.\n\n"
        f"EXPANDED IDEA:\n{expanded_idea}"
    )
    return _run_agent(INVESTOR_AGENT_KEY, prompt)


def run_market_analyst_agent(expanded_idea):
    prompt = (
        "Analyze the market and competition for this expanded startup idea.\n\n"
        f"EXPANDED IDEA:\n{expanded_idea}"
    )
    return _run_agent(MARKET_ANALYST_AGENT_KEY, prompt)
