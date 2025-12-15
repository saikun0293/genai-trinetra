from google.adk.agents import LlmAgent
from google.adk.models import Gemini

# ==================================================
# INPUTS (MARKDOWN + TRANSACTIONS)
# ==================================================

PAYER_MARKDOWN = """
==================================
Payer ID: COMP0041
Report Generated: 2024-02-29 15:39:40 UTC
Analysis Period: Last 90 Days

BASELINE PROFILE
----------------
Total Transactions (Historical): 44
Average Transaction Amount: $866.85
Standard Deviation: $594.55
Range: $59.00 - $2254.53
Unique Payees: 41
Unique Vendors: 43
Unique Payment Methods: 5
Approval Rate: 100%
Rejection Rate: 0%

RECENT TRANSACTION SUMMARY (Last 90 Days)
------------------------------------------
Transaction Count (Recent): 0
Average Amount (Recent): N/A
Total Volume (Recent): N/A
Approval Count: 0
Rejection Count: 0

SUMMARY OF OBSERVABLE ANOMALIES
--------------------------------
* Significant decrease in transaction activity (no transactions in last 90 days).
"""

PAYEE_MARKDOWN = """
VENDOR FRAUD PATTERN ANALYSIS REPORT
Vendor ID: VEND0001
Vendor Industry: Cryptocurrency Trading

Total Transactions (Lifetime): 7
Approval Rate: 100%
Rejection Rate: 0%

Key Findings:
- No high-value or structured transactions detected
- No coordinated multi-payer activity
- One external payer (COMP0042) appears across multiple vendors
"""

COMPLIANCE_MARKDOWN = """
# Geopolitical Compliance Analysis

## Country Analysis
- No explicit sanctions identified
- Country data incomplete

## Compliance Concerns
- Missing country and payment method confirmation
- Incomplete compliance metadata

## Recommended Actions
- Request additional compliance documentation
"""

TRANSACTION_COUNTS = {
    "approved": 44,
    "rejected": 0,
    "total_transactions": 44
}

# ==================================================
# CRITIC PROMPT
# ==================================================

CRITIC_PROMPT = """
You are a financial risk scoring agent.

Inputs:
- payer_markdown (markdown)
- payee_markdown (markdown)
- compliance_markdown (markdown)
- transaction_counts (JSON)

Your task is to internally perform the following:

1. Derive four internal sub-scores (0–100):
   - Payer score
   - Payee score
   - Compliance score
   - Transaction score

2. Apply weighted averaging:
   - Payer: 30%
   - Payee: 25%
   - Compliance: 35%
   - Transaction: 10%

3. Produce a final score (0–100)

4. Assign a category:
   - 80–100 → APPROVED
   - 60–79 → REVIEW
   - < 60 → REJECTED

Guidelines:
- Strong approval history is positive
- Dormancy reduces confidence but is not fraud
- Incomplete compliance materially lowers score
- No sanctions is neutral unless stated otherwise
- Transaction approval ratio supports but does not dominate

IMPORTANT:
- Do NOT expose sub-scores
- Do NOT show calculations
- Return ONLY the final result

Return STRICT JSON ONLY:
{
  "score": number,
  "category": "APPROVED | REVIEW | REJECTED",
  "reason": string,
  "notes": string
}
"""

# ==================================================
# SINGLE CRITIC AGENT
# ==================================================

critic_agent = LlmAgent(
    name="single_score_runner",
    model=Gemini(model="gemini-2.5-pro"),
    instruction=CRITIC_PROMPT,
    output_key="risk_result",
    input_keys=[
        "payer_markdown",
        "payee_markdown",
        "compliance_markdown",
        "transaction_counts"
    ]
)

# ==================================================
# RUNNER
# ==================================================

if __name__ == "__main__":
    response = critic_agent.run(
        payer_markdown=PAYER_MARKDOWN,
        payee_markdown=PAYEE_MARKDOWN,
        compliance_markdown=COMPLIANCE_MARKDOWN,
        transaction_counts=TRANSACTION_COUNTS
    )

    print("\n=== FINAL RISK SCORE ===\n")
    print(response["risk_result"])
