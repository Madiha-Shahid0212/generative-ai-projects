from agents import (
    run_founder_agent,
    run_investor_agent,
    run_market_analyst_agent,
)

SAMPLE_RAW_IDEA = (
    "An app that reminds busy parents when kids need school supplies, "
    "and lets them order the missing items in one tap."
)

SAMPLE_EXPANDED_IDEA = """
## Expanded Idea
A mobile app that tracks a child's school supply list, sends reminders
when items run low, and lets parents reorder from local stores.

## Target Audience
Working parents with school-age children who forget supply restocks.

## Business Model
Affiliate fees on orders, plus a low-cost premium plan for multiple kids.

## Core Features
Supply list, reminders, one-tap reorder, store comparison, shared family list.
""".strip()


def _print_section(title, text):
    print("=" * 60)
    print(title)
    print("=" * 60)
    print(text)
    print()


if __name__ == "__main__":
    founder_output = run_founder_agent(SAMPLE_RAW_IDEA)
    _print_section("FOUNDER AGENT", founder_output)

    investor_output = run_investor_agent(SAMPLE_EXPANDED_IDEA)
    _print_section("INVESTOR AGENT", investor_output)

    market_output = run_market_analyst_agent(SAMPLE_EXPANDED_IDEA)
    _print_section("MARKET ANALYST AGENT", market_output)
