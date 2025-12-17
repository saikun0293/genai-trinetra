import logging
import os
from typing import Any, Dict, List, Optional
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from app.sub_agents.bigquery_agent.agent import bigquery_agent
from app.sub_agents.payee_vendor_agent.tools import (
    get_vendor_for_payee,
    analyze_vendor_patterns,
    identify_suspicious_payers,
    analyze_temporal_patterns,
)
from app.sub_agents.utils import create_analysis_callback
from app.sub_agents.thinking_callbacks import create_thinking_callback
from .prompt import PAYEE_VENDOR_PROMPT

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
) 
logger = logging.getLogger(__name__)

# Payee-Vendor Relationship Analysis Agent
payee_agent = LlmAgent(
    name="payee_agent",
    model="gemini-2.0-flash",
    description=(
        "Analyzes payee and vendor transaction patterns to identify relationships, "
        "assess transaction consistency, and document behavioral patterns."
    ),
    instruction=PAYEE_VENDOR_PROMPT,
    output_key = "payee_agent",
    tools=[
        get_vendor_for_payee,
        analyze_vendor_patterns,
        identify_suspicious_payers,
        analyze_temporal_patterns,
    ],
    before_agent_callback=create_thinking_callback("Payee Agent", "Analyzing payee-vendor relationships and transaction patterns..."),
    after_agent_callback=create_analysis_callback("payee_analysis", "payee_agent")
)

logger.info("Payee vendor agent initialized successfully") 
