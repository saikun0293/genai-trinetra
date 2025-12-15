# Geopolitics Compliance Agent

## Overview
This agent analyzes financial transactions for compliance based on geopolitical factors, payment methods, transaction timing, and payment purposes. It uses real-time Google Search to ground its analysis in current events, regulations, and fraud trends.

## Features

### Analysis Dimensions
1. **Country Analysis**: Evaluates both payee and vendor countries for sanctions, regulations, and geopolitical risks
2. **Payment Method Analysis**: Assesses payment method security, fraud trends, and compliance status
3. **Time Analysis**: Reviews transaction timing for unusual patterns or compliance concerns
4. **Purpose Analysis**: Validates payment purpose legitimacy and checks for fraud patterns

### Key Capabilities
- Real-time information gathering via Google Search
- Compliance-focused analysis based on current regulations
- Structured JSON output for downstream processing
- No risk scoring (analysis only - scoring done by critique agent)

## Usage

### Integration Example

```python
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from app.sub_agents.geopolitics_agent.agent import root_agent as geopolitics_agent

# Create session with transaction data
session_service = InMemorySessionService()
await session_service.create_session(
    app_name="compliance_app",
    user_id="reviewer_001",
    session_id="tx_review_001"
)

# Set transaction data in session state
session = await session_service.get_session(
    app_name="compliance_app",
    user_id="reviewer_001",
    session_id="tx_review_001"
)
session.state["transaction_data"] = {
    "transaction_id": "c75e81cd-127f-4164-ae72-f2edbb952067",
    "payment_time": "43:32.2",
    "payee_country": "Canada",
    "vendor_country": "Australia",
    "payment_method": "Bank Transfer",
    "payment_purpose": "Payroll",
    "payment_currency": "USD",
    "payment_amount": 517.18,
    "vendor_industry": "Cryptocurrency Trading"
}

# Run the agent
runner = Runner(
    agent=geopolitics_agent,
    app_name="compliance_app",
    session_service=session_service
)

async for event in runner.run_async(
    user_id="reviewer_001",
    session_id="tx_review_001",
    new_message="Analyze this transaction for compliance"
):
    print(event)

# Retrieve analysis from state
analysis = session.state.get("compliance_analysis")
```

### Output Structure

The agent saves its analysis to session state under the key `compliance_analysis` with the following structure:

```json
{
  "country_analysis": {
    "payee_country": "Canada",
    "payee_country_findings": "...",
    "vendor_country": "Australia",
    "vendor_country_findings": "...",
    "cross_border_risks": "...",
    "sanctions_or_restrictions": "No",
    "regulatory_concerns": []
  },
  "payment_method_analysis": {
    "method": "Bank Transfer",
    "security_assessment": "...",
    "fraud_trends": "...",
    "compliance_status": "Compliant",
    "recommendations": []
  },
  "time_analysis": {
    "transaction_time": "43:32.2",
    "time_assessment": "...",
    "time_zone_considerations": "...",
    "timing_risks": []
  },
  "purpose_analysis": {
    "stated_purpose": "Payroll",
    "purpose_legitimacy": "...",
    "common_fraud_patterns": "...",
    "industry_alignment": "...",
    "purpose_risks": []
  },
  "overall_assessment": {
    "key_findings": [],
    "compliance_concerns": [],
    "positive_indicators": [],
    "recommended_actions": []
  },
  "search_sources": [
    {
      "query": "Canada cryptocurrency trading regulations 2025",
      "key_finding": "..."
    }
  ]
}
```

## Integration with Critique Agent

This agent is designed to work in conjunction with a critique agent that will:
1. Read the `compliance_analysis` from session state
2. Evaluate the findings
3. Assign risk scores
4. Make approval/rejection recommendations

The separation ensures:
- Clear separation of concerns (analysis vs. scoring)
- Reusable analysis for multiple review workflows
- Audit trail of factual findings vs. scoring decisions

## Configuration

### Environment Variables
Create a `.env` file in this directory:

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True
```

### Model Configuration
The agent uses `gemini-2.5-pro` for optimal reasoning and search capabilities. You can adjust this in [agent.py](agent.py):

```python
root_agent = Agent(
    model='gemini-2.5-pro',  # Change model here
    # ... other config
)
```

## Testing

### Local Testing Script

```python
# filepath: test_geopolitics_agent.py
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from app.sub_agents.geopolitics_agent.agent import root_agent

async def test_agent():
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session"
    )
    
    session = await session_service.get_session(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session"
    )
    
    # Sample transaction
    session.state["transaction_data"] = {
        "transaction_id": "c75e81cd-127f-4164-ae72-f2edbb952067",
        "payment_time": "43:32.2",
        "payee_country": "Canada",
        "vendor_country": "Australia",
        "payment_method": "Bank Transfer",
        "payment_purpose": "Payroll",
        "payment_currency": "USD",
        "payment_amount": 517.18,
        "vendor_industry": "Cryptocurrency Trading"
    }
    
    runner = Runner(
        agent=root_agent,
        app_name="test_app",
        session_service=session_service
    )
    
    print("Running geopolitics compliance analysis...")
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message="Analyze this transaction for compliance"
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text)
    
    print("\n=== Analysis Result ===")
    analysis = session.state.get("compliance_analysis")
    if analysis:
        import json
        print(json.dumps(analysis, indent=2))
    else:
        print("No analysis found in session state")

if __name__ == "__main__":
    asyncio.run(test_agent())
```

Run: `uv run python test_geopolitics_agent.py`

## Dependencies

All dependencies are managed via the parent project's `pyproject.toml`. This agent uses:
- `google-adk` - Agent Development Kit
- `google-cloud-logging` - For structured logging
- Standard Google Cloud authentication

## Best Practices

1. **Always set transaction_data in state** before invoking the agent
2. **Monitor search queries** to ensure relevant information is retrieved
3. **Review search_sources** in output to understand analysis basis
4. **Update prompt periodically** to reflect new compliance requirements
5. **Log all analyses** for audit trails

## Troubleshooting

### Agent not finding transaction data
- Ensure `transaction_data` is set in session state before agent runs
- Check that all required fields are present in the transaction object

### Poor search results
- Review the agent's search queries in the output
- Adjust the prompt to generate more specific queries
- Consider the current date/time relevance of searches

### Analysis not saved to state
- Verify `output_key='compliance_analysis'` is set in agent config
- Check agent logs for errors during execution
- Ensure session state is properly initialized