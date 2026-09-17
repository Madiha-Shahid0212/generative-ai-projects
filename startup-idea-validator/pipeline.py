from agents import (
    run_founder_agent,
    run_investor_agent,
    run_market_analyst_agent,
)


def run_validation_pipeline(raw_idea, on_status=None):
    """Run the three-agent chain.

    Flow:
    1. Founder Agent reads the user's raw idea and expands it.
    2. Investor Agent and Market Analyst Agent both receive that
       expanded idea. They do not read each other's output.
    """

    def report(message):
        if on_status:
            on_status(message)

    report("🚀 Founder Agent is thinking...")
    founder_output = run_founder_agent(raw_idea)

    report("💼 Investor Agent is reviewing...")
    investor_output = run_investor_agent(founder_output)

    report("📊 Market Analyst Agent is researching...")
    market_analyst_output = run_market_analyst_agent(founder_output)

    report("All agents finished.")
    return {
        "raw_idea": raw_idea,
        "founder": founder_output,
        "investor": investor_output,
        "market_analyst": market_analyst_output,
    }
