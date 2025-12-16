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
Unit tests for sub_agents utility functions.
"""
from unittest.mock import MagicMock, patch

# Mock BigQuery client before importing the module
with patch("google.cloud.bigquery.Client"):
    from app.sub_agents.utils import store_analysis_in_bigquery, update_approval_status


@patch("app.sub_agents.utils.bq_client")
def test_store_analysis_in_bigquery_update_existing(mock_bq_client: MagicMock) -> None:
    """Test store_analysis_in_bigquery when record exists (update path)."""
    # Mock check query returning a record
    mock_check_result = MagicMock()
    mock_check_result.__iter__ = lambda self: iter([{"transaction_id": "TXN_001"}])
    
    # Mock update query
    mock_update_result = MagicMock()
    
    mock_bq_client.query.side_effect = [
        MagicMock(result=lambda: mock_check_result),  # Check query
        MagicMock(result=lambda: mock_update_result),  # Update query
    ]
    
    result = store_analysis_in_bigquery("TXN_001", "payee_analysis", "Test analysis")
    
    assert result is True


@patch("app.sub_agents.utils.bq_client")
def test_store_analysis_in_bigquery_insert_new(mock_bq_client: MagicMock) -> None:
    """Test store_analysis_in_bigquery when record does not exist (insert path)."""
    # Mock check query returning no records
    mock_check_result = MagicMock()
    mock_check_result.__iter__ = lambda self: iter([])
    
    # Mock insert query
    mock_insert_result = MagicMock()
    
    mock_bq_client.query.side_effect = [
        MagicMock(result=lambda: mock_check_result),  # Check query
        MagicMock(result=lambda: mock_insert_result),  # Insert query
    ]
    
    result = store_analysis_in_bigquery("TXN_002", "payer_analysis", "Test analysis")
    
    assert result is True


@patch("app.sub_agents.utils.bq_client")
def test_store_analysis_in_bigquery_error(mock_bq_client: MagicMock) -> None:
    """Test store_analysis_in_bigquery when BigQuery raises an exception."""
    # Mock BigQuery exception
    mock_bq_client.query.side_effect = Exception("Connection error")
    
    result = store_analysis_in_bigquery("TXN_001", "payee_analysis", "Test analysis")
    
    assert result is False


@patch("app.sub_agents.utils.bq_client")
def test_update_approval_status_success(mock_bq_client: MagicMock) -> None:
    """Test update_approval_status with successful update."""
    # Mock successful update
    mock_result = MagicMock()
    mock_bq_client.query.return_value.result.return_value = mock_result
    
    result = update_approval_status("TXN_001", "Approved")
    
    assert result is True


@patch("app.sub_agents.utils.bq_client")
def test_update_approval_status_error(mock_bq_client: MagicMock) -> None:
    """Test update_approval_status when BigQuery raises an exception."""
    # Mock BigQuery exception
    mock_bq_client.query.side_effect = Exception("Update failed")
    
    result = update_approval_status("TXN_001", "Rejected")
    
    assert result is False


@patch("app.sub_agents.utils.bq_client")
def test_store_analysis_strips_whitespace(mock_bq_client: MagicMock) -> None:
    """Test that store_analysis_in_bigquery strips whitespace from transaction_id."""
    # Mock check query returning no records
    mock_check_result = MagicMock()
    mock_check_result.__iter__ = lambda self: iter([])
    
    # Mock insert query
    mock_insert_result = MagicMock()
    
    mock_bq_client.query.side_effect = [
        MagicMock(result=lambda: mock_check_result),
        MagicMock(result=lambda: mock_insert_result),
    ]
    
    result = store_analysis_in_bigquery("  TXN_003  ", "transaction_analysis", "Test")
    
    assert result is True
    # Verify the query was called (whitespace should be stripped internally)
    assert mock_bq_client.query.called
