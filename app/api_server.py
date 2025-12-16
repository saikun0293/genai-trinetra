"""
Custom FastAPI server that exposes both the ADK agent and custom API endpoints. 

This module demonstrates how to:
1. Get the base FastAPI app with agent endpoints from ADK
2. Add custom REST API endpoints to the same server
3. Run everything together on a single port
4. Auto-start Pub/Sub listener for agent processing

Usage:
    Local: python -m app.api_server
    Or: uvicorn app.api_server:app --host 0.0.0.0 --port 8000
"""

import asyncio
import ast
import json
import logging
import os
import threading
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import InMemoryRunner
from google.cloud import bigquery
from google. cloud import pubsub_v1
from google. genai import types
from pydantic import BaseModel

# Import BigQuery service
from app.bigquery_service import get_transaction_analysis

# Import agent and utilities
from app.agent import root_orchestrator_agent
from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging. getLogger(__name__)
for logger_name in ["urllib3", "google", "grpc", "asyncio", "subscriber-streams", "google_adk", "httpcore", "httpx", "google.auth"]: 
    logging.getLogger(logger_name).setLevel(logging.ERROR)
# =============================================================================
# Configuration
# =============================================================================

AGENT_DIR = os.path. dirname(os.path. abspath(__file__))
SESSION_SERVICE_URI = "sqlite:///./sessions.db"  # For local dev
ALLOWED_ORIGINS = ["http://localhost:*", "http://127.0.0.1:*", "*"]
SERVE_WEB_INTERFACE = False  # Set to True to serve ADK web UI

# Pub/Sub Configuration
PROJECT_ID = os.environ.get("PROJECT_ID", "ccibt-hack25ww7-714")
SUBSCRIPTION_NAME = os. environ.get("SUBSCRIPTION_NAME", "bigquery-insert-topic-sub")
AGENT_APP_NAME = "app"
AGENT_USER_ID = "113437527361240185667"

# =============================================================================
# Global Variables for Pub/Sub Listener
# =============================================================================

agent_runner = None
subscriber_future = None
processed_transactions = set()
processing_results = {}  # Store results for API access

# =============================================================================
# Pub/Sub Message Processing Functions
# =============================================================================


def parse_message_data(raw_data: str) -> dict: 
    """Parse message data that could be JSON or Python dict string."""
    data = raw_data.strip()
    if data. startswith('"') and data.endswith('"'):
        data = data[1:-1]
    
    try:
        return json.loads(data)
    except json. JSONDecodeError: 
        pass
    
    try:
        return ast.literal_eval(data)
    except (ValueError, SyntaxError):
        pass
    
    raise ValueError(f"Could not parse message data:  {raw_data[: 100]}...")


async def get_or_create_session(transaction_id: str):
    """Get existing session or create a new one."""
    existing_session = await agent_runner.session_service.get_session(
        app_name=AGENT_APP_NAME,
        user_id=AGENT_USER_ID,
        session_id=transaction_id,
    )
    
    if existing_session: 
        logger.info(f"Found existing session for transaction:  {transaction_id}")
        return existing_session, False
    
    logger.info(f"Creating new session for transaction: {transaction_id}")
    new_session = await agent_runner.session_service.create_session(
        app_name=AGENT_APP_NAME,
        user_id=AGENT_USER_ID,
        session_id=transaction_id,
    )
    return new_session, True


