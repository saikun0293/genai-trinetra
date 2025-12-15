import logging
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from app.sub_agents.bigquery_agent import bigquery_agent
from .prompt import PAYER_VALIDATION_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Main Payer Anomaly Detection Agent
payer_validation_agent = LlmAgent(
    name="payer_validation_agent",
    model="gemini-2.0-flash",
    description="Banking fraud detection agent specialized in payer transaction anomaly detection",
    instruction=PAYER_VALIDATION_PROMPT,
    output_key="payer_validation_agent",
    tools=[
        AgentTool(bigquery_agent, skip_summarization=False)
    ],
    include_contents=False  # Don't respond to user directly, only write to state
)

logger.info("Payer validation agent initialized successfully")