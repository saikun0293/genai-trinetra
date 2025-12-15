"""State schema definitions for Payee Agent.

This module defines the state structure using TypedDict for type safety
and validation in the payee agent workflow.
"""

from typing import Optional, TypedDict


class PayeeAnalysisOutput(TypedDict):
    """Output structure for payee analysis."""

    analysis: str
    vendor_analysis: Optional[str]


class PayeeAgentState(TypedDict):
    """Complete state schema for Payee Agent."""

    # Input
    payee_id: str

    # Output
    output: PayeeAnalysisOutput
