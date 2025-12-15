from typing import Any
from google.adk.tools import ToolContext


def extract_transaction_data(tool_context: ToolContext) -> dict[str, Any]:
    """
    Extract transaction data from session state for analysis.
    
    Args:
        tool_context: The ADK tool context with access to session state
        
    Returns:
        dict: Transaction data for analysis
    """
    transaction = tool_context.state.get("transaction_data", {})
    
    return {
        "transaction_id": transaction.get("transaction_id"),
        "payee_country": transaction.get("payee_country"),
        "vendor_country": transaction.get("vendor_country"),
        "payment_method": transaction.get("payment_method"),
        "payment_time": transaction.get("payment_time"),
        "payment_purpose": transaction.get("payment_purpose"),
        "payment_currency": transaction.get("payment_currency"),
        "payment_amount": transaction.get("payment_amount"),
        "vendor_industry": transaction.get("vendor_industry")
    }