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
Main agent module for the ADK agent starter pack.
This module re-exports the compliance agent as the primary app.
"""

import logging
from google.adk.apps.app import App
from app.compliance_agent.agent import root_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the App instance - this is what gets loaded by ADK and deployed
app = App(
    name="app",
    root_agent=root_agent
)

logger.info("Agent application initialized successfully")