async def process_workflow_async(workflow_data:  dict) -> str:
    """Process workflow data by invoking the root agent."""
    
    transaction_id = workflow_data.get("transaction_id")
    if not transaction_id:
        raise ValueError("workflow_data must contain 'transaction_id'")
    
    if transaction_id in processed_transactions:
        logger.info(f"Transaction {transaction_id} already processed, skipping")
        return "Already processed"
    
    session, is_new = await get_or_create_session(transaction_id)
    
    workflow_message = json.dumps(workflow_data)
    content = types.Content(
        role='user',
        parts=[types.Part. from_text(text=workflow_message)]
    )
    
    response_parts = []
    async for event in agent_runner.run_async(
        user_id=AGENT_USER_ID,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_parts.append(part.text)
                    logger.info(f"Agent ({event.author}): {part.text[: 100]}...")
    
    final_response = "".join(response_parts)
    
    if final_response:
        processed_transactions.add(transaction_id)
        logger.info(f"Transaction {transaction_id} completed")
        
        # Store result for API access
        processing_results[transaction_id] = {
            "status": "completed",
            "response": final_response,
            "workflow_data": workflow_data
        }
    
    return final_response


def register_feedback(feedback: dict) -> None:
    """Log feedback into telemetry with error handling."""
    try:
        feedback_with_defaults = {
            "score": 0.0,
            **feedback,
        }
        feedback_obj = Feedback. model_validate(feedback_with_defaults)
        logger.info(f"Telemetry logged: {feedback_obj.model_dump()}")
    except Exception as e:
        logger. warning(f"Feedback validation failed: {e}")
        logger.info(f"Raw feedback: {feedback}")


def pubsub_callback(message):
    """Pub/Sub callback - processes incoming messages."""
    message_id = message.message_id
    
    try:
        logger.info(f"Received message ID: {message_id}")
        raw_data = message.data.decode()
        
        workflow_data = parse_message_data(raw_data)
        logger.info(f"Parsed workflow_data: {workflow_data. get('transaction_id')}")
        
        transaction_id = workflow_data.get("transaction_id")
        if not transaction_id: 
            logger.error("Message missing transaction_id, acking")
            message.ack()
            return
        
        if transaction_id in processed_transactions: 
            logger.info(f"Transaction {transaction_id} already processed, acking")
            message.ack()
            return
        
        # Use existing event loop or create new one
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError: 
            loop = asyncio.new_event_loop()
            asyncio. set_event_loop(loop)
        
        # Run the async processing
        if loop.is_running():
            # If loop is already running, use run_coroutine_threadsafe
            import concurrent.futures
            future = asyncio.run_coroutine_threadsafe(
                process_workflow_async(workflow_data), 
                loop
            )
            response = future.result(timeout=300)  # 5 minute timeout
        else:
            response = loop.run_until_complete(process_workflow_async(workflow_data))
        
        logger.info(f"Completed transaction:  {transaction_id}")
        register_feedback({
            "transaction_id": transaction_id,
            "workflow_data": workflow_data,
            "response": response,
            "score": 1.0
        })
        
        message. ack()
        
    except Exception as e:
        logger.error(f"Error processing message {message_id}: {e}", exc_info=True)
        message.ack()

def start_pubsub_listener():
    """Start the Pub/Sub listener in a background thread."""
    global subscriber_future
    
    try:
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber. subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)
        
        flow_control = pubsub_v1.types.FlowControl(max_messages=5)
        
        logger.info(f"✓ Starting Pub/Sub listener on {SUBSCRIPTION_NAME}...")
        subscriber_future = subscriber. subscribe(
            subscription_path,
            callback=pubsub_callback,
            flow_control=flow_control,
        )
        
        # Block this thread to keep listening
        subscriber_future.result()
        
    except Exception as e: 
        logger.error(f"Pub/Sub listener error: {e}")


def stop_pubsub_listener():
    """Stop the Pub/Sub listener."""
    global subscriber_future
    if subscriber_future: 
        subscriber_future.cancel()
        logger.info("Pub/Sub listener stopped.")


# =============================================================================
# Application Lifespan Management
# =============================================================================


@asynccontextmanager
async def lifespan(app:  FastAPI):
    """Manage application lifespan - startup and shutdown."""
    global agent_runner
    
    # ===== STARTUP =====
    logger.info("Starting application...")
    
    # Setup telemetry
    setup_telemetry()
    logger.info("✓ Telemetry initialized")
    
    # Initialize the agent runner for Pub/Sub processing
    agent_runner = InMemoryRunner(
        agent=root_orchestrator_agent,
        app_name=AGENT_APP_NAME,
    )
    logger.info("✓ Agent runner initialized")
    
    # Start Pub/Sub listener in background thread
    listener_thread = threading. Thread(target=start_pubsub_listener, daemon=True)
    listener_thread. start()
    logger.info("✓ Pub/Sub listener thread started")
    
    yield
    
    # ===== SHUTDOWN =====
    logger.info("Shutting down application...")
    stop_pubsub_listener()
    logger.info("Application shutdown complete.")


# =============================================================================
# Get the base FastAPI app from ADK with lifespan
# This includes all agent endpoints:  /run, /run_sse, /list-apps, etc.
# =============================================================================

app:  FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
    lifespan=lifespan,  # Add lifespan handler
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

# Initialize BigQuery client
try:
    bq_client = bigquery.Client()
    logger.info("BigQuery client initialized successfully")
except Exception as e:
    logger. warning(f"BigQuery client initialization failed: {e}")
    bq_client = None

# =============================================================================
# Pub/Sub Listener Status Endpoints
# =============================================================================


