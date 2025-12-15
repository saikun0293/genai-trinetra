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
from google.adk.agents import Agent
from .prompt import CRITIQUE_AGENT_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

critique_agent = Agent(
    name="critique_agent",
    model="gemini-2.5-pro",  # Use the most capable model for synthesis
    description=(
        "Synthesizes findings from all compliance agents to provide a comprehensive "
        "risk assessment and decision recommendation for transactions."
    ),
    instruction=CRITIQUE_AGENT_PROMPT,
    output_key="compliance_critique"
)

logger.info("Critique agent initialized successfully")
