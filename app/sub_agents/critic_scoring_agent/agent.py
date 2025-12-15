from google.adk.agents import LlmAgent
from google.adk.models import Gemini

from .prompt import CRITIC_PROMPT

critic_agent = LlmAgent(
    name="critic_scoring_agent",
    model=Gemini(model="gemini-2.5-pro"),
    instruction=CRITIC_PROMPT,
    output_key="risk_result",
    input_keys=[
        "payer_markdown",
        "payee_markdown",
        "compliance_markdown",
        "transaction_counts"
    ]
)
