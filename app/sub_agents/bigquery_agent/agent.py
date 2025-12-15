from google.adk.agents import Agent
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode
import os
import google.auth
from dotenv import load_dotenv
from google.adk.agents.callback_context import CallbackContext

load_dotenv()
database_settings = None

toolconfig = BigQueryToolConfig(write_mode = WriteMode.BLOCKED)
credentials,_ = google.auth.default()
credentials_config = BigQueryCredentialsConfig(credentials = credentials)

bigquery_toolset = BigQueryToolset(credentials_config=credentials_config,bigquery_tool_config=toolconfig)

def setup_before_agent_call(callback_context: CallbackContext) -> None:
    """Setup the agent."""

    if "database_settings" not in callback_context.state:
        callback_context.state["database_settings"] = (
            get_database_settings()
        )


def get_database_settings():
    """Get database settings."""
    global database_settings
    if database_settings is None:
        database_settings = update_database_settings()
    return database_settings


def update_database_settings():
    """Update database settings."""
    global database_settings
    print("Updating database settings...",os.getenv("GOOGLE_CLOUD_PROJECT"))
    database_settings = {
        "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
        "dataset_id": os.getenv("BQ_DATASET_ID"),
    }
    return database_settings

bigquery_agent = Agent(
    name="BQL_Agent",
    model=os.getenv("MODEL"),
    description=(
        "Retrieves transaction data from BigQuery by translating "
        "natural language requests into safe, read-only BigQuery SQL queries."
    ),
    instruction="""
    You are a BigQuery data retrieval agent.

    Your responsibility is to:
    - Translate natural language data requests into safe, read-only BigQuery SQL queries.
    - Only use SELECT statements.
    - Only query the tables you are allowed to access.
    - Return structured results

    You must NEVER:
    - Modify data
    - Use non-SELECT statements
    - Assume schema beyond what is provided

    Note the following details -
    projectID - ccibt-hack25ww7-714
    dataSetId - ccibt-hack25ww7-714.tri_netra_payments
    tableName - PaymentsCompliance
""",
    before_agent_callback=setup_before_agent_call,
    tools=[bigquery_toolset]
)