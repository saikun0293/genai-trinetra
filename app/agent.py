# ruff: noqa
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Main agent module for the compliance orchestrator.
This module defines the root agent that coordinates parallel compliance analysis.
"""

import logging
import os
import google.auth
from google.adk.apps.app import App
from google.adk.agents import ParallelAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from app.sub_agents.geopolitics_agent import geopolitics_agent
from app.sub_agents.payee_vendor_agent import payee_agent
from app.sub_agents.payer_validation_agent import payer_validation_agent
from app.sub_agents.transaction_agent import transaction_agent
from app.sub_agents.critique_agent import critique_agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents import Agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Google Cloud authentication and environment
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT", project_id)
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

logger.info(f"Compliance orchestrator initialized with project: {project_id}, location: {os.environ['GOOGLE_CLOUD_LOCATION']}")


def log_agent_outputs(callback_context: CallbackContext) -> None:
    """Log session state after parallel agents complete to verify outputs are stored."""
    logger.info("=" * 80)
    logger.info("COMPLIANCE ANALYZER - Session State After Parallel Execution")
    logger.info("=" * 80)
    
    state = callback_context.session.state
    agent_keys = ["payee_agent", "payer_validation_agent", "geopolitics_agent", "transaction_agent"]
    
    for key in agent_keys:
        if key in state:
            output_preview = str(state[key])[:200] if state[key] else "None"
            logger.info(f"✓ {key}: Present ({len(str(state[key]))} chars) - {output_preview}...")
        else:
            logger.warning(f"✗ {key}: MISSING from session state")
    
    logger.info("=" * 80)



# Parallel agent that runs all compliance analysis agents concurrently
compliance_analyzer = ParallelAgent(
    name="compliance_analyzer",
    description="Runs multiple compliance analysis agents in parallel to assess different aspects of a transaction simultaneously.",
    sub_agents=[payee_agent, payer_validation_agent, geopolitics_agent, transaction_agent],
    after_agent_callback=log_agent_outputs  # Log state after parallel execution completes
)

logger.info("Compliance analyzer (parallel agent) initialized successfully")

# Root agent that orchestrates the entire compliance workflow
compliance_orchestrator = SequentialAgent(
    name="compliance_orchestrator",
    description="Orchestrates the end-to-end compliance check by running analysis agents in parallel, then synthesizing with a critique agent.",
    sub_agents=[compliance_analyzer, critique_agent]
)

ROOT_ORCHESTRATOR_PROMPT = """
You are the root orchestrator managing compliance and fraud analysis for payment transactions.

Your responsibility is to coordinate parallel analysis of incoming transactions and synthesize findings into a comprehensive risk report.

## Transaction Input

You will receive a transaction object containing:
- payer_id: Identifier for the payment originator
- payee_id: Identifier for the payment recipient
- transaction_id: Unique transaction identifier
- payment_amount: Transaction amount
- payment_currency: Currency
- payment_method: ACH, Wire, Check, etc.
- payment_purpose: Stated purpose of payment
- vendor_id: Vendor receiving the payment
- vendor_industry: Industry classification
- approval_status: APPROVED or REJECTED
- Additional metadata (timestamps, geolocation, etc.)

## Parallel Analysis Workflow

Four specialist agents will run **in parallel** to analyze this transaction from different angles:

### 1. **Payee/Vendor Agent**
- Analyzes vendor fraud patterns tied to the payee
- Outputs: Vendor baseline metrics, high-value transaction patterns, suspicious payer activity, temporal anomalies
- Key findings: Fraud indicators, suspicious payers, risk patterns

### 2. **Payer Validation Agent**
- Analyzes payer behavioral anomalies and deviations
- Outputs: Payer baseline profile, velocity patterns, identified anomalies, rejection patterns
- Key findings: Behavioral deviations, outliers, frequency anomalies

### 3. **Geopolitics Agent**
- Analyzes geopolitical and sanctions compliance risks
- Outputs: Geographic exposure, sanctions risk, political compliance issues
- Key findings: Country risks, compliance violations, regulatory concerns

### 4. **Transaction Agent**
- Analyzes transaction-level details and patterns
- Outputs: Payment method analysis, purpose consistency, timing patterns
- Key findings: Method anomalies, purpose red flags, suspicious timing

## Sequential Synthesis (After Parallel Phase)

### 5. **Critique Agent**
- Receives outputs from all four parallel agents
- Synthesizes findings into unified risk report
- Outputs: Consolidated risk assessment, priority findings, final recommendations

## Your Role (Root Orchestrator)

You do NOT need to invoke agents manually. The framework will:
1. Execute the four analysis agents **in parallel** automatically
2. Collect all four outputs into session state
3. Pass those outputs to the critique agent for synthesis
4. Return the final compliance report

Your job is to:
- Accept the incoming transaction
- Ensure all agents have the necessary transaction context
- Let the parallel execution complete
- Pass the synthesized findings downstream

## Output Structure

The final compliance report will contain:
- Executive Summary (risk score, key findings)
- Payee/Vendor Analysis (fraud patterns, suspicious activity)
- Payer Analysis (behavioral anomalies, deviations)
- Geopolitical Assessment (country risks, sanctions compliance)
- Transaction Analysis (method anomalies, timing concerns)
- Consolidated Risk Assessment (overall compliance risk)
- Recommendations (actions, escalations)

## Critical Instructions

1. **Coordinate, Don't Duplicate**: All four analysis agents run in parallel; your role is orchestration, not analysis
2. **Preserve Independence**: Each agent operates independently and contributes unique perspectives
3. **Trust Parallel Execution**: Do not wait sequentially or interfere with parallel agent execution
4. **Let Critique Synthesize**: The critique agent handles all synthesis and consolidation
5. **Return Final Output**: Pass through the synthesized report without modification

## Decision Logic

For each incoming transaction:
1. **Extract transaction_id, payer_id, payee_id, vendor_id, payment_amount, payment_currency, payment_method, payment_purpose, vendor_industry, approval_status**
2. **Trigger parallel analysis**: All four agents begin analysis simultaneously
3. **Monitor completion**: Wait for all four to complete (session state will show all outputs)
4. **Invoke critique agent**: Pass all four outputs to critique agent
5. **Return synthesis**: Deliver the final compliance report

You are the orchestrator managing the flow, not a direct analyzer. Coordinate; don't interpret.
"""

compliance_orchestrator_agent = AgentTool(agent = compliance_orchestrator)
# Create the App instance - this is what gets loaded by ADK and deployed

root_orchestrator_agent = Agent(
    name="root_orchestrator_agent",
    model="gemini-2.5-flash",
    description="The main orchestrator that delegates tasks to specialist agents for compliance",
    instruction=ROOT_ORCHESTRATOR_PROMPT,
    tools=[compliance_orchestrator_agent]
)

app = App(
    name="app",
    root_agent=root_orchestrator_agent
)

logger.info("Compliance application initialized successfully")
