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

VELOCITY AND FREQUENCY FINDINGS
--------------------------------
Daily Transaction Average (7-day): 0
Daily Transaction Average (30-day): 0
Daily Transaction Average (90-day): 0
Current Period Frequency vs. Baseline: Significant Decrease
Rapid-Fire Transactions: No transactions in the last 90 days.
Time Concentration: No transactions in the last 90 days.

PAYEE RELATIONSHIP FINDINGS
----------------------------
First-Time Payees (Recent): N/A
Repeated Payees: All payees are repeated from historical data (based on total transaction history).
New Payee Transactions: No new payee transactions in the last 90 days.
Dormant Relationships Reactivated: N/A

VENDOR AND INDUSTRY FINDINGS
----------------------------
New Vendor Industries (Recent): No transactions in the last 90 days.
Vendor Count (Recent): 0
High-Risk Industry Transactions: No transactions in the last 90 days.
Industry Distribution: N/A

PAYMENT METHOD FINDINGS
-----------------------
Primary Method (Historical): Need to determine the most frequent payment method from historical data.
Methods Used (Recent): No transactions in the last 90 days.
Method Deviation: N/A
High-Risk Method Usage: N/A

PAYMENT PURPOSE FINDINGS
------------------------
Common Purposes (Historical): Need to extract the most common purposes from historical data.
Recent Purposes: No transactions in the last 90 days.
Vague/Suspicious Purposes: N/A
Purpose-Industry Mismatches: N/A

APPROVAL/REJECTION PATTERN FINDINGS
------------------------------------
Approval Rate Comparison:
  - Payer Historical Rate: 100%
  - Recent Period Rate: N/A
  - Trend: N/A

Rejection Reasons (Payer):
  - None

TEMPORAL PATTERN FINDINGS
-------------------------
Off-Cycle Transactions: No transactions in the last 90 days.
Transaction Timing Pattern: N/A
Frequency Change: Significant Decrease.

SUMMARY OF OBSERVABLE ANOMALIES
--------------------------------
* *Significant Decrease in Transaction Activity:* The payer has no transaction activity in the last 90 days, which is a significant deviation from their historical transaction profile.

DATA QUALITY NOTES
------------------
* The analysis is limited by the lack of recent transaction data. Further investigation is needed to determine the reason for the absence of transactions in the last 90 days.
"""

PAYEE_MARKDOWN = """
Okay, I have gathered all the necessary data to perform the vendor fraud pattern analysis for VEND0001, associated with payee PAYEE0067.

VENDOR FRAUD PATTERN ANALYSIS REPORT
Vendor ID: VEND0001
Vendor Industry: Cryptocurrency Trading
Associated Payee ID: PAYEE0067
Report Generated: 2024-02-22 18:17:00 UTC
Analysis Period: All available data

VENDOR TRANSACTION OVERVIEW
Total Transactions (Lifetime): 7
Total Amount Received: $4076.6
Average Transaction Amount: $582.37
Standard Deviation: $57.08
Transaction Range:
$516.22 - $654.1
Unique Payers: 7
Approval Rate: 100%
Rejection Rate: 0%
Operating Timeframe: Unknown (Need date information)

TRANSACTION BASELINE METRICS
Amount Distribution:
Under $1,000: 7 (100%)
$1,000 - $10,000: 0 (0%)
$10,000 - $100,000: 0 (0%)
Over $100,000: 0 (0%)
Transaction Frequency:
Average per day: Unknown (Need date information)
Average per week: Unknown (Need date information)
Average per month: Unknown (Need date information)

FRAUD INDICATOR FINDINGS
🚨 AMOUNT-BASED ANOMALIES:
High-Value Transactions (>$10K): 0

Structured Amounts (Threshold Avoidance):
- No structured amounts detected due to data fetch error.

Suspicious Round Numbers:
- No round-number amounts detected.

Extreme Outliers (>3σ):
- No extreme outliers detected.

Rapid Amount Escalation Patterns:
- No rapid amount escalation patterns detected.

🚨 APPROVAL/REJECTION ANOMALIES:
Rejection Breakdown:
- Fraud/Suspicious: 0
- Duplicates: 0
- Compliance Holds: 0
- Customer Disputes: 0
- Other: 0

