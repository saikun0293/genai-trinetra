from collections import defaultdict
import logging
import os
from google.adk.apps.app import App
from google.adk.agents import LlmAgent
from google.cloud import bigquery
from google.adk.tools import FunctionTool
from app.sub_agents.utils import create_analysis_callback
from .prompt import TRANSACTION_AGENT_PROMPT

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
) 

logger = logging.getLogger(__name__)

# Initialize the BigQuery client once to be reused.
bq_client = bigquery.Client()

# --- TODO: Replace this with your actual BigQuery table ID ---
BQ_TABLE_ID = "ccibt-hack25ww7-714.tri_netra_payments.PaymentsCompliance"

def analyze_transaction_frequency(
    payer_id: str,
    vendor_id: str,
    transaction_id: str
) -> str:
    """
    Evaluates a single transaction using historical payer-vendor behavior and returns a markdown summary.
    """
 
    query = f"""
    SELECT
      COUNTIF(approval_status = 'APPROVED') as approved_count,
      COUNTIF(approval_status = 'REJECTED') as rejected_count,
      COUNT(*) as total_transactions
    FROM `{BQ_TABLE_ID}`
    WHERE payer_id = @payer_id
      AND vendor_id = @vendor_id
    """
    try:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("payer_id", "STRING", payer_id),
                bigquery.ScalarQueryParameter("vendor_id", "STRING", vendor_id),
            ]
        )
        results = list(bq_client.query(query, job_config=job_config).result())
        
        if not results:
            stats = {"approved_count": 0, "rejected_count": 0, "total_transactions": 0}
        else:
            stats = dict(results[0])
        
        total = stats.get("total_transactions", 0)
        approved = stats.get("approved_count", 0)
        rejected = stats.get("rejected_count", 0)

        approval_rate = approved / total if total else 0
        rejection_rate = rejected / total if total else 0

        if total == 0:
            # No history for this payer-vendor pair, consider it medium risk.
            risk_score = 50
            risk_level = "MEDIUM"
        else:
            risk_score = rejection_rate * 100
            risk_level = "HIGH" if risk_score >= 80 else "MEDIUM" if risk_score >= 50 else "LOW"

        action = "ALLOW" if risk_level == "LOW" else "REVIEW" if risk_level == "MEDIUM" else "BLOCK"

        markdown_output = f"""### Transaction Frequency Analysis
- **Transaction ID**: {transaction_id}
- **Payer ID**: {payer_id}
- **Vendor ID**: {vendor_id}
#### Historical Summary
- **Total Transactions**: {total}
- **Approved**: {approved}
- **Rejected**: {rejected}
- **Approval Rate**: {approval_rate:.0%}
- **Rejection Rate**: {rejection_rate:.0%}
#### Risk Assessment
- **Risk Score**: {risk_score:.0f}
- **Risk Level**: {risk_level}
#### Recommended Decision
- **Action**: {action}
"""
        return markdown_output
    except Exception as e:
        logger.error(f"Error analyzing transaction frequency for payer {payer_id}, vendor {vendor_id}: {e}")
        return f"Error analyzing transaction: {e}"


transaction_agent = LlmAgent(
    name="transaction_agent",
    model=os.environ.get("ADK_MODEL", "gemini-2.5-pro"),
    description="Analyzes transaction data to calculate the frequency of approved and rejected transactions for the current payer, vendor involved",
    instruction=TRANSACTION_AGENT_PROMPT,
    tools=[FunctionTool(analyze_transaction_frequency)],
    output_key="transaction_agent",
    after_agent_callback=create_analysis_callback("transaction_analysis", "transaction_agent")  # Store in BigQuery
)

logger.info("Transaction agent initialized successfully")
