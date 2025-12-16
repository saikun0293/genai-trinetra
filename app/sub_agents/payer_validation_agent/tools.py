import logging
from typing import Any, Dict
from google.adk.tools.tool_context import ToolContext
from google.cloud import bigquery

logger = logging.getLogger(__name__)
bq_client = bigquery.Client()

# Table ID from environment
BQ_TABLE_ID = "ccibt-hack25ww7-714.tri_netra_payments.PaymentsCompliance"


def upsert_state(tool_context: ToolContext, key: str, value: Any) -> Dict[str, Any]:
    """Write or overwrite a session state entry.

    Args:
        tool_context: ADK tool context containing session state
        key: target session state key
        value: payload to store

    Returns:
        Dict summarizing the operation.
    """
    state = tool_context.state
    existed = key in state
    state[key] = value

    logger.info("Session state %s for key=%s", "updated" if existed else "created", key)

    return {
        "status": "updated" if existed else "created",
        "key": key,
        "value_preview": str(value)[:500],
    }


def get_payer_baseline(payer_id: str) -> Dict[str, Any]:
    """Get baseline transaction metrics for a payer."""
    query = f"""
    SELECT
      COUNT(*) as total_transactions,
      AVG(payment_amount) as avg_amount,
      STDDEV_POP(payment_amount) as stddev_amount,
      MIN(payment_amount) as min_amount,
      MAX(payment_amount) as max_amount,
      COUNT(DISTINCT payee_id) as unique_payees,
      COUNT(DISTINCT vendor_id) as unique_vendors,
      COUNT(DISTINCT payment_method) as unique_methods,
      COUNTIF(approval_status = 'APPROVED') as approved_count,
      COUNTIF(approval_status = 'REJECTED') as rejected_count
    FROM `{BQ_TABLE_ID}`
    WHERE payer_id = @payer_id
    """
    try:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("payer_id", "STRING", payer_id)
            ]
        )
        results = list(bq_client.query(query, job_config=job_config).result())
        baseline = dict(results[0]) if results else {}
        logger.info(f"Got baseline metrics for payer {payer_id}")
        return {"payer_id": payer_id, "baseline": baseline}
    except Exception as e:
        logger.error(f"Error getting payer baseline: {e}")
        return {"error": str(e), "payer_id": payer_id}


def get_recent_transactions(payer_id: str, days: int = 90) -> Dict[str, Any]:
    """Get recent transaction history for a payer.
    
    Note: payment_time column contains time-only values (HH:MM.S format),
    not full timestamps, so date-range filtering is not applicable.
    """
    query = f"""
    SELECT
      transaction_id,
      payment_time,
      payee_id,
      payment_amount,
      payment_currency,
      payment_method,
      payment_purpose,
      vendor_id,
      vendor_industry,
      approval_status
    FROM `{BQ_TABLE_ID}`
    WHERE payer_id = @payer_id
    ORDER BY payment_time DESC
    LIMIT 500
    """
    try:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("payer_id", "STRING", payer_id)
            ]
        )
        results = bq_client.query(query, job_config=job_config).result()
        transactions = [dict(row) for row in results]
        logger.info(f"Got {len(transactions)} recent transactions for payer {payer_id}")
        return {"payer_id": payer_id, "transaction_count": len(transactions), "transactions": transactions}
    except Exception as e:
        logger.error(f"Error getting recent transactions: {e}")
        return {"error": str(e), "payer_id": payer_id}


def analyze_velocity_patterns(payer_id: str) -> Dict[str, Any]:
    """Analyze transaction velocity and frequency patterns."""
    query = f"""
    SELECT
      CAST(payment_time AS STRING) as time_period,
      COUNT(*) as transaction_count,
      SUM(payment_amount) as total_amount,
      AVG(payment_amount) as avg_amount
    FROM `{BQ_TABLE_ID}`
    WHERE payer_id = @payer_id
    GROUP BY time_period
    ORDER BY transaction_count DESC
    LIMIT 30
    """
    try:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("payer_id", "STRING", payer_id)
            ]
        )
        results = bq_client.query(query, job_config=job_config).result()
        patterns = [dict(row) for row in results]
        logger.info(f"Analyzed velocity patterns for payer {payer_id}")
        return {"payer_id": payer_id, "velocity_patterns": patterns}
    except Exception as e:
        logger.error(f"Error analyzing velocity: {e}")
        return {"error": str(e), "payer_id": payer_id}


def identify_anomalies(payer_id: str) -> Dict[str, Any]:
    """Identify behavioral anomalies for a payer."""
    query = f"""
    WITH payer_stats AS (
      SELECT
        AVG(payment_amount) as avg_amount,
        STDDEV_POP(payment_amount) as stddev_amount
      FROM `{BQ_TABLE_ID}`
      WHERE payer_id = @payer_id
    )
    SELECT
      transaction_id,
      payment_time,
      payee_id,
      payment_amount,
      approval_status,
      CASE 
        WHEN payment_amount > (ps.avg_amount + 3 * ps.stddev_amount) THEN 'Extreme Outlier'
        WHEN payment_amount > (ps.avg_amount + 2 * ps.stddev_amount) THEN 'High Outlier'
        ELSE 'Normal'
      END as anomaly_type
    FROM `{BQ_TABLE_ID}`, payer_stats ps
    WHERE payer_id = @payer_id
      AND (
        payment_amount > (ps.avg_amount + 2 * ps.stddev_amount)
        OR approval_status = 'REJECTED'
        OR payment_amount BETWEEN 9900 AND 9999
        OR payment_amount BETWEEN 49900 AND 49999
      )
    ORDER BY payment_time DESC
    LIMIT 50
    """
    try:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("payer_id", "STRING", payer_id)
            ]
        )
        results = bq_client.query(query, job_config=job_config).result()
        anomalies = [dict(row) for row in results]
        logger.info(f"Identified {len(anomalies)} anomalies for payer {payer_id}")
        return {"payer_id": payer_id, "anomalies": anomalies}
    except Exception as e:
        logger.error(f"Error identifying anomalies: {e}")
        return {"error": str(e), "payer_id": payer_id}


def analyze_rejection_patterns(payer_id: str) -> Dict[str, Any]:
    """Analyze rejection and approval patterns for a payer."""
    query = f"""
    SELECT
      approval_status,
      COUNT(*) as count,
      AVG(payment_amount) as avg_amount,
      MIN(payment_amount) as min_amount,
      MAX(payment_amount) as max_amount
    FROM `{BQ_TABLE_ID}`
    WHERE payer_id = @payer_id
    GROUP BY approval_status
    """
    try:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("payer_id", "STRING", payer_id)
            ]
        )
        results = bq_client.query(query, job_config=job_config).result()
        patterns = [dict(row) for row in results]
        logger.info(f"Analyzed rejection patterns for payer {payer_id}")
        return {"payer_id": payer_id, "approval_patterns": patterns}
    except Exception as e:
        logger.error(f"Error analyzing rejection patterns: {e}")
        return {"error": str(e), "payer_id": payer_id}