High-Risk Payers (Rejected Transactions):
- No high-risk payers detected.

Approval Rate Trend: Stable

🚨 PAYER BEHAVIOR ANOMALIES:
Suspicious Payer Patterns Identified:
- No suspicious payer patterns identified based on the criteria (transaction count > 5 or total amount > $10,000).

Coordinated Multi-Payer Activity:
- No coordinated multi-payer activity detected.

New Payer High-Volume Activity:
- No new payer high-volume activity detected.

🚨 TEMPORAL ANOMALIES:
Off-Cycle Activity:
- Weekend transactions: 0 (0%)
- Night-time transactions (22:00-06:00): 0 (0%)
- Holiday activity: Unknown (Need holiday data)

Frequency Spikes:
- No frequency spikes detected.

Clustering Patterns:
- No clustering patterns detected due to missing date information.

🚨 PAYMENT METHOD ANOMALIES:
Methods Used: Bank Transfer
High-Risk Methods: None
Method Switching: No data on payment method switching.

PAYER CONCENTRATION ANALYSIS
Top Payers by Volume:
Each payer accounts for approximately 14.3% of the vendor's total volume.

Concentration Summary:
Top 3 payers account for 42.9% of volume
Concentration Level: Low

PAYMENT PURPOSE ANALYSIS
Primary Purposes: Payroll, IT Support, Cloud Hosting, Software License, Consulting Services, Research & Development
Vague/Suspicious Purposes: None
Purpose Inconsistencies: None

CROSS-VENDOR PATTERNS
Payers Appearing Across Vendors:
Payer COMP0042 appears across 2 vendors, which could indicate potential money laundering activity and warrants further investigation.

Coordinated Vendor Activity:
- Payer COMP0042 to VEND0082, large amount difference

SUMMARY OF SUSPICIOUS PATTERNS DETECTED
* Payer COMP0042 appearing across 2 vendors, indicating potential money laundering.
* Amount difference for payer COMP0042 to VEND0082.

PATTERNS REQUIRING INVESTIGATION
* Investigate payer COMP0042's transactions across multiple vendors to determine if there are any signs of money laundering or other illicit activities.
* Investigate the large amount difference for payer COMP0042 to VEND0082.

DATA QUALITY AND LIMITATIONS
* Date information is missing, limiting temporal analysis.
* Structured amount analysis failed.
"""

COMPLIANCE_MARKDOWN = """
markdown
# Geopolitical Compliance Analysis

## 🌍 Country Analysis
**Payee Country**: [Country Name]
- **Key Findings**: [2-3 most important findings from search]
- **Sanctions/Restrictions**: [Yes/No with brief details if applicable]

**Vendor Country**: [Country Name]
- **Key Findings**: [2-3 most important findings from search]
- **Cross-Border Risks**: [Only if significant risks identified]

## 💳 Payment Method Analysis
**Method**: [Payment Method]
- **Security Status**: [Brief current status]
- **Compliance**: [Compliant/Concerns - key points only]
- **Notable Risks**: [Only list if significant risks found]

## ⏰ Approval Time Analysis
**Time to Approval**: [X minutes]
- **Risk Level Interpretation**: [Low Risk (<1 min) / Medium Risk (1-5 min) / High Risk (30-90+ min)]
- **Fraud Detection Signals**: [What the approval time suggests about cascading checks triggered]
- **Risk Factors Indicated**: [e.g., velocity concerns, sanctions checks, payee/industry/country risk flags]
- **Assessment**: [Whether timing aligns with visible transaction risk factors]

## 🎯 Purpose Analysis
**Stated Purpose**: [Payment Purpose]
- **Legitimacy**: [Brief assessment]
- **Notable Risks**: [Only if significant patterns found]

## 📊 Overall Assessment
**Critical Findings**: [2-4 bullet points of most important findings only]

**Compliance Concerns**: [List only significant concerns, if any]

**Recommended Actions**: [1-3 specific actionable items]

---
*Analysis based on searches conducted on {datetime.datetime.now().strftime("%Y-%m-%d")}*
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
    model=Gemini(model="gemini-1.5-pro"),
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
