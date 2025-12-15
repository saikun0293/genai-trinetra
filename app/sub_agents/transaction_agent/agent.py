from collections import defaultdict
import logging
import os
from google.adk.apps.app import App
from google.adk.agents import LlmAgent
from google.cloud import bigquery
from google.adk.tools import FunctionTool
from .prompt import TRANSACTION_AGENT_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the BigQuery client once to be reused.
bq_client = bigquery.Client()

# --- TODO: Replace this with your actual BigQuery table ID ---
BQ_TABLE_ID = "ccibt-hack25ww7-714.tri_netra_payments.PaymentsCompliance"


def analyze_transaction_frequency() -> dict:
    """
    Performs frequency analysis on a predefined transaction data table.
    This tool queries the table, counts 'approved' and 'rejected' transactions
    for each payer-vendor pair, and returns a summary.

    Returns:
        A dictionary containing the frequency map of transactions.
    """
    try:
        query = f"SELECT payer_id, vendor_id, approval_status FROM `{BQ_TABLE_ID}`"
        transactions = bq_client.query(query).result()
        freq_map = defaultdict(lambda: {"approved": 0, "rejected": 0, "total_transcations": 0})

        for tx in transactions:
            key = (tx["payer_id"], tx["vendor_id"])
            status = tx.get("approval_status", "unknown").lower()

            freq_map[key]["total_transcations"] += 1
            if status == "approved":
                freq_map[key]["approved"] += 1
            elif status == "rejected":
                freq_map[key]["rejected"] += 1
        # Convert tuple keys to strings for JSON compatibility
        string_key_map = {f"{k[0]}-{k[1]}": v for k, v in freq_map.items()}
        return {"frequency_map": string_key_map}
    except Exception as e:
        logger.error(f"An error occurred during BigQuery processing: {e}", exc_info=True)
        return {"error": "An error occurred while analyzing transaction data."}



transaction_agent = LlmAgent(
    name="transaction_agent",
    # Provide a default model to prevent errors if the env var is not set.
    model=os.environ.get("ADK_MODEL", "gemini-2.5-pro"),
    description="Analyzes transaction data to calculate the frequency of approved and rejected transactions.",
    instruction=TRANSACTION_AGENT_PROMPT,
    tools=[FunctionTool(analyze_transaction_frequency)],
    output_key="transaction_agent",
    include_contents='none'  # Don't respond to user directly, only write to state
)

logger.info("Transaction agent initialized successfully")

