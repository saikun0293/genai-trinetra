"""Quick test/demo of the analysis-based payee agent.

This demonstrates the new simplified output structure focused on narrative analysis.
"""


def demo_analysis_output():
    """Demo showing the expected analysis output format."""

    # Simulated output from the agent
    sample_output = {
        "analysis": """Payee P12345 demonstrates a well-established business profile with 150 transactions totaling $450,000 over the analyzed period. The transaction history shows consistent high-value payments averaging $3,000 per transaction, indicating substantial commercial operations. This level of activity suggests an established business entity with regular payment obligations.

The payee operates across two primary markets (USA and UK) and utilizes multiple payment methods including wire transfers, ACH, and traditional checks, which is typical for businesses managing diverse payment scenarios. Transactions are primarily conducted in USD and EUR, aligning perfectly with the geographic footprint. This multi-method, multi-currency approach is characteristic of international business operations.

From a risk perspective, the payee shows strong reliability with only 5 rejected transactions, representing a 3.3% rejection rate. This low rejection rate, combined with the substantial transaction volume, indicates high trustworthiness and operational maturity. The payment patterns are consistent and predictable, with no unusual spikes or suspicious activity detected throughout the analysis period.

The geographic and payment method diversity appears normal for a business of this scale and does not raise concerns. The multi-currency usage aligns with cross-border operations between the US and UK markets. Transaction amounts show appropriate variation without extreme outliers, suggesting legitimate business activities across various commercial purposes.

Overall assessment: This payee presents a low-risk profile with strong indicators of legitimate business activity and reliable payment behavior. The established transaction history, low rejection rate, consistent patterns, and appropriate use of payment methods all point to a trustworthy business relationship. No significant red flags identified. The payee demonstrates business maturity, operational consistency, and financial reliability across all analyzed metrics.""",
        "vendor_analysis": """Vendor V789 associated with this payee operates in the Technology sector from the USA. Analysis of 50 transactions shows a 2% rejection rate (1 rejection due to duplicate transaction), indicating reliable vendor operations. The vendor relationship appears stable with consistent transaction patterns and no concerning anomalies. The single rejection was administrative in nature and not indicative of any compliance or fraud issues. This vendor-payee relationship demonstrates healthy business operations.""",
    }

    print("=" * 70)
    print("PAYEE ANALYSIS OUTPUT (New Format)")
    print("=" * 70)
    print("\n📊 ANALYSIS:")
    print("-" * 70)
    print(sample_output["analysis"])
    print("\n")

    if sample_output.get("vendor_analysis"):
        print("🏢 VENDOR ANALYSIS:")
        print("-" * 70)
        print(sample_output["vendor_analysis"])

    print("\n" + "=" * 70)
    print("Key Benefits:")
    print("  ✓ Natural language - easy to understand")
    print("  ✓ Comprehensive context in narrative form")
    print("  ✓ LLM provides nuanced insights")
    print("  ✓ Simple state structure (2 fields)")
    print("  ✓ Direct display in UI/reports")
    print("=" * 70)


def demo_usage_pattern():
    """Demo the usage pattern with the new agent."""

    print("\n" + "=" * 70)
    print("USAGE PATTERN")
    print("=" * 70)

    code = """
from app.sub_agents.payee_agent import payee_agent

# Simple input
state = {"payee_id": "P12345"}

# Run analysis
result = payee_agent.run(state=state)

# Access narrative analysis
analysis = result.state["output"]["analysis"]
print(analysis)

# Check for vendor analysis
if result.state["output"]["vendor_analysis"]:
    print("\\nVendor Analysis:")
    print(result.state["output"]["vendor_analysis"])
"""

    print("\nCode Example:")
    print(code)

    print("\nState Schema:")
    print(
        """
{
    "payee_id": str,           # Input
    "output": {                # Output
        "analysis": str,       # Comprehensive narrative
        "vendor_analysis": str | None
    }
}
"""
    )


if __name__ == "__main__":
    demo_analysis_output()
    demo_usage_pattern()
