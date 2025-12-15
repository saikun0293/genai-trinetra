from google.adk.agents import LlmAgent
from google.adk.models import Gemini

# ==================================================
# MOCK UPSTREAM AGENT OUTPUTS
# ==================================================

payee_agent = """
Vendor Industry: Cryptocurrency Trading
Approval Rate: 100%
No direct fraud indicators detected.
One related payer appears across multiple vendors.
"""

payer_validation_agent = """
Historical approval rate: 100%
No transactions in last 90 days.
Dormancy detected but no anomalies.
"""

geopolitics_agent = """
No explicit sanctions identified.
Country and payment method information missing.
Compliance metadata incomplete.
"""

transaction_agent = """
Total transactions: 44
Approved: 44
Rejected: 0
No frequency spikes detected.
"""

# ==================================================
# CRITIQUE PROMPT
# ==================================================

CRITIQUE_AGENT_PROMPT = """
You are a financial risk scoring agent.

You receive FOUR ANALYSIS INPUTS derived from prior agents:

1. Payee/Vendor Analysis (markdown):
{payee_agent}

2. Payer Validation Analysis (markdown):
{payer_validation_agent}

3. Geopolitical / Compliance Analysis (markdown):
{geopolitics_agent}

4. Transaction Frequency Analysis (markdown or structured summary):
{transaction_agent}

---

YOUR TASK (INTERNAL REASONING ONLY — DO NOT EXPOSE STEPS):

STEP 1 — INPUT-LEVEL ANALYSIS

For EACH input, produce a concise JSON analysis using key–value pairs ONLY.

Include:
- summary
- risk_level: Low | Medium | High
- key_risk_factors
- data_gaps

---

STEP 2 — DERIVE INTERNAL SUB-SCORES (0–100)

• Payer
• Payee
• Compliance / Geopolitics
• Transaction

---

STEP 3 — WEIGHTED AVERAGE

Weights:
- Payer: 35%
- Payee: 25%
- Compliance / Geopolitics: 20%
- Transaction: 20%

---

STEP 4 — FINAL DECISION

- 80–100 → APPROVED
- 60–79 → REVIEW
- < 60   → REJECTED

---

STRICT OUTPUT RULES:
- No markdown
- No calculations
- No sub-scores
- JSON ONLY

RETURN STRICT JSON:

{
  "input_analysis": {
    "payer": {
      "summary": string,
      "risk_level": "Low | Medium | High",
      "key_risk_factors": [string],
      "data_gaps": [string]
    },
    "payee": {
      "summary": string,
      "risk_level": "Low | Medium | High",
      "key_risk_factors": [string],
      "data_gaps": [string]
    },
    "compliance": {
      "summary": string,
      "risk_level": "Low | Medium | High",
      "key_risk_factors": [string],
      "data_gaps": [string]
    },
    "transaction": {
      "summary": string,
      "risk_level": "Low | Medium | High",
      "key_risk_factors": [string],
      "data_gaps": [string]
    }
  },
  "final_decision": {
    "score": number,
    "category": "APPROVED | REVIEW | REJECTED",
    "reason": string,
    "notes": string
  }
}
"""

# ==================================================
# AGENT
# ==================================================

critic_agent = LlmAgent(
    name="single_score_runner",
    model=Gemini(model="gemini-2.5-pro"),
    instruction=CRITIQUE_AGENT_PROMPT,
    output_key="risk_assessment_state",
    input_keys=[
        "payee_agent",
        "payer_validation_agent",
        "geopolitics_agent",
        "transaction_agent"
    ]
)

# ==================================================
# RUNNER
# ==================================================

if __name__ == "__main__":
    result = critic_agent.run(
        payee_agent=payee_agent,
        payer_validation_agent=payer_validation_agent,
        geopolitics_agent=geopolitics_agent,
        transaction_agent=transaction_agent
    )

    print("\n=== RISK ASSESSMENT STATE ===\n")
    print(result["risk_assessment_state"])
