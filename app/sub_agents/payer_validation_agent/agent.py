import logging
from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext
from .tools import (
    get_payer_baseline,
    get_recent_transactions,
    analyze_velocity_patterns,
    identify_anomalies,
    analyze_rejection_patterns,
)
from app.sub_agents.utils import create_analysis_callback
from app.sub_agents.thinking_callbacks import create_thinking_callback
from .prompt import PAYER_VALIDATION_PROMPT

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
) 

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
    ],
    before_agent_callback=create_thinking_callback("Payer Agent", "Analyzing payer behavior patterns and transaction anomalies..."),
    after_agent_callback=create_analysis_callback("payer_analysis", "payer_validation_agent")  # Store in BigQuery
)

logger.info("Payer validation agent initialized successfully")