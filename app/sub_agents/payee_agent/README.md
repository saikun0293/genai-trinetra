# Payee Risk Analysis Agent

A comprehensive, production-ready agent for analyzing payee and vendor transaction patterns using Google's Agent Development Kit (ADK) and BigQuery.

## Overview

The Payee Agent is an intelligent risk assessment system that analyzes transaction histories to:

- **Classify payees** (BUSINESS, INDIVIDUAL, or UNKNOWN)
- **Assess trust levels** (HIGH, MEDIUM, LOW)
- **Calculate risk scores** (0-100 scale)
- **Determine risk levels** (VERY_LOW to VERY_HIGH)
- **Identify red flags** in transaction patterns
- **Analyze vendor relationships** and associated risks

## Architecture

### Design Principles

This agent follows enterprise-grade best practices:

1. **Separation of Concerns**: Clear module boundaries between configuration, tools, utilities, state, and agent logic
2. **Type Safety**: Full type hints and TypedDict schemas for state management
3. **Error Handling**: Comprehensive exception handling with custom error types
4. **Logging**: Structured logging at all critical points for observability
5. **Configuration Management**: Environment-based configuration with validation
6. **Documentation**: Comprehensive docstrings following Google style guide
7. **Testability**: Modular design enabling unit and integration testing

### Module Structure

```
payee_agent/
├── __init__.py          # Public API and exports
├── config.py            # Configuration and constants
├── state.py             # State schema definitions (TypedDict)
├── tools.py             # Data retrieval tools
├── utils.py             # Helper functions for risk assessment
├── payee_agent.py       # Main agent implementation
└── README.md            # This file
```

### Component Details

#### 1. Configuration (`config.py`)

**Purpose**: Centralized configuration management with validation

**Key Components**:

- `PayeeAgentConfig`: Main configuration dataclass
- Environment variable loading with defaults
- Risk threshold constants
- Enums for classification types (TrustLevel, PayeeClassification, RiskLevel)

**Example**:

```python
from app.sub_agents.payee_agent import config

print(config.project_id)  # GCP project
print(config.thresholds.HIGH_REJECTION_RATIO)  # 0.3
```

#### 2. State Schema (`state.py`)

**Purpose**: Type-safe state definitions using TypedDict

**Schema**:

```python
{
    "payee_id": str,  # Input
    "output": {
        "payee_id": str,
        "payee_summary": str,
        "payee_trust_level": str,
        "payee_classification": str,
        "risk_score": int,
        "risk_level": str,
        "red_flags": List[str],
        "vendor_summary": Optional[str]
    }
}
```

#### 3. Tools (`tools.py`)

**Purpose**: BigQuery data retrieval with error handling

**Key Methods**:

- `query_payee_history(payee_id)`: Fetch aggregated payee transaction data
- `query_vendor_risk_data(vendor_id)`: Fetch vendor risk indicators

**Features**:

- Input validation
- Comprehensive error handling
- Query parameterization to prevent SQL injection
- Detailed logging

#### 4. Utilities (`utils.py`)

**Purpose**: Business logic for risk assessment

**Key Functions**:

- `calculate_rejection_ratio()`: Calculate rejection rate
- `classify_payee()`: Classify as BUSINESS/INDIVIDUAL
- `calculate_trust_level()`: Determine trust level
- `calculate_risk_score()`: Score 0-100 based on multiple factors
- `determine_risk_level()`: Map score to risk level
- `identify_red_flags()`: Detect suspicious patterns
- `format_payee_summary()`: Create human-readable summaries
- Data validation functions

#### 5. Main Agent (`payee_agent.py`)

**Purpose**: Core agent implementation with ADK

**Features**:

- LlmAgent using Gemini model
- Structured state management
- Before/after callbacks for validation
- Comprehensive instructions for LLM
- Integration with BigQuery sub-agent
- Error handling and recovery

## Usage

### Basic Usage

```python
from app.sub_agents.payee_agent import payee_agent

# Prepare state with payee ID
state = {
    "payee_id": "P12345"
}

# Run the agent
result = payee_agent.run(state=state)

# Access results
output = result.state["output"]
print(f"Risk Level: {output['risk_level']}")
print(f"Trust Level: {output['payee_trust_level']}")
print(f"Classification: {output['payee_classification']}")
print(f"Risk Score: {output['risk_score']}/100")
print(f"Red Flags: {output['red_flags']}")
```

