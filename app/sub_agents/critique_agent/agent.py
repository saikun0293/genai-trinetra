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
from google.adk.agents import LlmAgent
from google.adk.models import Gemini

from .prompt import CRITIQUE_AGENT_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# critique scoring agent:
# - Relies strictly on upstream agent outputs
# - Does NOT assume, infer, or hallucinate missing information
# - Explicitly treats unknown or undefined data as UNKNOWN
critique_agent = LlmAgent(
    name="critique_scoring_agent",
    model=Gemini(model="gemini-2.5-pro"),
    instruction=CRITIQUE_AGENT_PROMPT,

    # Single canonical output state for downstream consumers
    output_key="risk_assessment_state",

)

logger.info("critique scoring agent initialized successfully")
