"""
BigQuery service for querying transaction compliance analysis data.
"""

import logging
from typing import Optional, Dict, Any
from google.cloud import bigquery
import os

logger = logging.getLogger(__name__)

# BigQuery configuration
PROJECT_ID = "ccibt-hack25ww7-714"
DATASET_ID = "tri_netra_payments"
TABLE_ID = "TransactionAnalysis"
FULL_TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"


def get_transaction_analysis(transaction_id: str) -> Optional[Dict[str, Any]]:
    """
    Query BigQuery for analysis data for a specific transaction.
    
    Args:
        transaction_id: The transaction ID to query
        
    Returns:
        Dictionary containing analysis data or None if not found
    """
    try:
        client = bigquery.Client(project=PROJECT_ID)
        
        query = f"""
        SELECT 
            transaction_id,
            payee_analysis,
            payer_analysis,
            geopolitical_analysis,
            transaction_analysis,
            critic_analysis
        FROM `{FULL_TABLE_ID}`
        WHERE transaction_id = @transaction_id
        LIMIT 1
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("transaction_id", "STRING", transaction_id)
            ]
        )
        
        logger.info(f"Querying BigQuery table {FULL_TABLE_ID} for transaction_id: {transaction_id}")
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        # Convert to dictionary
        row_count = 0
        for row in results:
            row_count += 1
            analysis_data = {
                "transaction_id": row.transaction_id,
                "payee_analysis": row.payee_analysis,
                "payer_analysis": row.payer_analysis,
                "geopolitical_analysis": row.geopolitical_analysis,
                "transaction_analysis": row.transaction_analysis,
                "critic_analysis": row.critic_analysis
            }
            logger.info(f"Found analysis for transaction {transaction_id}: payee={bool(row.payee_analysis)}, payer={bool(row.payer_analysis)}, geo={bool(row.geopolitical_analysis)}, txn={bool(row.transaction_analysis)}, critic={bool(row.critic_analysis)}")
            return analysis_data
        
        logger.warning(f"No rows found for transaction {transaction_id} in table {FULL_TABLE_ID}. Total rows returned: {row_count}")
        
        # Log a sample query to help debug
        sample_query = f"SELECT transaction_id FROM `{FULL_TABLE_ID}` LIMIT 5"
        sample_job = client.query(sample_query)
        sample_results = list(sample_job.result())
        logger.info(f"Sample transaction IDs in table: {[r.transaction_id for r in sample_results[:5]]}")
        
        return None
        
    except Exception as e:
        logger.error(f"Error querying BigQuery for transaction {transaction_id}: {e}", exc_info=True)
        return None
