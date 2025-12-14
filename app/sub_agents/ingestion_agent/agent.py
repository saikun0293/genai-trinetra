from google.adk.agents.llm_agent import Agent
from .prompt import INGESTION_AGENT_PROMPT

root_agent = Agent(
    model='gemini-2.5-flash',
    name='ingestion_agent',
    description='A helpful assistant for user questions.',
    instruction=INGESTION_AGENT_PROMPT,
)
