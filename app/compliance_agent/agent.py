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

import logging
import os
import google.auth
from google.adk.agents import ParallelAgent, SequentialAgent
from google.adk.apps.app import App
from app.sub_agents.geopolitics_agent import geopolitics_agent
from app.sub_agents.payee_vendor_agent import payee_agent
from app.sub_agents.payer_validation_agent import payer_validation_agent
from app.sub_agents.transaction_agent import transaction_agent


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Google Cloud authentication and environment
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT", project_id)
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

logger.info(f"Initialized with project: {project_id}, location: {os.environ['GOOGLE_CLOUD_LOCATION']}")

compliance_analyzer = ParallelAgent(
    name="compliance_analyzer",
    description="Runs multiple compliance analysis agents in parallel to assess different aspects of a transaction simultaneously.",
    sub_agents=[payee_agent, payer_validation_agent, geopolitics_agent, transaction_agent],   
    max_iterations=1
)

root_agent = SequentialAgent(
    name="compliance_orchestrator",
    description="Orchestrates the end-to-end compliance check by running analysis agents in a predefined sequence.",
    sub_agents=[compliance_analyzer]
)