### Advanced Usage with Error Handling

```python
from app.sub_agents.payee_agent import payee_agent, PayeeDataError
import logging

logger = logging.getLogger(__name__)

def analyze_payee(payee_id: str) -> dict:
    """Analyze a payee with comprehensive error handling."""
    try:
        state = {"payee_id": payee_id}
        result = payee_agent.run(state=state)
        return result.state["output"]
    except PayeeDataError as e:
        logger.error(f"Data error for payee {payee_id}: {e}")
        return {"error": "data_unavailable"}
    except ValueError as e:
        logger.error(f"Invalid payee ID {payee_id}: {e}")
        return {"error": "invalid_input"}
    except Exception as e:
        logger.error(f"Unexpected error analyzing {payee_id}: {e}")
        return {"error": "analysis_failed"}

# Use the function
result = analyze_payee("P12345")
if "error" not in result:
    print(f"Analysis complete: Risk Level = {result['risk_level']}")
else:
    print(f"Analysis failed: {result['error']}")
```

### Using Utility Functions Directly

```python
from app.sub_agents.payee_agent import (
    calculate_risk_score,
    classify_payee,
    identify_red_flags
)

# Direct risk calculation
payment_methods = ["WIRE", "ACH", "CHECK"]
currencies = ["USD", "EUR"]
score = calculate_risk_score(
    total_transactions=100,
    rejection_ratio=0.05,
    payment_methods=payment_methods,
    currencies=currencies,
    payee_countries=["USA"]
)
print(f"Risk Score: {score}")

# Classification
classification = classify_payee(
    total_transactions=150,
    payment_methods=payment_methods,
    currencies=currencies
)
print(f"Classification: {classification}")
```

## Risk Assessment Methodology

### Classification Logic

**BUSINESS** indicators:

- ≥50 transactions
- Multiple payment methods (≥3)
- Multiple currencies (≥2)

**INDIVIDUAL** indicators:

- 10-50 transactions
- Consistent payment patterns

**UNKNOWN**:

- <10 transactions (insufficient data)

### Trust Level Calculation

Based on rejection ratio:

- **HIGH**: <10% rejections
- **MEDIUM**: 10-30% rejections
- **LOW**: >30% rejections

### Risk Score Components (0-100)

1. **Rejection Ratio** (40 points max)

   - Direct correlation with rejection percentage

2. **Payment Method Diversity** (15 points max)

   - 3 points per unique method

3. **Currency Diversity** (15 points max)

   - 5 points per unique currency

4. **Country Diversity** (15 points max)

   - > 3 countries: 15 points
   - 2-3 countries: 7 points

5. **Transaction Volume Uncertainty** (15 points max)
   - <5 transactions: 15 points
   - 5-20 transactions: 7 points

### Risk Level Mapping

- **VERY_LOW**: 0-20
- **LOW**: 21-40
- **MEDIUM**: 41-60
- **HIGH**: 61-80
- **VERY_HIGH**: 81-100

### Red Flag Detection

Triggers:

- Rejection rate >30%
- > 5 different currencies
- > 4 different payment methods
- > 3 different countries
- Vendor rejection rate >30%

## Configuration

### Environment Variables

Required:

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
BQ_DATASET_ID=your-dataset-id
```

Optional:

```bash
MODEL=gemini-2.0-flash-001  # Default model
BQ_TABLE_NAME=PaymentsCompliance  # Default table
GOOGLE_CLOUD_LOCATION=us-central1  # Default location
```

### Custom Configuration

```python
from app.sub_agents.payee_agent.config import PayeeAgentConfig, RiskThresholds

# Custom thresholds
custom_thresholds = RiskThresholds(
    HIGH_REJECTION_RATIO=0.25,  # Lower threshold
    BUSINESS_TRANSACTION_THRESHOLD=75  # Higher threshold
)

