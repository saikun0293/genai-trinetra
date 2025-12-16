"""Common utilities for sub-agents."""

import logging
import os
import re
import json
from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.cloud import bigquery
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

# Initialize BigQuery client
bq_client = bigquery.Client()
BQ_ANALYSIS_TABLE_ID = "ccibt-hack25ww7-714.tri_netra_payments.TransactionAnalysis"
BQ_COMPLIANCE_TABLE_ID = "ccibt-hack25ww7-714.tri_netra_payments.PaymentsCompliance"

def store_analysis_in_bigquery(
    transaction_id: str,
    column_name: str,
    analysis_text: str
) -> bool:
    """
    Store agent analysis in BigQuery table.
    
    Args:
        transaction_id: The transaction ID to update
        column_name: The column to update (payee_analysis, payer_analysis, etc.)
        analysis_text: The analysis text to store
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Strip whitespace from transaction_id
        transaction_id = transaction_id.strip()
        
        # Check if record exists
        check_query = f"""
            SELECT transaction_id 
            FROM `{BQ_ANALYSIS_TABLE_ID}` 
            WHERE transaction_id = @transaction_id
        """
        
        check_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("transaction_id", "STRING", transaction_id)
            ]
        )
        
        check_job = bq_client.query(check_query, job_config=check_job_config)
        results = list(check_job.result())
        
        if results:
            # Update existing record
            update_query = f"""
                UPDATE `{BQ_ANALYSIS_TABLE_ID}`
                SET {column_name} = @analysis_text
                WHERE transaction_id = @transaction_id
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("analysis_text", "STRING", analysis_text),
                    bigquery.ScalarQueryParameter("transaction_id", "STRING", transaction_id)
                ]
            )
            
            query_job = bq_client.query(update_query, job_config=job_config)
            query_job.result()
            
            logger.info(f"✓ Updated {column_name} for transaction {transaction_id} in BigQuery")
        else:
            # Insert new record
            insert_query = f"""
                INSERT INTO `{BQ_ANALYSIS_TABLE_ID}` (transaction_id, {column_name})
                VALUES (@transaction_id, @analysis_text)
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("transaction_id", "STRING", transaction_id),
                    bigquery.ScalarQueryParameter("analysis_text", "STRING", analysis_text)
                ]
            )
            
            query_job = bq_client.query(insert_query, job_config=job_config)
            query_job.result()
            
            logger.info(f"✓ Inserted {column_name} for transaction {transaction_id} in BigQuery")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to store {column_name} in BigQuery: {e}", exc_info=True)
        return False


def update_approval_status(transaction_id: str, approval_status: str) -> bool:
    """
    Update the approval status of a transaction in the PaymentsCompliance table.
    
    Args:
        transaction_id: The transaction ID to update
        approval_status: The new approval status (APPROVED, REJECTED, REVIEW, etc.)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Strip whitespace from transaction_id
        transaction_id = transaction_id.strip()
        
        update_query = f"""
            UPDATE `{BQ_COMPLIANCE_TABLE_ID}`
            SET approval_status = @approval_status
            WHERE transaction_id = @transaction_id
        """
        
        print("Updating approval status")
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("approval_status", "STRING", approval_status),
                bigquery.ScalarQueryParameter("transaction_id", "STRING", transaction_id)
            ]
        )
        
        query_job = bq_client.query(update_query, job_config=job_config)
        query_job.result()
        
        logger.info(f"✓ Updated approval_status to '{approval_status}' for transaction {transaction_id}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to update approval_status for transaction {transaction_id}: {e}", exc_info=True)
        return False


def create_analysis_callback(column_name: str, output_key: str):
    """
    Factory function to create agent callbacks that store analysis in BigQuery.
    
    Args:
        column_name: The BigQuery column to store the analysis in
        output_key: The session state key where the agent stores its output
        
    Returns:
        A callback function for the agent
    """
    def callback(callback_context: CallbackContext) -> Optional[genai_types.Content]:
        """Store analysis from session state to BigQuery."""
        try:
            # Get transaction_id from session state
            transaction_id = callback_context.session.state.get("transaction_id")
            
            if not transaction_id:
                logger.warning(f"⚠ No transaction_id in session state, skipping {column_name} storage")
                return None
            
            # Get the agent's output from session state using output_key
            analysis_text = callback_context.session.state.get(output_key)
            
            if analysis_text:
                # Convert to string if it's not already
                if not isinstance(analysis_text, str):
                    analysis_text = str(analysis_text)
                
                # Store in BigQuery
                store_analysis_in_bigquery(transaction_id, column_name, analysis_text)
                logger.info(f"✓ Stored {column_name} for transaction {transaction_id}")
            else:
                logger.warning(f"⚠ No analysis text found in session state key '{output_key}' for {column_name}")
            
        except Exception as e:
            logger.error(f"✗ Error in {column_name} callback: {e}", exc_info=True)
        
        # Return None to suppress UI response
        return None
    
    return callback


def create_critique_callback(column_name: str, output_key: str):
    """
    Factory function to create critique agent callback that stores analysis 
    and updates approval status based on the final decision.
    
    Args:
        column_name: The BigQuery column to store the analysis in
        output_key: The session state key where the agent stores its output
        
    Returns:
        A callback function for the critique agent
    """
    def callback(callback_context: CallbackContext) -> Optional[genai_types.Content]:
        """Store critique analysis and update approval status based on category."""
        try:
            # Get transaction_id from session state
            transaction_id = callback_context.session.state.get("transaction_id")
            
            if not transaction_id:
                logger.warning(f"⚠ No transaction_id in session state, skipping {column_name} storage")
                return None
            
            # Get the agent's output from session state using output_key
            analysis_text = callback_context.session.state.get(output_key)
            if analysis_text:
                # Convert to string if it's not already
                if not isinstance(analysis_text, str):
                    analysis_text = str(analysis_text)
                
                # Store in BigQuery
                store_analysis_in_bigquery(transaction_id, column_name, analysis_text)
                logger.info(f"✓ Stored {column_name} for transaction {transaction_id}")
                
                # Parse JSON and extract category to update approval status
                try:
                    # Strip whitespace before parsing
                    match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                    critique_data = json.loads(match.group())
                    final_decision = critique_data.get("final_decision", {})
                    category = final_decision.get("category")
                    
                    if category:
                        # Map category to approval_status
                        status_mapping = {
                            "APPROVED": "Approved",
                            "REJECTED": "Rejected",
                            "REVIEW": "In Review"
                        }
                        approval_status = status_mapping.get(category, category)
                        # Update approval status in PaymentsCompliance table
                        update_approval_status(transaction_id, approval_status)
                        logger.info(f"✓ Updated approval_status to '{approval_status}' based on category '{category}'")
                    else:
                        logger.warning(f"⚠ No category found in critique analysis for transaction {transaction_id}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"✗ Failed to parse critique JSON for transaction {transaction_id}: {e}")
                except Exception as e:
                    logger.error(f"✗ Error extracting category from critique for transaction {transaction_id}: {e}")
                    
            else:
                logger.warning(f"⚠ No analysis text found in session state key '{output_key}' for {column_name}")
            
        except Exception as e:
            logger.error(f"✗ Error in {column_name} callback: {e}", exc_info=True)
        
        # Return None to suppress UI response
        return None
    
    return callback
