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


def get_vendor_for_payee(payee_id: str) -> Dict[str, Any]:
    """Get vendors associated with a payee and their transaction stats."""
    query = f"""
    SELECT
      vendor_id,
      vendor_industry,
      COUNT(*) as transaction_count,
      SUM(payment_amount) as total_amount_received,
      COUNT(DISTINCT payer_id) as unique_payers
    FROM `{BQ_TABLE_ID}`
    WHERE payee_id = @payee_id
    GROUP BY vendor_id, vendor_industry
    ORDER BY transaction_count DESC
    LIMIT 5
    """
    try:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("payee_id", "STRING", payee_id)
            ]
        )
        results = bq_client.query(query, job_config=job_config).result()
        vendors = [dict(row) for row in results]
        logger.info(f"Found {len(vendors)} vendors for payee {payee_id}")
        return {"vendors": vendors, "payee_id": payee_id}
    except Exception as e:
        logger.error(f"Error querying vendors for payee {payee_id}: {e}")
        return {"error": str(e), "payee_id": payee_id}


def analyze_vendor_patterns(vendor_id: str) -> Dict[str, Any]:
    """Analyze payment patterns for a vendor: baseline metrics and anomalies."""
    query = f"""
    WITH vendor_stats AS (
      SELECT
        COUNT(*) as total_transactions,
        SUM(payment_amount) as total_received,
        AVG(payment_amount) as avg_amount,
        STDDEV_POP(payment_amount) as stddev_amount,
        MIN(payment_amount) as min_amount,
        MAX(payment_amount) as max_amount,
        COUNT(DISTINCT payer_id) as unique_payers,
        COUNTIF(approval_status = 'APPROVED') as approved_count,
        COUNTIF(approval_status = 'REJECTED') as rejected_count
      FROM `{BQ_TABLE_ID}`
      WHERE vendor_id = @vendor_id
    ),
    high_value_txns AS (
      SELECT COUNT(*) as high_value_count
      FROM `{BQ_TABLE_ID}`
      WHERE vendor_id = @vendor_id AND payment_amount > 10000
    ),
    structured_amounts AS (
      SELECT COUNT(*) as structured_count
      FROM `{BQ_TABLE_ID}`
      WHERE vendor_id = @vendor_id
        AND (payment_amount BETWEEN 9900 AND 9999
          OR payment_amount BETWEEN 49900 AND 49999
          OR payment_amount BETWEEN 99900 AND 99999)
    )
    SELECT
      vs.total_transactions,
      ROUND(vs.total_received, 2) as total_received,
      ROUND(vs.avg_amount, 2) as avg_amount,
      ROUND(vs.stddev_amount, 2) as stddev_amount,
      ROUND(vs.min_amount, 2) as min_amount,
      ROUND(vs.max_amount, 2) as max_amount,
      vs.unique_payers,
      vs.approved_count,
      vs.rejected_count,
      hv.high_value_count,
      sa.structured_count
    FROM vendor_stats vs, high_value_txns hv, structured_amounts sa
    """
    try:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("vendor_id", "STRING", vendor_id)
            ]
        )
        results = list(bq_client.query(query, job_config=job_config).result())
        pattern = dict(results[0]) if results else {}
        logger.info(f"Analyzed patterns for vendor {vendor_id}")
        return {"vendor_id": vendor_id, "patterns": pattern}
    except Exception as e:
        logger.error(f"Error analyzing vendor patterns: {e}")
        return {"error": str(e), "vendor_id": vendor_id}


def identify_suspicious_payers(vendor_id: str) -> Dict[str, Any]:
    """Identify payers with suspicious activity patterns to this vendor."""
    query = f"""
    SELECT
      payer_id,
      COUNT(*) as transaction_count,
      SUM(payment_amount) as total_to_vendor,
      AVG(payment_amount) as avg_amount,
      COUNTIF(approval_status = 'REJECTED') as rejection_count,
      COUNTIF(payment_amount > 10000) as high_value_count
    FROM `{BQ_TABLE_ID}`
    WHERE vendor_id = @vendor_id
    GROUP BY payer_id
    HAVING rejection_count > 0 OR high_value_count > 0 OR transaction_count > 5
    ORDER BY transaction_count DESC
    LIMIT 20
    """
    try:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("vendor_id", "STRING", vendor_id)
            ]
        )
        results = bq_client.query(query, job_config=job_config).result()
        suspicious_payers = [dict(row) for row in results]
        logger.info(f"Found {len(suspicious_payers)} suspicious payers for vendor {vendor_id}")
        return {"vendor_id": vendor_id, "suspicious_payers": suspicious_payers}
    except Exception as e:
        logger.error(f"Error identifying suspicious payers: {e}")
        return {"error": str(e), "vendor_id": vendor_id}


def analyze_temporal_patterns(vendor_id: str) -> Dict[str, Any]:
    """Analyze temporal and frequency patterns for a vendor."""
    query = f"""
    SELECT
      CAST(payment_time AS STRING) as time_period,
      COUNT(*) as transaction_count,
      AVG(payment_amount) as avg_amount,
      COUNTIF(approval_status = 'REJECTED') as rejected_count
    FROM `{BQ_TABLE_ID}`
    WHERE vendor_id = @vendor_id
    GROUP BY time_period
    ORDER BY transaction_count DESC
    """
    try:
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("vendor_id", "STRING", vendor_id)
            ]
        )
        results = bq_client.query(query, job_config=job_config).result()
        temporal_patterns = [dict(row) for row in results]
        logger.info(f"Analyzed temporal patterns for vendor {vendor_id}")
        return {"vendor_id": vendor_id, "temporal_patterns": temporal_patterns}
    except Exception as e:
        logger.error(f"Error analyzing temporal patterns: {e}")
        return {"error": str(e), "vendor_id": vendor_id}