# Custom config
custom_config = PayeeAgentConfig(
    model="gemini-2.5-pro",
    thresholds=custom_thresholds
)
```

## Database Schema

Expected BigQuery table structure:

```sql
CREATE TABLE `project.dataset.PaymentsCompliance` (
  transaction_id STRING,
  payment_time TIMESTAMP,
  payer_id STRING,
  payee_id STRING,
  payment_amount NUMERIC,
  payment_currency STRING,
  payment_method STRING,
  payment_purpose STRING,
  vendor_id STRING,
  payee_country STRING,
  vendor_country STRING,
  vendor_industry STRING,
  approval_status STRING,  -- 'APPROVED' or 'REJECTED'
  reject_reason STRING
)
```

## Error Handling

### Custom Exceptions

- `PayeeDataError`: Data retrieval or processing failures

### Error Recovery

The agent implements graceful degradation:

1. Invalid data → Returns error state with UNKNOWN classification
2. Query failures → Logged and returned in structured format
3. Missing fields → Validation callbacks catch and log warnings

## Logging

Structured logging at multiple levels:

```python
# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Agent automatically logs:
# - Configuration initialization
# - Data retrieval operations
# - Risk calculations
# - Validation results
# - Errors and warnings
```

## Testing

### Unit Tests

```python
import pytest
from app.sub_agents.payee_agent import (
    calculate_risk_score,
    classify_payee,
    PayeeClassification
)

def test_classify_high_volume_business():
    result = classify_payee(
        total_transactions=100,
        payment_methods=["WIRE", "ACH"],
        currencies=["USD"]
    )
    assert result == PayeeClassification.BUSINESS

def test_risk_score_calculation():
    score = calculate_risk_score(
        total_transactions=50,
        rejection_ratio=0.15,
        payment_methods=["WIRE"],
        currencies=["USD"],
        payee_countries=["USA"]
    )
    assert 0 <= score <= 100
```

### Integration Tests

```python
def test_agent_end_to_end():
    from app.sub_agents.payee_agent import payee_agent

    state = {"payee_id": "TEST_PAYEE_001"}
    result = payee_agent.run(state=state)

    assert "output" in result.state
    assert "risk_level" in result.state["output"]
    assert "payee_classification" in result.state["output"]
```

## Performance Considerations

- **Query Optimization**: Aggregation done in BigQuery for efficiency
- **Caching**: Consider caching frequent payee analyses
- **Batch Processing**: For multiple payees, implement parallel processing
- **Cost Management**: BigQuery queries are metered; monitor usage

## Security Best Practices

1. **SQL Injection Prevention**: All queries use parameterization
2. **Access Control**: Relies on GCP IAM for BigQuery access
3. **Data Privacy**: Logs exclude sensitive transaction details
4. **Environment Secrets**: Never hardcode credentials

## Maintenance

### Adding New Risk Factors

1. Update `RiskThresholds` in `config.py`
2. Modify `calculate_risk_score()` in `utils.py`
3. Update agent instructions in `payee_agent.py`
4. Add tests for new logic

### Updating Classification Logic

1. Modify `classify_payee()` in `utils.py`
2. Update enums in `config.py` if needed
3. Adjust agent instructions
4. Update documentation

## Best Practices Implemented

✅ **Type Safety**: Full type hints and TypedDict schemas  
✅ **Error Handling**: Custom exceptions and graceful degradation  
✅ **Logging**: Structured logging for observability  
✅ **Configuration**: Environment-based with validation  
✅ **Documentation**: Comprehensive docstrings (Google style)  
✅ **Modularity**: Clear separation of concerns  
✅ **Testability**: Isolated, testable components  
✅ **Security**: Parameterized queries, no hardcoded secrets  
✅ **Observability**: Callbacks for monitoring  
✅ **Maintainability**: Clear code structure and naming

## Troubleshooting

### Common Issues

**Issue**: `ValueError: GOOGLE_CLOUD_PROJECT environment variable is required`  
**Solution**: Set required environment variables in `.env` file

**Issue**: `PayeeDataError: No transaction data found`  
**Solution**: Verify payee_id exists in database and has transactions

**Issue**: `ImportError: Failed to import BigQuery agent`  
**Solution**: Ensure bigquery_agent module is properly configured

**Issue**: Missing output fields warning  
**Solution**: Check agent instructions and state population logic

## Contributing

When extending this agent:

1. Follow existing code patterns
2. Add type hints to all functions
3. Include docstrings (Google style)
4. Add logging at key points
5. Write tests for new functionality
6. Update this README

## License

Copyright 2025 - Licensed under Apache 2.0

## Contact

For questions or issues, contact the Agent Architecture team.

---

**Version**: 1.0.0  
**Last Updated**: December 15, 2025  
**Maintainer**: Agent Architect
