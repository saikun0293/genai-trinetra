import logging
from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext
from .tools import (
    get_payer_baseline,
    get_recent_transactions,
    analyze_velocity_patterns,
    identify_anomalies,
    analyze_rejection_patterns,
    upsert_state,
)
from .prompt import PAYER_VALIDATION_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Main Payer Validation Agent with hardcoded SQL query tools
payer_validation_agent = LlmAgent(
    name="payer_validation_agent",
    model="gemini-2.0-flash",
    description="Banking fraud detection agent specialized in payer transaction anomaly detection",
    instruction=PAYER_VALIDATION_PROMPT,
    output_key="payer_validation_agent",
    tools=[
        get_payer_baseline,
        get_recent_transactions,
        analyze_velocity_patterns,
        identify_anomalies,
        analyze_rejection_patterns,
        upsert_state
    ],
    include_contents='none'  # Don't respond to user directly, only write to state
)

logger.info("Payer validation agent initialized successfully")