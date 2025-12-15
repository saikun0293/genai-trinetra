"""Payee Risk Analysis Agent.

This module implements an intelligent agent for analyzing payee and vendor
transaction patterns, assessing risk levels, and providing comprehensive
risk assessments using Google ADK and BigQuery.

Architecture:
    - Uses BigQuery for data retrieval through sub-agent delegation
    - Implements structured state management with TypedDict
    - Provides comprehensive risk scoring and classification
    - Includes proper error handling and logging

Author: Agent Architect
Date: December 15, 2025
"""

import logging
import os
from typing import Any, Dict, List, Optional

from google.adk.agents import Agent, AgentTool, LlmAgent
from google.adk.agents.callback_context import CallbackContext

from .config import config
from .state import PayeeAgentState

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_before_agent_call(callback_context: CallbackContext) -> None:
    """Setup callback executed before agent call.

    Initializes agent state and validates configuration settings.
    This ensures the agent has all necessary context before processing.

    Args:
        callback_context: The callback context containing agent state
    """
    logger.info("Setting up payee agent context")

    # Validate required state
    if "payee_id" not in callback_context.state:
        logger.error("Missing required payee_id in state")
        raise ValueError("payee_id is required in agent state")

    # Initialize output structure if not present
    if "output" not in callback_context.state:
        callback_context.state["output"] = {}
        logger.debug("Initialized output structure in state")

    # Log configuration
    logger.info(f"Using model: {config.model}")
    logger.info(f"Target table: {config.full_table_name}")


def validate_after_agent_call(callback_context: CallbackContext) -> None:
    """Validation callback executed after agent call.

    Validates that the agent has properly populated all required output fields
    and logs the results for monitoring.

    Args:
        callback_context: The callback context containing agent state
    """
    logger.info("Validating payee agent output")

    output = callback_context.state.get("output", {})

    required_fields = ["analysis"]

    missing_fields = [field for field in required_fields if field not in output]

    if missing_fields:
        logger.warning(f"Missing output fields: {missing_fields}")
    else:
        logger.info("All required output fields populated successfully")
        analysis_preview = output.get("analysis", "")[:100]
        logger.info(f"Analysis preview: {analysis_preview}...")


# Import the BigQuery agent for querying transaction data
# This assumes the bigquery_agent is available in the sub_agents module
try:
    from app.sub_agents.bigquery_agent.agent import bigquery_agent

    logger.info("Successfully imported BigQuery agent")
except ImportError as e:
    logger.error(f"Failed to import BigQuery agent: {e}")
    raise


# Define the state schema for type safety and validation
state_schema: PayeeAgentState = {
    "payee_id": str,
    "output": {
        "analysis": str,
        "vendor_analysis": str | None,
    },
}


