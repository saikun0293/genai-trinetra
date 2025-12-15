"""Utility functions for payee agent risk assessment.

This module contains helper functions for risk scoring, classification,
and analysis of payee and vendor data.
"""

import logging
from typing import Any, Dict, List, Optional

from .config import (
    PayeeClassification,
    RiskLevel,
    RiskThresholds,
    TrustLevel,
    config,
)

logger = logging.getLogger(__name__)


def calculate_rejection_ratio(
    total_transactions: int, rejected_transactions: int
) -> float:
    """Calculate the rejection ratio.

    Args:
        total_transactions: Total number of transactions
        rejected_transactions: Number of rejected transactions

    Returns:
        Rejection ratio as a float between 0 and 1
    """
    if total_transactions == 0:
        return 0.0
    return rejected_transactions / total_transactions


def classify_payee(
    total_transactions: int,
    payment_methods: List[str],
    currencies: List[str],
) -> PayeeClassification:
    """Classify a payee as BUSINESS or INDIVIDUAL based on transaction patterns.

    Args:
        total_transactions: Total number of transactions
        payment_methods: List of unique payment methods used
        currencies: List of unique currencies used

    Returns:
        PayeeClassification enum value
    """
    thresholds = config.thresholds

    # Business indicators:
    # - High transaction volume
    # - Multiple payment methods
    # - Multiple currencies

    if total_transactions >= thresholds.BUSINESS_TRANSACTION_THRESHOLD:
        return PayeeClassification.BUSINESS

    if len(payment_methods) >= 3 or len(currencies) >= 2:
        return PayeeClassification.BUSINESS

    if total_transactions > 10:
        return PayeeClassification.INDIVIDUAL

    return PayeeClassification.UNKNOWN


def calculate_trust_level(rejection_ratio: float) -> TrustLevel:
    """Calculate trust level based on rejection ratio.

    Args:
        rejection_ratio: Ratio of rejected transactions (0.0 to 1.0)

    Returns:
        TrustLevel enum value
    """
    thresholds = config.thresholds

    if rejection_ratio >= thresholds.HIGH_REJECTION_RATIO:
        return TrustLevel.LOW
    elif rejection_ratio >= thresholds.MEDIUM_REJECTION_RATIO:
        return TrustLevel.MEDIUM
    else:
        return TrustLevel.HIGH


def calculate_risk_score(
    total_transactions: int,
    rejection_ratio: float,
    payment_methods: List[str],
    currencies: List[str],
    payee_countries: List[str],
) -> int:
    """Calculate a risk score from 0-100 based on multiple factors.

    Args:
        total_transactions: Total number of transactions
        rejection_ratio: Ratio of rejected transactions
        payment_methods: List of unique payment methods
        currencies: List of unique currencies
        payee_countries: List of unique payee countries

    Returns:
        Risk score from 0 to 100
    """
    score = 0
    thresholds = config.thresholds

    # Rejection ratio contribution (0-40 points)
    score += min(40, int(rejection_ratio * 100))

    # Diversity/complexity contribution (0-30 points)
    method_score = min(15, len(payment_methods) * 3)
    currency_score = min(15, len(currencies) * 5)
    score += method_score + currency_score

    # Multiple countries can be a red flag (0-15 points)
    if len(payee_countries) > 3:
        score += 15
    elif len(payee_countries) > 1:
        score += 7

    # Low transaction volume can indicate uncertainty (0-15 points)
    if total_transactions < 5:
        score += 15
    elif total_transactions < 20:
        score += 7

    return min(100, score)


def determine_risk_level(risk_score: int) -> RiskLevel:
    """Determine risk level based on risk score.

    Args:
        risk_score: Risk score from 0 to 100

    Returns:
        RiskLevel enum value
    """
    thresholds = config.thresholds

    if risk_score <= thresholds.VERY_LOW_RISK_MAX:
        return RiskLevel.VERY_LOW
    elif risk_score <= thresholds.LOW_RISK_MAX:
        return RiskLevel.LOW
    elif risk_score <= thresholds.MEDIUM_RISK_MAX:
        return RiskLevel.MEDIUM
    elif risk_score <= thresholds.HIGH_RISK_MAX:
        return RiskLevel.HIGH
    else:
        return RiskLevel.VERY_HIGH


