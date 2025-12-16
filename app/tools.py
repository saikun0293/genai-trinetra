"""Shared tools for the root orchestrator."""

import logging
from typing import Any, Dict

from google.cloud import bigquery

logger = logging.getLogger(__name__)

BQ_TABLE_ID = "ccibt-hack25ww7-714.tri_netra_payments.PaymentsCompliance"

# Initialize BigQuery client once
bq_client = bigquery.Client()


def fetch_transaction_by_id(transaction_id: str) -> Dict[str, Any]:
    """Fetch a single transaction by transaction_id from BigQuery.

    Args:
        transaction_id: Unique transaction identifier.

    Returns:
        A dict with transaction fields or an error payload if not found.
    """
    query = f"""
    SELECT *
    FROM `{BQ_TABLE_ID}`
    WHERE transaction_id = @transaction_id
    LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("transaction_id", "STRING", transaction_id)
        ]
    )
    try:
        results = list(bq_client.query(query, job_config=job_config).result())
        if not results:
            logger.warning("Transaction %s not found", transaction_id)
            return {"found": False, "transaction_id": transaction_id, "error": "Not found"}

        row = dict(results[0])
        # Normalize any datetime types to strings for safe serialization
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()

        logger.info("Fetched transaction %s", transaction_id)
        return {"found": True, "transaction": row}
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Error fetching transaction %s: %s", transaction_id, exc)
        return {"found": False, "transaction_id": transaction_id, "error": str(exc)}
