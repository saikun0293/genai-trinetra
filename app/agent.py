# ruff: noqa
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Main agent module for the compliance orchestrator.
This module defines the root agent that coordinates parallel compliance analysis.
"""

import logging
import os
import google.auth
from google.adk.apps.app import App
from google.adk.agents import ParallelAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from app.sub_agents.geopolitics_agent import geopolitics_agent
from app.sub_agents.payee_vendor_agent import payee_agent
from app.sub_agents.payer_validation_agent import payer_validation_agent
from app.sub_agents.transaction_agent import transaction_agent
from app.sub_agents.critique_agent import critique_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Google Cloud authentication and environment
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT", project_id)
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

logger.info(f"Compliance orchestrator initialized with project: {project_id}, location: {os.environ['GOOGLE_CLOUD_LOCATION']}")


def log_agent_outputs(callback_context: CallbackContext) -> None:
    """Log session state after parallel agents complete to verify outputs are stored."""
    logger.info("=" * 80)
    logger.info("COMPLIANCE ANALYZER - Session State After Parallel Execution")
    logger.info("=" * 80)
    
    state = callback_context.session.state
    agent_keys = ["payee_agent", "payer_validation_agent", "geopolitics_agent", "transaction_agent"]
    
    for key in agent_keys:
        if key in state:
            output_preview = str(state[key])[:200] if state[key] else "None"
            logger.info(f"✓ {key}: Present ({len(str(state[key]))} chars) - {output_preview}...")
        else:
            logger.warning(f"✗ {key}: MISSING from session state")
    
    logger.info("=" * 80)


# Parallel agent that runs all compliance analysis agents concurrently
compliance_analyzer = ParallelAgent(
    name="compliance_analyzer",
    description="Runs multiple compliance analysis agents in parallel to assess different aspects of a transaction simultaneously.",
    sub_agents=[payee_agent, payer_validation_agent, geopolitics_agent, transaction_agent],   
)

logger.info("Compliance analyzer (parallel agent) initialized successfully")

# Root agent that orchestrates the entire compliance workflow
root_agent = SequentialAgent(
    name="compliance_orchestrator",
    description="Orchestrates the end-to-end compliance check by running analysis agents in parallel, then synthesizing with a critique agent.",
    sub_agents=[compliance_analyzer, critique_agent]
)

logger.info("Root agent (compliance orchestrator) initialized successfully")

# Create the App instance - this is what gets loaded by ADK and deployed
app = App(
    name="app",
    root_agent=root_agent
)

logger.info("Compliance application initialized successfully")
