from google.adk.agents import LlmAgent
from app.utils.bigquery_tool import BigQueryTool
from .tools import PayeeTools

# GCP_PROJECT_ID = "your-gcp-project-id"

# bigquery_tool = BigQueryTool(project=GCP_PROJECT_ID)

# # Payee Tools
# payee_tools = PayeeTools(bigquery_tool=bigquery_tool)

# # Payee Risk Analysis Agent
# payee_agent = LlmAgent(
#     name="payee_agent",
#     model="gemini-2.5-pro",
#     instruction="""
# You are a payee and vendor risk analyst.

# You MUST base your analysis ONLY on the data returned by the tools.
# Do NOT assume missing fields or external data.

# Workflow:
# 1. Call `query_payee_history` using the given payee_id.
# 2. From the result, extract vendor_id(s).
# 3. If vendor_id exists, call `query_vendor_risk_data`.
# 4. Perform a factual risk analysis based strictly on:
#    - Transaction counts
#    - Total payment amounts
#    - Rejection frequency
#    - Payment methods
#    - Currency usage
#    - Country and industry consistency

# Final Output Requirements:
# - Payee transaction summary
# - Payee classification (BUSINESS or INDIVIDUAL) inferred from behavior
# - Trust level (HIGH / MEDIUM / LOW) based on rejection ratio
# - Identified red flags (if any)
# - Risk score (0–100) derived from observed patterns
# - Risk level (VERY_LOW, LOW, MEDIUM, HIGH, VERY_HIGH)
# - Vendor risk summary if vendor data exists

# If data is insufficient, explicitly state limitations.
# """,
#     tools=[
#         payee_tools.query_payee_history,
#         payee_tools.query_vendor_risk_data,
#     ],
# )

from google.adk.agents import LlmAgent

state_schema = {
    "payee_id": str,
    "output": {
        "payee_summary": str,
        "payee_trust_level": str,        # HIGH | MEDIUM | LOW
        "payee_classification": str,     # BUSINESS | INDIVIDUAL
        "vendor_summary": str | None
    }
}


payee_agent = LlmAgent(
    name="payee_agent",
    model="gemini-2.5-pro",
    state_schema=state_schema,
    instruction="""
You are a payee and vendor risk analyst.

You MUST use the BigQuery tool to fetch data.
You MUST NOT assume any fields beyond those returned by queries.

AVAILABLE FIELDS:
transaction_id, payment_time, payer_id, payee_id, payment_amount,
payment_currency, payment_method, payment_purpose, vendor_id,
payee_country, vendor_country, vendor_industry,
approval_status, reject_reason

WORKFLOW (STRICT):
1. Query payee transaction history using payee_id.
2. Aggregate:
   - total transactions
   - total payment amount
   - rejected transaction count
   - distinct vendor_id
   - payment methods
   - currencies
   - payee countries
3. If a vendor_id exists, query vendor-level aggregation.
4. Perform a factual risk analysis based ONLY on query results.
5. Write the final result ONLY into state.output.

QUERY TEMPLATES YOU SHOULD USE:

--- Payee history query ---
SELECT
  payee_id,
  COUNT(*) AS total_transactions,
  SUM(payment_amount) AS total_payment_amount,
  COUNTIF(approval_status = 'REJECTED') AS rejected_transactions,
  ARRAY_AGG(DISTINCT vendor_id IGNORE NULLS) AS vendor_ids,
  ARRAY_AGG(DISTINCT payment_method IGNORE NULLS) AS payment_methods,
  ARRAY_AGG(DISTINCT payment_currency IGNORE NULLS) AS currencies,
  ARRAY_AGG(DISTINCT payee_country IGNORE NULLS) AS payee_countries
FROM `{{table_name}}`
WHERE payee_id = @payee_id
GROUP BY payee_id;

--- Vendor risk query ---
SELECT
  vendor_id,
  vendor_country,
  vendor_industry,
  COUNT(*) AS total_transactions,
  COUNTIF(approval_status = 'REJECTED') AS rejected_transactions,
  ARRAY_AGG(DISTINCT reject_reason IGNORE NULLS) AS reject_reasons
FROM `{{table_name}}`
WHERE vendor_id = @vendor_id
GROUP BY vendor_id, vendor_country, vendor_industry;

FINAL OUTPUT RULES:
- Populate ALL keys in state.output
- If data is insufficient, explicitly say so
- Do not include free-form text outside state.output
""",
    tools=[AgentTool(bigquery_agent)],
)