@app.get("/pubsub/status")
async def pubsub_status() -> dict[str, Any]: 
    """Get Pub/Sub listener status and processed transactions."""
    return {
        "status": "active" if subscriber_future and not subscriber_future.cancelled() else "inactive",
        "subscription":  SUBSCRIPTION_NAME,
        "processed_count": len(processed_transactions),
        "processed_transactions": list(processed_transactions)[-10:],  # Last 10
    }


@app.get("/pubsub/results")
async def pubsub_results() -> dict[str, Any]:
    """Get all processing results from Pub/Sub messages."""
    return {
        "total":  len(processing_results),
        "results": processing_results
    }


@app.get("/pubsub/results/{transaction_id}")
async def get_pubsub_result(transaction_id:  str) -> dict[str, Any]: 
    """Get processing result for a specific transaction."""
    if transaction_id in processing_results: 
        return {
            "success": True,
            "transaction_id":  transaction_id,
            "result": processing_results[transaction_id]
        }
    elif transaction_id in processed_transactions:
        return {
            "success": True,
            "transaction_id": transaction_id,
            "status": "processed",
            "message": "Transaction was processed but result not cached"
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction {transaction_id} not found or not yet processed"
        )


# =============================================================================
# Custom API Endpoints
# Add your own REST endpoints below alongside the agent endpoints
# =============================================================================


# BigQuery endpoint to fetch transactions
@app.get("/getTransactions")
async def get_transactions(
    limit: int = 25,
    offset:  int = 0,
    fetch_all: bool = False
) -> dict[str, Any]:
    """
    Fetch transactions from BigQuery table.
    
    Args:
        limit: Maximum number of transactions to return (optional)
        offset: Number of transactions to skip for pagination (default:  0)
        fetch_all: If True, fetches all transactions ignoring limit (default: True)
    
    Returns:
        List of transactions with all fields and pagination metadata
    """
    if not bq_client: 
        raise HTTPException(
            status_code=503,
            detail="BigQuery client not initialized.  Check credentials."
        )
    
    try: 
        table_id = "ccibt-hack25ww7-714.tri_netra_payments. PaymentsCompliance"
        
        # Build query with optional pagination
        if fetch_all:
            query = f"""
                SELECT *
                FROM `{table_id}`
                ORDER BY transaction_id DESC
            """
            logger.info(f"Fetching ALL transactions from BigQuery table: {table_id}")
        else:
            query = f"""
                SELECT *
                FROM `{table_id}`
                ORDER BY transaction_id DESC
                LIMIT {limit}
                OFFSET {offset}
            """
            logger.info(f"Fetching transactions with limit={limit}, offset={offset}")
        
        query_job = bq_client.query(query)
        results = query_job. result()
        
        # Convert to list of dictionaries
        transactions = []
        for row in results:
            transaction = dict(row)
            # Convert any non-serializable types
            for key, value in transaction.items():
                if hasattr(value, 'isoformat'):
                    transaction[key] = value.isoformat()
            transactions.append(transaction)
        
        logger.info(f"Successfully fetched {len(transactions)} transactions")
        
        # Get total count for pagination info
        count_query = f"SELECT COUNT(*) as total FROM `{table_id}`"
        count_job = bq_client.query(count_query)
        total_count = list(count_job. result())[0]['total']
        
        return {
            "success": True,
            "count": len(transactions),
            "total":  total_count,
            "offset": offset,
            "limit": limit if not fetch_all else None,
            "has_more": (offset + len(transactions)) < total_count if not fetch_all else False,
            "transactions": transactions
        }
        
    except Exception as e: 
        logger.error(f"Error fetching transactions from BigQuery: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch transactions:  {str(e)}"
        )


