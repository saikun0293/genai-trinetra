import logging
from google.adk.agents import LlmAgent
from google.adk.models import Gemini

from .prompt import CRITIQUE_AGENT_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

critic_agent = LlmAgent(
    name="critique_scoring_agent",
    model=Gemini(model="gemini-2.5-pro"),
    instruction=CRITIQUE_AGENT_PROMPT,
    output_key="risk_result",
    input_keys=[
        "payee_agent",
        "payer_validation_agent",
        "geopolitics_agent",
        "transaction_agent"
    ]
)

logger.info("Critique scoring agent initialized successfully")