def identify_red_flags(
    rejection_ratio: float,
    payment_methods: List[str],
    currencies: List[str],
    payee_countries: List[str],
    vendor_rejection_ratio: Optional[float] = None,
) -> List[str]:
    """Identify potential red flags in transaction patterns.

    Args:
        rejection_ratio: Payee rejection ratio
        payment_methods: List of payment methods
        currencies: List of currencies
        payee_countries: List of payee countries
        vendor_rejection_ratio: Optional vendor rejection ratio

    Returns:
        List of red flag descriptions
    """
    red_flags = []
    thresholds = config.thresholds

    if rejection_ratio >= thresholds.HIGH_REJECTION_RATIO:
        red_flags.append(
            f"High rejection rate: {rejection_ratio:.1%} of transactions rejected"
        )

    if len(currencies) > thresholds.MAX_CURRENCY_DIVERSITY:
        red_flags.append(
            f"High currency diversity: {len(currencies)} different currencies"
        )

    if len(payment_methods) > thresholds.MAX_PAYMENT_METHOD_DIVERSITY:
        red_flags.append(
            f"High payment method diversity: {len(payment_methods)} different methods"
        )

    if len(payee_countries) > 3:
        red_flags.append(
            f"Multiple countries: Transactions from {len(payee_countries)} countries"
        )

    if (
        vendor_rejection_ratio
        and vendor_rejection_ratio >= thresholds.HIGH_REJECTION_RATIO
    ):
        red_flags.append(f"High vendor rejection rate: {vendor_rejection_ratio:.1%}")

    return red_flags


def format_payee_summary(
    payee_id: str,
    total_transactions: int,
    total_amount: float,
    rejection_ratio: float,
    payment_methods: List[str],
    currencies: List[str],
    countries: List[str],
    classification: PayeeClassification,
    trust_level: TrustLevel,
    risk_score: int,
    risk_level: RiskLevel,
    red_flags: List[str],
) -> str:
    """Format a comprehensive payee summary.

    Args:
        payee_id: Payee identifier
        total_transactions: Total transaction count
        total_amount: Total payment amount
        rejection_ratio: Rejection ratio
        payment_methods: Payment methods list
        currencies: Currencies list
        countries: Countries list
        classification: Payee classification
        trust_level: Trust level
        risk_score: Risk score (0-100)
        risk_level: Overall risk level
        red_flags: List of identified red flags

    Returns:
        Formatted summary string
    """
    summary_parts = [
        f"Payee ID: {payee_id}",
        f"Classification: {classification.value}",
        f"Trust Level: {trust_level.value}",
        f"",
        f"Transaction Summary:",
        f"  - Total Transactions: {total_transactions}",
        f"  - Total Amount: ${total_amount:,.2f}",
        f"  - Rejection Rate: {rejection_ratio:.1%}",
        f"  - Payment Methods: {', '.join(payment_methods)}",
        f"  - Currencies: {', '.join(currencies)}",
        f"  - Countries: {', '.join(countries)}",
        f"",
        f"Risk Assessment:",
        f"  - Risk Score: {risk_score}/100",
        f"  - Risk Level: {risk_level.value}",
    ]

    if red_flags:
        summary_parts.append("")
        summary_parts.append("Red Flags:")
        for flag in red_flags:
            summary_parts.append(f"  - {flag}")

    return "\n".join(summary_parts)


def format_vendor_summary(
    vendor_id: str,
    vendor_country: Optional[str],
    vendor_industry: Optional[str],
    total_transactions: int,
    rejection_ratio: float,
    reject_reasons: List[str],
) -> str:
    """Format a vendor risk summary.

    Args:
        vendor_id: Vendor identifier
        vendor_country: Vendor country
        vendor_industry: Vendor industry
        total_transactions: Total transaction count
        rejection_ratio: Rejection ratio
        reject_reasons: List of rejection reasons

    Returns:
        Formatted vendor summary string
    """
    summary_parts = [
        f"Vendor ID: {vendor_id}",
        f"Country: {vendor_country or 'Unknown'}",
        f"Industry: {vendor_industry or 'Unknown'}",
        f"",
        f"Transaction Summary:",
        f"  - Total Transactions: {total_transactions}",
        f"  - Rejection Rate: {rejection_ratio:.1%}",
    ]

    if reject_reasons:
        summary_parts.append("")
        summary_parts.append("Common Rejection Reasons:")
        for reason in reject_reasons:
            summary_parts.append(f"  - {reason}")

    return "\n".join(summary_parts)


def validate_payee_data(data: Dict[str, Any]) -> bool:
    """Validate that payee data contains required fields.

    Args:
        data: Payee data dictionary

    Returns:
        True if data is valid, False otherwise
    """
    required_fields = [
        "payee_id",
        "total_transactions",
        "total_payment_amount",
        "rejected_transactions",
    ]

    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field in payee data: {field}")
            return False

    return True


def validate_vendor_data(data: Dict[str, Any]) -> bool:
    """Validate that vendor data contains required fields.

    Args:
        data: Vendor data dictionary

    Returns:
        True if data is valid, False otherwise
    """
    required_fields = [
        "vendor_id",
        "total_transactions",
        "rejected_transactions",
    ]

    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field in vendor data: {field}")
            return False

    return True
