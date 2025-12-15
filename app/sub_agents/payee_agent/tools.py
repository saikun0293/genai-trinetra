"""Tools module for Payee Agent.

This module provides data retrieval and processing tools for analyzing
payee and vendor transaction data from BigQuery.
"""

import logging
from typing import Any, Dict, List, Optional

from .config import config

logger = logging.getLogger(__name__)


class PayeeDataError(Exception):
    """Exception raised for errors in payee data retrieval or processing."""

    pass


class PayeeTools:
    """Tools for querying and analyzing payee transaction data.

    This class provides methods to retrieve and process payee and vendor
    transaction history from BigQuery for risk analysis.

    Attributes:
        bigquery_tool: BigQuery tool instance for executing queries
    """

    def __init__(self, bigquery_tool):
        """Initialize PayeeTools with a BigQuery tool instance.

        Args:
            bigquery_tool: BigQuery tool for executing queries
        """
        self.bigquery_tool = bigquery_tool
        logger.info("PayeeTools initialized")

    def query_payee_history(self, payee_id: str) -> Dict[str, Any]:
        """Fetch transaction history for a given payee.

        Retrieves aggregated transaction data including counts, amounts,
        rejection statistics, and unique values for payment methods,
        currencies, and countries.

        Args:
            payee_id: Unique identifier for the payee

        Returns:
            Dictionary containing aggregated payee transaction data with keys:
                - payee_id: The payee identifier
                - total_transactions: Total number of transactions
                - total_payment_amount: Sum of all payment amounts
                - rejected_transactions: Count of rejected transactions
                - vendor_ids: Array of unique vendor IDs
                - payment_methods: Array of unique payment methods
                - currencies: Array of unique currencies
                - payee_countries: Array of unique payee countries

        Raises:
            PayeeDataError: If query execution fails or returns invalid data
            ValueError: If payee_id is empty or invalid
        """
        if not payee_id or not isinstance(payee_id, str):
            raise ValueError(f"Invalid payee_id: {payee_id}")

        logger.info(f"Querying payee history for payee_id: {payee_id}")

        query = f"""
        SELECT
            payee_id,
            COUNT(*) AS total_transactions,
            SUM(payment_amount) AS total_payment_amount,
            COUNTIF(approval_status = 'REJECTED') AS rejected_transactions,
            ARRAY_AGG(DISTINCT vendor_id IGNORE NULLS) AS vendor_ids,
            ARRAY_AGG(DISTINCT payment_method IGNORE NULLS) AS payment_methods,
            ARRAY_AGG(DISTINCT payment_currency IGNORE NULLS) AS currencies,
            ARRAY_AGG(DISTINCT payee_country IGNORE NULLS) AS payee_countries
        FROM {config.full_table_name}
        WHERE payee_id = @payee_id
        GROUP BY payee_id
        """

        params = {"payee_id": payee_id}

        try:
            result = self.bigquery_tool.run_query(query=query, params=params)

            if not result or (isinstance(result, list) and len(result) == 0):
                logger.warning(f"No data found for payee_id: {payee_id}")
                raise PayeeDataError(f"No transaction data found for payee: {payee_id}")

            logger.info(f"Successfully retrieved payee history for {payee_id}")
            return result

        except Exception as e:
            logger.error(f"Error querying payee history for {payee_id}: {str(e)}")
            raise PayeeDataError(f"Failed to retrieve payee data: {str(e)}") from e

    def query_vendor_risk_data(self, vendor_id: str) -> Dict[str, Any]:
        """Fetch vendor-related risk indicators from transaction history.

        Retrieves aggregated vendor data including transaction counts,
        rejection statistics, and common rejection reasons.

        Args:
            vendor_id: Unique identifier for the vendor

        Returns:
            Dictionary containing vendor risk data with keys:
                - vendor_id: The vendor identifier
                - vendor_country: Vendor's country
                - vendor_industry: Vendor's industry classification
                - total_transactions: Total number of transactions
                - rejected_transactions: Count of rejected transactions
                - reject_reasons: Array of unique rejection reasons

        Raises:
            PayeeDataError: If query execution fails or returns invalid data
            ValueError: If vendor_id is empty or invalid
        """
        if not vendor_id or not isinstance(vendor_id, str):
            raise ValueError(f"Invalid vendor_id: {vendor_id}")

        logger.info(f"Querying vendor risk data for vendor_id: {vendor_id}")

        query = f"""
        SELECT
            vendor_id,
            vendor_country,
            vendor_industry,
            COUNT(*) AS total_transactions,
            COUNTIF(approval_status = 'REJECTED') AS rejected_transactions,
            ARRAY_AGG(DISTINCT reject_reason IGNORE NULLS) AS reject_reasons
        FROM {config.full_table_name}
        WHERE vendor_id = @vendor_id
        GROUP BY vendor_id, vendor_country, vendor_industry
        """

        params = {"vendor_id": vendor_id}

        try:
            result = self.bigquery_tool.run_query(query=query, params=params)

            if not result or (isinstance(result, list) and len(result) == 0):
                logger.warning(f"No data found for vendor_id: {vendor_id}")
                raise PayeeDataError(
                    f"No transaction data found for vendor: {vendor_id}"
                )

            logger.info(f"Successfully retrieved vendor risk data for {vendor_id}")
            return result

        except Exception as e:
            logger.error(f"Error querying vendor data for {vendor_id}: {str(e)}")
            raise PayeeDataError(f"Failed to retrieve vendor data: {str(e)}") from e
