import logging
import os
from typing import Any, Dict, List, Optional
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.agent_tool import AgentTool
from app.sub_agents.bigquery_agent.agent import bigquery_agent
from .prompt import PAYEE_VENDOR_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Payee-Vendor Relationship Analysis Agent
payee_agent = LlmAgent(
    name="payee_vendor_agent",
    model="gemini-2.0-flash",
    description=(
        "Analyzes payee and vendor transaction patterns to identify relationships, "
        "assess transaction consistency, and document behavioral patterns."
    ),
    instruction=PAYEE_VENDOR_PROMPT,
    output_key = "payee_agent",
    tools=[AgentTool(bigquery_agent)],
    include_contents=False  # Don't respond to user directly, only write to state
)

logger.info("Payee vendor agent initialized successfully") 
