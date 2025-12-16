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
Unit tests for tools module.
"""
from unittest.mock import MagicMock, patch

# Mock BigQuery client before importing the module
with patch("google.cloud.bigquery.Client"):
    from app.tools import fetch_transaction_by_id


@patch("app.tools.bq_client")
def test_fetch_transaction_by_id_found(mock_bq_client: MagicMock) -> None:
    """Test fetch_transaction_by_id when transaction is found."""
    # Mock BigQuery response
    mock_row = {
        "transaction_id": "TXN_001",
        "payer_id": "PAYER_123",
        "payee_id": "PAYEE_456",
        "payment_amount": 1000.0,
        "payment_currency": "USD",
    }
    mock_result = MagicMock()
    mock_result.__iter__ = lambda self: iter([mock_row])
    mock_bq_client.query.return_value.result.return_value = mock_result

    result = fetch_transaction_by_id("TXN_001")

    assert result["found"] is True
    assert "transaction" in result
    assert result["transaction"]["transaction_id"] == "TXN_001"


@patch("app.tools.bq_client")
def test_fetch_transaction_by_id_not_found(mock_bq_client: MagicMock) -> None:
    """Test fetch_transaction_by_id when transaction is not found."""
    # Mock empty BigQuery response
    mock_result = MagicMock()
    mock_result.__iter__ = lambda self: iter([])
    mock_bq_client.query.return_value.result.return_value = mock_result

    result = fetch_transaction_by_id("NONEXISTENT")

    assert result["found"] is False
    assert result["transaction_id"] == "NONEXISTENT"
    assert "error" in result


@patch("app.tools.bq_client")
def test_fetch_transaction_by_id_error(mock_bq_client: MagicMock) -> None:
    """Test fetch_transaction_by_id when BigQuery raises an exception."""
    # Mock BigQuery exception
    mock_bq_client.query.side_effect = Exception("Connection error")

    result = fetch_transaction_by_id("TXN_001")

    assert result["found"] is False
    assert result["transaction_id"] == "TXN_001"
    assert "error" in result
    assert "Connection error" in result["error"]
