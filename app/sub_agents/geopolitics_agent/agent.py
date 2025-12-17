import logging
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search
from app.sub_agents.utils import create_analysis_callback
from app.sub_agents.thinking_callbacks import create_thinking_callback
from .prompt import GEOPOLITICS_AGENT_PROMPT

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
) 

logger = logging.getLogger(__name__)

geopolitics_agent = LlmAgent(
    model='gemini-2.5-pro',
    name='geopolitics_agent',
    description='Analyzes transaction compliance based on geopolitical factors, payment methods, timing, and purpose using real-time information.',
    instruction=GEOPOLITICS_AGENT_PROMPT,
    tools=[google_search],
    output_key='geopolitics_agent',
    before_agent_callback=create_thinking_callback("Geopolitics Agent", "Analyzing geopolitical factors, sanctions, and compliance risks..."),
    after_agent_callback=create_analysis_callback("geopolitical_analysis", "geopolitics_agent")  # Store in BigQuery
)

logger.info("Geopolitics compliance agent initialized successfully")
