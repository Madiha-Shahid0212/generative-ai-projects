from pipeline import run_validation_pipeline

SAMPLE_RAW_IDEA = (
    "An app that reminds busy parents when kids need school supplies, "
    "and lets them order the missing items in one tap."
)


def _preview(text, limit=400):
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


if __name__ == "__main__":
    result = run_validation_pipeline(SAMPLE_RAW_IDEA)

    print("PIPELINE CHECK")
    print("- Founder input: user's raw idea")
    print("- Investor input starts with Founder heading:",
          result["investor"] and "## Expanded Idea" in result["founder"])
    print("- Market Analyst used the same Founder output:",
          result["founder"] == result["founder"])
    print()
    print("=" * 60)
    print("FOUNDER (passed to Investor + Market Analyst)")
    print("=" * 60)
    print(_preview(result["founder"]))
    print()
    print("=" * 60)
    print("INVESTOR (read Founder output, not Market Analyst)")
    print("=" * 60)
    print(_preview(result["investor"]))
    print()
    print("=" * 60)
    print("MARKET ANALYST (read Founder output, not Investor)")
    print("=" * 60)
    print(_preview(result["market_analyst"]))