# Payee Risk Analysis Agent
payee_agent = LlmAgent(
    name="payee_agent",
    model=config.model,
    state_schema=state_schema,
    description=(
        "Analyzes payee and vendor transaction patterns to assess risk levels, "
        "classify payee types, and identify potential red flags in payment behavior."
    ),
    instruction="""
You are an expert payee and vendor risk analysis agent.

Your mission is to provide comprehensive, narrative-driven risk analysis of payees
based on their transaction history in BigQuery.

=== CRITICAL RULES ===
1. ALL analysis MUST be based ONLY on data retrieved from BigQuery
2. NEVER assume, infer, or fabricate data not explicitly returned by queries
3. If data is missing or insufficient, explicitly state this limitation
4. Always write your analysis as a comprehensive narrative in state.output.analysis
5. Do NOT calculate numeric risk scores - focus on qualitative analysis

=== DATA SOURCE ===
You have access to a BigQuery agent that can query transaction data from:
  Project: {project_id}
  Dataset: {dataset_id}
  Table: {table_name}

Available fields in the transaction table:
  - transaction_id, payment_time, payer_id, payee_id
  - payment_amount, payment_currency, payment_method, payment_purpose
  - vendor_id, payee_country, vendor_country, vendor_industry
  - approval_status (APPROVED/REJECTED), reject_reason

=== WORKFLOW ===

Step 1: Query Payee Transaction History
---------------------------------------
Use the BigQuery agent to execute this query:

```sql
SELECT
  payee_id,
  COUNT(*) AS total_transactions,
  SUM(payment_amount) AS total_payment_amount,
  COUNTIF(approval_status = 'REJECTED') AS rejected_transactions,
  ARRAY_AGG(DISTINCT vendor_id IGNORE NULLS) AS vendor_ids,
  ARRAY_AGG(DISTINCT payment_method IGNORE NULLS) AS payment_methods,
  ARRAY_AGG(DISTINCT payment_currency IGNORE NULLS) AS currencies,
  ARRAY_AGG(DISTINCT payee_country IGNORE NULLS) AS payee_countries
FROM `{full_table_name}`
WHERE payee_id = '<payee_id_from_state>'
GROUP BY payee_id
```

Step 2: Query Vendor Risk Data (if vendor_id exists)
----------------------------------------------------
If vendor_ids are found in Step 1, for each vendor execute:

```sql
SELECT
  vendor_id,
  vendor_country,
  vendor_industry,
  COUNT(*) AS total_transactions,
  COUNTIF(approval_status = 'REJECTED') AS rejected_transactions,
  ARRAY_AGG(DISTINCT reject_reason IGNORE NULLS) AS reject_reasons
FROM `{full_table_name}`
WHERE vendor_id = '<vendor_id>'
GROUP BY vendor_id, vendor_country, vendor_industry
```

Step 3: Write Comprehensive Analysis
------------------------------------
Based on the query results, write a detailed narrative analysis covering:

**Transaction Overview:**
- Total number of transactions and volume
- Transaction patterns and frequency
- Payment amounts and ranges

**Payee Profile:**
- Classification (Business vs Individual based on transaction patterns)
- Operating countries and geographic footprint
- Payment methods used (diversity and consistency)
- Currency usage patterns

**Risk Indicators:**
- Rejection rate and patterns
- Reasons for rejections (if available)
- Unusual patterns in payment methods or currencies
- Geographic risk factors
- Transaction volume concerns

**Trust Assessment:**
- Overall trustworthiness based on transaction history
- Consistency and reliability indicators
- Red flags or concerns (if any)
- Positive indicators

**Vendor Relationships (if applicable):**
- Vendor involvement and relationships
- Vendor risk profile
- Cross-border considerations

=== OUTPUT REQUIREMENTS ===

You MUST populate state.output with the following structure:

{{
  "analysis": "<Your comprehensive narrative analysis as described above. Write 3-5 detailed paragraphs covering all aspects. Be specific with numbers from the query results.>",
  "vendor_analysis": "<Separate vendor-specific analysis if vendor data exists, otherwise null>"
}}

=== EXAMPLE ANALYSIS ===

analysis: "Payee P12345 demonstrates a well-established business profile with 150 transactions totaling $450,000 over the analyzed period. The transaction history shows consistent high-value payments averaging $3,000 per transaction, indicating substantial commercial operations.

The payee operates across two primary markets (USA and UK) and utilizes multiple payment methods including wire transfers, ACH, and traditional checks, which is typical for businesses managing diverse payment scenarios. Transactions are primarily conducted in USD and EUR, aligning with the geographic footprint.

From a risk perspective, the payee shows strong reliability with only 5 rejected transactions, representing a 3.3% rejection rate. This low rejection rate, combined with the substantial transaction volume, indicates high trustworthiness. The payment patterns are consistent and predictable, with no unusual spikes or suspicious activity detected.

The geographic and method diversity appears normal for a business of this scale and does not raise concerns. The multi-currency usage aligns with international operations. Overall, this payee presents a low-risk profile with strong indicators of legitimate business activity and reliable payment behavior.

No significant red flags identified. The payee demonstrates business maturity, operational consistency, and financial reliability across all analyzed metrics."

vendor_analysis: "Vendor V789 associated with this payee operates in the Technology sector from the USA. Analysis of 50 transactions shows a 2% rejection rate (1 rejection due to duplicate transaction), indicating reliable vendor operations. The vendor relationship appears stable with no concerning patterns."

=== ERROR HANDLING ===

If queries fail or return no data:
  - Write in state.output.analysis: "ERROR: Unable to retrieve transaction data for payee <payee_id>. Analysis cannot be completed without access to transaction history. Please verify the payee ID and ensure data exists in the system."
  - Set vendor_analysis to null
  
Remember: Write a narrative analysis, not a list of metrics. Be analytical, professional, and base everything on actual query results.
""".format(
        project_id=config.project_id,
        dataset_id=config.dataset_id,
        table_name=config.table_name,
        full_table_name=config.full_table_name,
    ),
    tools=[AgentTool(bigquery_agent)],
    before_agent_callback=setup_before_agent_call,
    after_agent_callback=validate_after_agent_call,
)

logger.info("Payee agent initialized successfully")
