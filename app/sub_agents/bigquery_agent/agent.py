from google.adk.agents import LlmAgent
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode
import os
import logging
import google.auth
from dotenv import load_dotenv
from google.adk.agents.callback_context import CallbackContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

logger.info("Initializing BigQuery agent...")

toolconfig = BigQueryToolConfig(write_mode = WriteMode.BLOCKED)
credentials,_ = google.auth.default()
credentials_config = BigQueryCredentialsConfig(credentials = credentials)

bigquery_toolset = BigQueryToolset(credentials_config=credentials_config,bigquery_tool_config=toolconfig)

logger.info("BigQuery toolset initialized successfully")

database_settings = None


def setup_before_agent_call(callback_context: CallbackContext) -> None:
    """Setup the agent."""
    logger.info("Setting up BigQuery agent callback...")
    if "database_settings" not in callback_context.state:
        callback_context.state["database_settings"] = (
            get_database_settings()
        )
    logger.info("BigQuery agent callback setup complete")


def get_database_settings():
    """Get database settings."""
    global database_settings
    if database_settings is None:
        database_settings = update_database_settings()
    return database_settings


def update_database_settings():
    """Update database settings."""
    logger.info(f"Updating database settings for project: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
    global database_settings
    database_settings = {
        "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
        "dataset_id": os.getenv("BQ_DATASET_ID"),
    }
    logger.info(f"Database settings updated: project={database_settings['project_id']}, dataset={database_settings['dataset_id']}")
    return database_settings

# BigQuery NL-to-SQL Agent
bigquery_agent = LlmAgent(
    name="bigquery_agent",
    model="gemini-2.0-flash",
    description="Natural language to BigQuery SQL agent that executes queries on transaction data",
    instruction=f"""
    You are a BigQuery SQL expert specialized in payment transaction data analysis.
    
    You have access to a BigQuery table with the following schema:
    
    - The project ID is {os.getenv("GOOGLE_CLOUD_PROJECT")}
    - The dataset ID is {os.getenv("BQ_DATASET_ID")}
    - The table ID is {os.getenv("BQ_TABLE_ID")}: ``
    Columns:
    - transaction_id (STRING): Unique transaction identifier
    - payment_time (TIMESTAMP): When the payment occurred
    - payer_id (STRING): The customer/entity initiating payment
    - payee_id (STRING): The recipient account identifier
    - payment_amount (FLOAT): Transaction amount
    - payment_currency (STRING): Currency code (USD, EUR, GBP, CAD, etc.)
    - payment_method (STRING): Payment method (ACH, Wire Transfer, Check, Bank Transfer, etc.)
    - payment_purpose (STRING): Description of payment purpose
    - vendor_id (STRING): Merchant/business identifier
    - payee_country (STRING): Payee's country
    - vendor_country (STRING): Vendor's country
    - vendor_industry (STRING): Industry classification (Manufacturing, Retail, Logistics, etc.)
    - approval_status (STRING): APPROVED or REJECTED
    - reject_reason (STRING): Reason for rejection if applicable
    
    Your role:
    1. Convert natural language requests into accurate BigQuery SQL queries
    2. Execute the queries and return results in a clear, structured format
    3. Always filter and aggregate appropriately based on the request
    4. Use proper SQL functions for date/time, aggregations, and statistical calculations
    5. Return data in JSON format with clear field names
    
    When asked for transaction data, include ALL relevant columns unless specifically told otherwise.
    When asked for statistics, calculate metrics like AVG, STDDEV, MIN, MAX, COUNT, SUM appropriately.
    When asked about relationships (payer-payee, payer-vendor), group and aggregate properly.
    
    Always parameterize queries for safety when filtering by specific IDs.
    """,
    before_agent_callback= setup_before_agent_call,
    tools=[bigquery_toolset],
    output_key="bigquery_agent",
    include_contents='none'  # Don't respond to user directly, only write to state
)

logger.info("BigQuery agent initialized successfully")