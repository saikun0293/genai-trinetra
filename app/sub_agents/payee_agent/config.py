"""Configuration module for Payee Agent.

This module contains configuration constants, environment variable management,
and risk assessment thresholds for the payee agent.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class TrustLevel(str, Enum):
    """Trust level classification based on transaction patterns."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class PayeeClassification(str, Enum):
    """Payee classification types."""

    BUSINESS = "BUSINESS"
    INDIVIDUAL = "INDIVIDUAL"
    UNKNOWN = "UNKNOWN"


class RiskLevel(str, Enum):
    """Overall risk level assessment."""

    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


@dataclass(frozen=True)
class RiskThresholds:
    """Risk assessment thresholds for calculating risk scores."""

    # Rejection ratio thresholds
    HIGH_REJECTION_RATIO: float = 0.3  # 30% or more rejections
    MEDIUM_REJECTION_RATIO: float = 0.1  # 10-30% rejections

    # Transaction count thresholds for classification
    BUSINESS_TRANSACTION_THRESHOLD: int = 50
    HIGH_VOLUME_THRESHOLD: int = 100

    # Risk score thresholds
    VERY_LOW_RISK_MAX: int = 20
    LOW_RISK_MAX: int = 40
    MEDIUM_RISK_MAX: int = 60
    HIGH_RISK_MAX: int = 80
    # Above 80 is VERY_HIGH

    # Currency and method diversity thresholds (red flags)
    MAX_CURRENCY_DIVERSITY: int = 5
    MAX_PAYMENT_METHOD_DIVERSITY: int = 4


@dataclass
class PayeeAgentConfig:
    """Configuration for Payee Agent."""

    model: str = os.getenv("MODEL", "gemini-2.0-flash-001")
    project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    dataset_id: str = os.getenv("BQ_DATASET_ID", "")
    table_name: str = os.getenv("BQ_TABLE_NAME", "PaymentsCompliance")
    location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    # Risk assessment configuration
    thresholds: RiskThresholds = RiskThresholds()

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")
        if not self.dataset_id:
            raise ValueError("BQ_DATASET_ID environment variable is required")

    @property
    def full_table_name(self) -> str:
        """Get fully qualified BigQuery table name."""
        return f"`{self.project_id}.{self.dataset_id}.{self.table_name}`"


# Global configuration instance
config = PayeeAgentConfig()
