
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from app.sub_agents.bigquery_agent import bigquery_agent

payee_agent = LlmAgent(
    name='payee_agent',
    model='gemini-2.5-pro',
    instruction="""You are a payee analyst.
Your goal is to provide a summary of the payee's payment history based on the `payee_id`.
You will use the bigquery_agent tool to query the database to get all the data for the given `payee_id`.
The data you will receive is:
- payment_time
- payer_id
- payee_id
- payment_amount
- payment_currency
- payment_method
- payment_purpose
- vendor_id
- payee_country
- vendor_country
- vendor_industry


""",
    tools=[AgentTool(bigquery_agent)],
)
