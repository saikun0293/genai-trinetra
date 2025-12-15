import logging
from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from .prompt import GEOPOLITICS_AGENT_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

geopolitics_agent = Agent(
    model='gemini-2.5-pro',
    name='geopolitics_agent',
    description='Analyzes transaction compliance based on geopolitical factors, payment methods, timing, and purpose using real-time information.',
    instruction=GEOPOLITICS_AGENT_PROMPT,
    tools=[google_search],
    output_key='geopolitics_agent'
)

logger.info("Geopolitics compliance agent initialized successfully")
