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
Custom FastAPI server that exposes both the ADK agent and custom API endpoints.

This module demonstrates how to:
1. Get the base FastAPI app with agent endpoints from ADK
2. Add custom REST API endpoints to the same server
3. Run everything together on a single port

Usage:
    Local: python -m app.api_server
    Or: uvicorn app.api_server:app --host 0.0.0.0 --port 8000
"""

import logging
import os
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.adk.cli.fast_api import get_fast_api_app
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_SERVICE_URI = "sqlite:///./sessions.db"  # For local dev
ALLOWED_ORIGINS = ["http://localhost:*", "http://127.0.0.1:*", "*"]
SERVE_WEB_INTERFACE = False  # Set to True to serve ADK web UI

# =============================================================================
# Get the base FastAPI app from ADK
# This includes all agent endpoints: /run, /run_sse, /list-apps, etc.
# =============================================================================

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# Add CORS middleware for development (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("ADK FastAPI app initialized with custom endpoints")

# =============================================================================
# Custom API Endpoints
# Add your own REST endpoints below alongside the agent endpoints
# =============================================================================


# Example: Health check endpoint
@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint for monitoring.
    
    Returns:
        Health status of the service
    """
    return {"status": "healthy", "service": "adk-agent-api"}


# Example: Get service info
@app.get("/api/info")
async def get_info() -> dict[str, Any]:
    """
    Get information about the API service.
    
    Returns:
        Service metadata
    """
    return {
        "service": "GenAI Hackathon Agent API",
        "version": "1.0.0",
        "agent_endpoints": {
            "stream_query": "/run_sse",
            "query": "/run",
            "list_apps": "/list-apps",
            "create_session": "/apps/{app_name}/users/{user_id}/sessions",
        },
        "custom_endpoints": {
            "health": "/health",
            "info": "/api/info",
            "transactions": "/api/transactions",
        },
    }


# Example: Pydantic models for custom endpoints
class TransactionRequest(BaseModel):
    transaction_id: str
    amount: float
    currency: str
    payee_country: str
    vendor_country: str
    payment_method: str
    payment_purpose: str


class TransactionResponse(BaseModel):
    transaction_id: str
    status: str
    risk_score: float | None = None
    message: str


# Example: Custom transaction validation endpoint
@app.post("/api/transactions/validate")
async def validate_transaction(
    transaction: TransactionRequest,
) -> TransactionResponse:
    """
    Custom endpoint to validate a transaction.
    
    This is separate from the agent interaction and provides
    a direct REST API for transaction validation.
    
    Args:
        transaction: Transaction details to validate
        
    Returns:
        Validation result
    """
    logger.info(f"Validating transaction: {transaction.transaction_id}")
    
    # Example validation logic
    if transaction.amount < 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    # Simulate risk scoring
    risk_score = 0.3  # In reality, this would come from your risk engine
    
    return TransactionResponse(
        transaction_id=transaction.transaction_id,
        status="validated",
        risk_score=risk_score,
        message="Transaction validated successfully",
    )


# Example: Batch transaction endpoint
@app.post("/api/transactions/batch")
async def process_batch_transactions(
    transactions: list[TransactionRequest],
) -> dict[str, Any]:
    """
    Process multiple transactions in batch.
    
    Args:
        transactions: List of transactions to process
        
    Returns:
        Batch processing results
    """
    logger.info(f"Processing batch of {len(transactions)} transactions")
    
    results = []
    for txn in transactions:
        results.append({
            "transaction_id": txn.transaction_id,
            "status": "processed",
        })
    
    return {
        "total": len(transactions),
        "processed": len(results),
        "results": results,
    }


# Example: Get transaction history (mock endpoint)
@app.get("/api/transactions/{transaction_id}")
async def get_transaction(transaction_id: str) -> dict[str, Any]:
    """
    Retrieve transaction details by ID.
    
    Args:
        transaction_id: The transaction identifier
        
    Returns:
        Transaction details
    """
    logger.info(f"Fetching transaction: {transaction_id}")
    
    # Mock response - in production, this would query your database
    return {
        "transaction_id": transaction_id,
        "amount": 1000.00,
        "currency": "USD",
        "status": "completed",
        "timestamp": "2025-12-15T10:30:00Z",
    }


# Example: Agent invocation endpoint (custom wrapper)
@app.post("/api/agent/analyze")
async def analyze_with_agent(transaction: TransactionRequest) -> dict[str, Any]:
    """
    Custom endpoint that wraps agent invocation.
    
    This demonstrates how you can create custom endpoints that
    internally use the agent while providing a different API contract.
    
    Args:
        transaction: Transaction to analyze
        
    Returns:
        Analysis results
    """
    logger.info(f"Analyzing transaction with agent: {transaction.transaction_id}")
    
    # Here you could:
    # 1. Preprocess the transaction data
    # 2. Invoke the agent programmatically
    # 3. Post-process the agent's response
    # 4. Return a custom response format
    
    return {
        "transaction_id": transaction.transaction_id,
        "analysis": "Agent analysis would go here",
        "recommendation": "Proceed with caution",
        "note": "Use /run_sse endpoint for actual agent interaction",
    }


# =============================================================================
# Main entry point
# =============================================================================

if __name__ == "__main__":
    # Use the PORT environment variable for Cloud Run compatibility
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"Starting API server on port {port}")
    logger.info(f"Agent endpoints available at: http://0.0.0.0:{port}/docs")
    logger.info(f"Custom endpoints available at: http://0.0.0.0:{port}/api/*")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
