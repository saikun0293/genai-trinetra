"""Payee Agent Module.

This module provides a comprehensive payee and vendor risk analysis agent
that leverages BigQuery for transaction data analysis and provides detailed
risk assessments.

Components:
    - payee_agent: The main LlmAgent instance for payee risk analysis
    - PayeeTools: Data retrieval tools for payee and vendor queries
    - PayeeDataError: Custom exception for data-related errors
    - Configuration: Risk thresholds and environment settings
    - State: TypedDict schemas for type-safe state management
    - Utils: Helper functions for risk scoring and classification

Usage:
    from app.sub_agents.payee_agent import payee_agent

    # The agent expects state with 'payee_id' key
    # and will populate 'output' with risk analysis results

Example:
    state = {"payee_id": "P12345"}
    result = payee_agent.run(state=state)
    print(result.state["output"])

Author: Agent Architect
Date: December 15, 2025
"""

from .config import (
    PayeeAgentConfig,
    PayeeClassification,
    RiskLevel,
    RiskThresholds,
    TrustLevel,
    config,
)
from .payee_agent import payee_agent
from .state import PayeeAgentState, PayeeAnalysisOutput
from .tools import PayeeDataError, PayeeTools

__all__ = [
    # Main agent
    "payee_agent",
    # Tools
    "PayeeTools",
    "PayeeDataError",
    # Configuration
    "config",
    "PayeeAgentConfig",
    "PayeeClassification",
    "RiskLevel",
    "RiskThresholds",
    "TrustLevel",
    # State schemas
    "PayeeAgentState",
    "PayeeAnalysisOutput",
]

__version__ = "1.0.0"
