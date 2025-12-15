# Payee Agent - Analysis-Based Output

## Overview

The Payee Agent now provides **narrative analysis** instead of calculated risk scores. The agent leverages the LLM's analytical capabilities to generate comprehensive, context-aware analysis of payee transaction patterns.

## Key Changes

### Previous Approach (Calculated Metrics)

```python
output = {
    "payee_id": "P12345",
    "payee_summary": "...",
    "payee_trust_level": "HIGH",
    "payee_classification": "BUSINESS",
    "risk_score": 28,
    "risk_level": "LOW",
    "red_flags": ["...", "..."],
    "vendor_summary": "..."
}
```

### New Approach (Narrative Analysis)

```python
output = {
    "analysis": "Comprehensive narrative analysis (3-5 paragraphs)",
    "vendor_analysis": "Separate vendor analysis (if applicable)"
}
```

## Benefits of Analysis-Based Approach

1. **LLM Leverages Context**: The model can provide nuanced insights based on patterns it identifies
2. **Natural Language Output**: Easy to read and understand for non-technical users
3. **Flexible Analysis**: Can adapt analysis depth based on data complexity
4. **Holistic View**: Combines multiple factors into coherent narrative
5. **Simpler State**: Reduced complexity in state management

## State Schema

```python
from typing import Optional, TypedDict

class PayeeAnalysisOutput(TypedDict):
    """Output structure for payee analysis."""
    analysis: str
    vendor_analysis: Optional[str]

class PayeeAgentState(TypedDict):
    """Complete state schema for Payee Agent."""
    payee_id: str  # Input
    output: PayeeAnalysisOutput  # Output
```

## Usage Example

```python
from app.sub_agents.payee_agent import payee_agent

# Run analysis
state = {"payee_id": "P12345"}
result = payee_agent.run(state=state)

# Access the narrative analysis
analysis = result.state["output"]["analysis"]
print(analysis)

# Output example:
# "Payee P12345 demonstrates a well-established business profile with 150
# transactions totaling $450,000 over the analyzed period. The transaction
# history shows consistent high-value payments averaging $3,000 per transaction,
# indicating substantial commercial operations.
#
# The payee operates across two primary markets (USA and UK) and utilizes
# multiple payment methods including wire transfers, ACH, and traditional checks,
# which is typical for businesses managing diverse payment scenarios..."

# Check vendor analysis if available
if result.state["output"]["vendor_analysis"]:
    print("\nVendor Analysis:")
    print(result.state["output"]["vendor_analysis"])
```

## What the Analysis Includes

The agent's narrative analysis covers:

### 1. Transaction Overview

- Total transaction count and volume
- Transaction patterns and frequency
- Payment amount ranges and averages

### 2. Payee Profile

- Classification (Business vs Individual)
- Geographic footprint and operating countries
- Payment method usage and diversity
- Currency patterns

### 3. Risk Indicators

- Rejection rates and patterns
- Reasons for rejections
- Unusual patterns or anomalies
- Geographic risk factors
- Transaction volume concerns

### 4. Trust Assessment

- Overall trustworthiness evaluation
- Consistency and reliability indicators
- Red flags or concerns
- Positive indicators

### 5. Vendor Relationships

- Vendor involvement (if applicable)
- Vendor risk profile
- Cross-border considerations

## Agent Instructions Summary

The agent is instructed to:

1. Query BigQuery for payee transaction history
2. Query vendor data if vendor IDs are found
3. Analyze the data qualitatively (no numeric scoring)
4. Write 3-5 detailed paragraphs covering all aspects
5. Include specific numbers from query results
6. Be analytical, professional, and factual

## Error Handling

If data retrieval fails:

```python
output = {
    "analysis": "ERROR: Unable to retrieve transaction data for payee P12345.
                 Analysis cannot be completed without access to transaction history.
                 Please verify the payee ID and ensure data exists in the system.",
    "vendor_analysis": None
}
```

## Integration

The simplified output makes it easier to:

- Display results in UI (single text field)
- Generate reports (narrative format)
- Log analysis for audit trails
- Chain with other agents (pass analysis as context)

## Comparison: Before vs After

| Aspect               | Calculated Approach       | Analysis Approach     |
| -------------------- | ------------------------- | --------------------- |
| **Output Fields**    | 8 fields                  | 2 fields              |
| **Complexity**       | High (score calculations) | Low (narrative)       |
| **Flexibility**      | Fixed metrics             | Adaptive analysis     |
| **Readability**      | Requires interpretation   | Directly readable     |
| **LLM Utilization**  | Minimal                   | Full analytical power |
| **State Management** | Complex schema            | Simple schema         |
| **User Experience**  | Technical metrics         | Natural language      |

## When to Use Each Approach

### Use Analysis-Based (Current):

- When users need to understand "why"
- For compliance and audit reporting
- When analysis nuance matters
- For executive summaries
- When LLM insights add value

### Use Calculated Metrics (Previous):

- When downstream systems need numeric scores
- For automated decision thresholds
- When strict reproducibility is required
- For ML training data
- When regulations require specific metrics

## Migration Note

The utility functions for risk calculation (`utils.py`) are still available if you need programmatic risk scoring for other purposes, but the agent itself now focuses on narrative analysis.

---

**Version**: 2.0.0 (Analysis-Based)  
**Last Updated**: December 15, 2025  
**Maintainer**: Agent Architect