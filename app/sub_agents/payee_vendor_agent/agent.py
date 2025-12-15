import logging
import os
from typing import Any, Dict, List, Optional
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from app.sub_agents.bigquery_agent.agent import bigquery_agent
from app.sub_agents.payee_vendor_agent.tools import (
    upsert_state,
    get_vendor_for_payee,
    analyze_vendor_patterns,
    identify_suspicious_payers,
    analyze_temporal_patterns,
)
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
    tools=[
        get_vendor_for_payee,
        analyze_vendor_patterns,
        identify_suspicious_payers,
        analyze_temporal_patterns,
        upsert_state,
    ],
    include_contents='none'  # Don't respond to user directly, only write to state
)

logger.info("Payee vendor agent initialized successfully") 
