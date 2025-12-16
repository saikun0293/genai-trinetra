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
Unit tests for prompt templates.
"""
from unittest.mock import MagicMock, patch

# Mock BigQuery and auth before importing
with patch("google.cloud.bigquery.Client"), patch("google.auth.default", return_value=(None, "test-project")):
    from app.prompt import ROOT_ORCHESTRATOR_PROMPT, TRANSACTION_AGENT_PROMPT


def test_root_orchestrator_prompt_exists() -> None:
    """Test that ROOT_ORCHESTRATOR_PROMPT is defined and not empty."""
    assert ROOT_ORCHESTRATOR_PROMPT is not None
    assert len(ROOT_ORCHESTRATOR_PROMPT) > 0
    assert isinstance(ROOT_ORCHESTRATOR_PROMPT, str)


def test_root_orchestrator_prompt_contains_key_instructions() -> None:
    """Test that ROOT_ORCHESTRATOR_PROMPT contains key instructions."""
    # Check for important keywords that should be in the orchestrator prompt
    assert "transaction_id" in ROOT_ORCHESTRATOR_PROMPT
    assert "parallel" in ROOT_ORCHESTRATOR_PROMPT.lower()
    assert "BigQuery" in ROOT_ORCHESTRATOR_PROMPT or "bigquery" in ROOT_ORCHESTRATOR_PROMPT.lower()


def test_transaction_agent_prompt_exists() -> None:
    """Test that TRANSACTION_AGENT_PROMPT is defined and not empty."""
    assert TRANSACTION_AGENT_PROMPT is not None
    assert len(TRANSACTION_AGENT_PROMPT) > 0
    assert isinstance(TRANSACTION_AGENT_PROMPT, str)


def test_transaction_agent_prompt_contains_key_instructions() -> None:
    """Test that TRANSACTION_AGENT_PROMPT contains key instructions."""
    # Check for important keywords that should be in the transaction agent prompt
    assert "transaction_id" in TRANSACTION_AGENT_PROMPT or "transaction ID" in TRANSACTION_AGENT_PROMPT
    assert "extract" in TRANSACTION_AGENT_PROMPT.lower()

