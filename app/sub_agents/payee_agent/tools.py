from typing import List, Dict, Any

class PayeeTools:
    def __init__(self, bigquery_tool):
        self.bigquery_tool = bigquery_tool

    def query_payee_history(self, payee_id: str) -> Dict[str, Any]:
        """
        Fetch transaction history for a given payee.
        Returns aggregated facts + vendor_id list.
        """

        query = """
        SELECT
            payee_id,
            COUNT(*) AS total_transactions,
            SUM(payment_amount) AS total_payment_amount,
            COUNTIF(approval_status = 'REJECTED') AS rejected_transactions,
            ARRAY_AGG(DISTINCT vendor_id IGNORE NULLS) AS vendor_ids,
            ARRAY_AGG(DISTINCT payment_method IGNORE NULLS) AS payment_methods,
            ARRAY_AGG(DISTINCT payment_currency IGNORE NULLS) AS currencies,
            ARRAY_AGG(DISTINCT payee_country IGNORE NULLS) AS payee_countries
        FROM `{{table_name}}`
        WHERE payee_id = @payee_id
        GROUP BY payee_id
        """

        params = {
            "payee_id": payee_id
        }

        return self.bigquery_tool.run_query(
            query=query,
            params=params
        )

    def query_vendor_risk_data(self, vendor_id: str) -> Dict[str, Any]:
        """
        Fetch vendor-related risk indicators derived only
        from transaction history.
        """

        query = """
        SELECT
            vendor_id,
            vendor_country,
            vendor_industry,
            COUNT(*) AS total_transactions,
            COUNTIF(approval_status = 'REJECTED') AS rejected_transactions,
            ARRAY_AGG(DISTINCT reject_reason IGNORE NULLS) AS reject_reasons
        FROM `{{table_name}}`
        WHERE vendor_id = @vendor_id
        GROUP BY vendor_id, vendor_country, vendor_industry
        """

        params = {
            "vendor_id": vendor_id
        }

        return self.bigquery_tool.run_query(
            query=query,
            params=params
        )