@app.post("/updateTransactionStatus")
async def update_transaction_status(request: dict[str, Any]) -> dict[str, Any]: 
    """
    Update the approval status of a transaction in BigQuery.
    
    Args: 
        request: Dict containing transaction_id and approval_status
    
    Returns: 
        Success status and updated transaction info
    """
    if not bq_client:
        raise HTTPException(
            status_code=503,
            detail="BigQuery client not initialized.  Check credentials."
        )
    
    try:
        transaction_id = request. get("transaction_id")
        new_status = request. get("approval_status")
        
        if not transaction_id or not new_status:
            raise HTTPException(
                status_code=400,
                detail="Both transaction_id and approval_status are required"
            )
        
        table_id = "ccibt-hack25ww7-714.tri_netra_payments.PaymentsCompliance"
        
        # Update query
        update_query = f"""
            UPDATE `{table_id}`
            SET approval_status = @new_status
            WHERE transaction_id = @transaction_id
        """
        
        job_config = bigquery. QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("new_status", "STRING", new_status),
                bigquery. ScalarQueryParameter("transaction_id", "STRING", transaction_id),
            ]
        )
        
        query_job = bq_client.query(update_query, job_config=job_config)
        query_job.result()  # Wait for the query to complete
        
        logger.info(f"Successfully updated transaction {transaction_id} to status:  {new_status}")
        
        return {
            "success": True,
            "transaction_id":  transaction_id,
            "new_status": new_status,
            "message":  f"Transaction status updated to {new_status}"
        }
        
    except Exception as e: 
        logger.error(f"Error updating transaction status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update transaction status: {str(e)}"
        )


@app.get("/analysis/{transaction_id}")
async def get_analysis(transaction_id:  str) -> dict[str, Any]: 
    """
    Get compliance analysis data for a specific transaction from BigQuery.
    
    Args: 
        transaction_id:  The transaction ID to fetch analysis for
    
    Returns:
        Analysis data including payee, payer, geopolitical, transaction, and critic analysis
    """
    try:
        logger.info(f"Fetching analysis for transaction: {transaction_id}")
        
        analysis_data = get_transaction_analysis(transaction_id)
        
        if not analysis_data: 
            raise HTTPException(
                status_code=404,
                detail=f"No analysis found for transaction: {transaction_id}"
            )
        
        return {
            "success":  True,
            "transaction_id": transaction_id,
            "analysis": analysis_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching analysis for transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch analysis:  {str(e)}"
        )


# Example:  Health check endpoint
@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint for monitoring.
    
    Returns:
        Health status of the service
    """
    return {
        "status": "healthy",
        "service": "adk-agent-api",
        "pubsub_listener":  "active" if subscriber_future and not subscriber_future. cancelled() else "inactive"
    }


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
            "stream_query":  "/run_sse",
            "query":  "/run",
            "list_apps": "/list-apps",
            "create_session": "/apps/{app_name}/users/{user_id}/sessions",
        },
        "custom_endpoints": {
            "health":  "/health",
            "info": "/api/info",
            "transactions": "/getTransactions",
        },
        "pubsub_endpoints": {
            "status": "/pubsub/status",
            "results": "/pubsub/results",
            "result_by_id": "/pubsub/results/{transaction_id}",
        },
    }


# Example:  Pydantic models for custom endpoints
class TransactionRequest(BaseModel):
    transaction_id:  str
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
    logger.info(f"Validating transaction:  {transaction.transaction_id}")
    
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


# Example:  Batch transaction endpoint
@app.post("/api/transactions/batch")
async def process_batch_transactions(
    transactions: list[TransactionRequest],
) -> dict[str, Any]: 
    """
    Process multiple transactions in batch. 
    
    Args:
        transactions:  List of transactions to process
        
    Returns:
        Batch processing results
    """
    logger.info(f"Processing batch of {len(transactions)} transactions")
    
    results = []
    for txn in transactions: 
        results.append({
            "transaction_id": txn. transaction_id,
            "status": "processed",
        })
    
    return {
        "total": len(transactions),
        "processed": len(results),
        "results": results,
    }


# Example:  Get transaction history (mock endpoint)
@app.get("/api/transactions/{transaction_id}")
async def get_transaction(transaction_id: str) -> dict[str, Any]:
    """
    Retrieve transaction details by ID.
    
    Args: 
        transaction_id:  The transaction identifier
        
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


# Example:  Agent invocation endpoint (custom wrapper)
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
    # 2.  Invoke the agent programmatically
    # 3. Post-process the agent's response
    # 4. Return a custom response format
    
    return {
        "transaction_id": transaction. transaction_id,
        "analysis": "Agent analysis would go here",
        "recommendation": "Proceed with caution",
        "note": "Use /run_sse endpoint for actual agent interaction",
    }


# =============================================================================
# Main entry point
# =============================================================================

if __name__ == "__main__":
    # Use the PORT environment variable for Cloud Run compatibility
    port = int(os.environ. get("PORT", 8000))
    
    logger.info(f"Starting API server on port {port}")
    logger.info(f"Agent endpoints available at: http://0.0.0.0:{port}/docs")
    logger.info(f"Custom endpoints available at: http://0.0.0.0:{port}/api/*")
    logger.info(f"Pub/Sub listener will start automatically")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )