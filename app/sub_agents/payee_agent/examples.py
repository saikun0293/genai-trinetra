"""Example usage and integration tests for Payee Agent.

This module demonstrates various ways to use the payee agent and provides
integration test examples.

Author: Agent Architect
Date: December 15, 2025
"""

import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Example: Basic payee analysis."""
    from app.sub_agents.payee_agent import payee_agent

    logger.info("=== Basic Usage Example ===")

    # Prepare state with payee ID
    state = {"payee_id": "P12345"}

    # Run the agent
    logger.info(f"Analyzing payee: {state['payee_id']}")
    result = payee_agent.run(state=state)

    # Access results
    output = result.state["output"]

    logger.info(f"Risk Level: {output['risk_level']}")
    logger.info(f"Trust Level: {output['payee_trust_level']}")
    logger.info(f"Classification: {output['payee_classification']}")
    logger.info(f"Risk Score: {output['risk_score']}/100")

    if output["red_flags"]:
        logger.warning(f"Red Flags Identified: {len(output['red_flags'])}")
        for flag in output["red_flags"]:
            logger.warning(f"  - {flag}")

    return output


def example_with_error_handling():
    """Example: Robust error handling."""
    from app.sub_agents.payee_agent import payee_agent, PayeeDataError

    logger.info("=== Error Handling Example ===")

    def analyze_payee_safe(payee_id: str) -> Dict[str, Any]:
        """Analyze a payee with comprehensive error handling."""
        try:
            state = {"payee_id": payee_id}
            result = payee_agent.run(state=state)
            return {"success": True, "data": result.state["output"]}
        except PayeeDataError as e:
            logger.error(f"Data error for payee {payee_id}: {e}")
            return {"success": False, "error": "data_unavailable", "message": str(e)}
        except ValueError as e:
            logger.error(f"Invalid payee ID {payee_id}: {e}")
            return {"success": False, "error": "invalid_input", "message": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error analyzing {payee_id}: {e}")
            return {"success": False, "error": "analysis_failed", "message": str(e)}

    # Test with valid payee
    result = analyze_payee_safe("P12345")
    if result["success"]:
        logger.info(f"✓ Analysis successful")
        logger.info(f"Analysis preview: {result['data']['analysis'][:200]}...")
    else:
        logger.error(f"✗ Analysis failed: {result['error']}")

    return result


def example_batch_analysis():
    """Example: Analyzing multiple payees."""
    from app.sub_agents.payee_agent import payee_agent

    logger.info("=== Batch Analysis Example ===")

    payee_ids = ["P12345", "P67890", "P11111"]
    results = []

    for payee_id in payee_ids:
        try:
            logger.info(f"Analyzing {payee_id}...")
            state = {"payee_id": payee_id}
            result = payee_agent.run(state=state)
            results.append(
                {
                    "payee_id": payee_id,
                    "analysis": result.state["output"]["analysis"][:100] + "...",
                }
            )
        except Exception as e:
            logger.error(f"Failed to analyze {payee_id}: {e}")
            results.append({"payee_id": payee_id, "error": str(e)})

    # Summary
    logger.info(f"Analyzed {len(results)} payees")
    for r in results:
        if "error" not in r:
            logger.info(f"  {r['payee_id']}: {r['analysis']}")

    return results


def example_using_utility_functions():
    """Example: Direct use of utility functions."""
    from app.sub_agents.payee_agent import (
        calculate_risk_score,
        calculate_trust_level,
        classify_payee,
        determine_risk_level,
        identify_red_flags,
        calculate_rejection_ratio,
        PayeeClassification,
        TrustLevel,
        RiskLevel,
    )

    logger.info("=== Utility Functions Example ===")

    # Sample transaction data
    total_transactions = 150
    rejected_transactions = 8
    payment_methods = ["WIRE_TRANSFER", "ACH", "CHECK"]
    currencies = ["USD", "EUR"]
    payee_countries = ["USA", "UK"]

    # Calculate metrics
    rejection_ratio = calculate_rejection_ratio(
        total_transactions, rejected_transactions
    )
    logger.info(f"Rejection Ratio: {rejection_ratio:.2%}")

    classification = classify_payee(total_transactions, payment_methods, currencies)
    logger.info(f"Classification: {classification.value}")

    trust_level = calculate_trust_level(rejection_ratio)
    logger.info(f"Trust Level: {trust_level.value}")

    risk_score = calculate_risk_score(
        total_transactions=total_transactions,
        rejection_ratio=rejection_ratio,
        payment_methods=payment_methods,
        currencies=currencies,
        payee_countries=payee_countries,
    )
    logger.info(f"Risk Score: {risk_score}/100")

    risk_level = determine_risk_level(risk_score)
    logger.info(f"Risk Level: {risk_level.value}")

    red_flags = identify_red_flags(
        rejection_ratio=rejection_ratio,
        payment_methods=payment_methods,
        currencies=currencies,
        payee_countries=payee_countries,
    )

    if red_flags:
        logger.warning(f"Red Flags: {len(red_flags)}")
        for flag in red_flags:
            logger.warning(f"  - {flag}")
    else:
        logger.info("✓ No red flags identified")


def example_custom_configuration():
    """Example: Using custom configuration."""
    from app.sub_agents.payee_agent.config import PayeeAgentConfig, RiskThresholds

    logger.info("=== Custom Configuration Example ===")

    # Create custom thresholds
    custom_thresholds = RiskThresholds(
        HIGH_REJECTION_RATIO=0.25,  # More strict
        MEDIUM_REJECTION_RATIO=0.08,
        BUSINESS_TRANSACTION_THRESHOLD=75,  # Higher bar
        HIGH_VOLUME_THRESHOLD=150,
    )

    logger.info(
        f"Custom high rejection threshold: {custom_thresholds.HIGH_REJECTION_RATIO}"
    )
    logger.info(
        f"Custom business threshold: {custom_thresholds.BUSINESS_TRANSACTION_THRESHOLD}"
    )

    # Note: To use custom config globally, you would need to update the config module
    # For production, consider dependency injection pattern


def example_formatting_and_reporting():
    """Example: Formatting analysis results."""
    from app.sub_agents.payee_agent import (
        format_payee_summary,
        format_vendor_summary,
        PayeeClassification,
        TrustLevel,
        RiskLevel,
    )

    logger.info("=== Formatting Example ===")

    # Payee summary
    payee_summary = format_payee_summary(
        payee_id="P12345",
        total_transactions=150,
        total_amount=450000.00,
        rejection_ratio=0.05,
        payment_methods=["WIRE", "ACH"],
        currencies=["USD", "EUR"],
        countries=["USA", "UK"],
        classification=PayeeClassification.BUSINESS,
        trust_level=TrustLevel.HIGH,
        risk_score=28,
        risk_level=RiskLevel.LOW,
        red_flags=[],
    )

    logger.info("Payee Summary:")
    print(payee_summary)
    print()

    # Vendor summary
    vendor_summary = format_vendor_summary(
        vendor_id="V789",
        vendor_country="USA",
        vendor_industry="Technology",
        total_transactions=50,
        rejection_ratio=0.02,
        reject_reasons=["Duplicate transaction"],
    )

    logger.info("Vendor Summary:")
    print(vendor_summary)


def example_data_validation():
    """Example: Data validation utilities."""
    from app.sub_agents.payee_agent import validate_payee_data, validate_vendor_data

    logger.info("=== Data Validation Example ===")

    # Valid payee data
    valid_payee_data = {
        "payee_id": "P12345",
        "total_transactions": 100,
        "total_payment_amount": 50000.00,
        "rejected_transactions": 5,
    }

    is_valid = validate_payee_data(valid_payee_data)
    logger.info(f"Valid payee data: {is_valid}")

    # Invalid payee data (missing field)
    invalid_payee_data = {
        "payee_id": "P12345",
        "total_transactions": 100,
        # Missing required fields
    }

    is_valid = validate_payee_data(invalid_payee_data)
    logger.info(f"Invalid payee data: {is_valid}")

    # Valid vendor data
    valid_vendor_data = {
        "vendor_id": "V789",
        "total_transactions": 50,
        "rejected_transactions": 1,
    }

    is_valid = validate_vendor_data(valid_vendor_data)
    logger.info(f"Valid vendor data: {is_valid}")


def run_all_examples():
    """Run all example functions."""
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Error Handling", example_with_error_handling),
        ("Batch Analysis", example_batch_analysis),
        ("Utility Functions", example_using_utility_functions),
        ("Custom Configuration", example_custom_configuration),
        ("Formatting & Reporting", example_formatting_and_reporting),
        ("Data Validation", example_data_validation),
    ]

    logger.info("=" * 60)
    logger.info("PAYEE AGENT - COMPREHENSIVE EXAMPLES")
    logger.info("=" * 60)

    for name, func in examples:
        try:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Running: {name}")
            logger.info(f"{'=' * 60}")
            func()
            logger.info(f"✓ {name} completed successfully\n")
        except Exception as e:
            logger.error(f"✗ {name} failed: {e}\n")

    logger.info("=" * 60)
    logger.info("All examples completed")
    logger.info("=" * 60)


if __name__ == "__main__":
    # Run utility function examples (don't require actual agent execution)
    try:
        example_using_utility_functions()
        example_formatting_and_reporting()
        example_data_validation()
        example_custom_configuration()
    except Exception as e:
        logger.error(f"Example execution failed: {e}")

    # Note: To run full agent examples, ensure:
    # 1. GOOGLE_CLOUD_PROJECT and BQ_DATASET_ID are set
    # 2. BigQuery table exists with transaction data
    # 3. Appropriate GCP credentials are configured
