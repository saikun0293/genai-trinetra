import asyncio
import ast
import json
import logging
import os
from google.cloud import pubsub_v1
from google.adk.runners import InMemoryRunner
from google.genai import types
from agent import root_orchestrator_agent
from app_utils.telemetry import setup_telemetry
from app_utils.typing import Feedback

logging.basicConfig(level=logging.INFO)
logger = logging. getLogger(__name__)

PROJECT_ID = os.environ.get("PROJECT_ID", "ccibt-hack25ww7-714")
SUBSCRIPTION_NAME = os.environ.get("SUBSCRIPTION_NAME", "bigquery-insert-topic-sub")
APP_NAME = "app"
USER_ID = "113437527361240185667"

# Initialize runner globally
runner = InMemoryRunner(
    agent=root_orchestrator_agent,
    app_name=APP_NAME,
)

# Track processed transactions
processed_transactions = set()


def parse_message_data(raw_data:  str) -> dict:
    """Parse message data that could be JSON or Python dict string."""
    # Remove outer quotes if present (e.g., "'{'key': 'value'}'" -> "{'key': 'value'}")
    data = raw_data. strip()
    if data.startswith('"') and data.endswith('"'):
        data = data[1:-1]
    
    # Try JSON first
    try: 
        return json.loads(data)
    except json.JSONDecodeError:
        pass
    
    # Try Python literal (for dict strings like "{'key': 'value'}")
    try:
        return ast.literal_eval(data)
    except (ValueError, SyntaxError):
        pass
    
    raise ValueError(f"Could not parse message data: {raw_data[: 100]}...")


async def get_or_create_session(transaction_id: str):
    """Get existing session or create a new one."""
    existing_session = await runner.session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=transaction_id,
    )
    
    if existing_session:
        logger.info(f"Found existing session for transaction:  {transaction_id}")
        return existing_session, False
    
    logger.info(f"Creating new session for transaction: {transaction_id}")
    new_session = await runner.session_service. create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=transaction_id,
    )
    return new_session, True


async def process_workflow_async(workflow_data: dict) -> str:
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
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session. id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content. parts:
                if hasattr(part, 'text') and part.text:
                    response_parts.append(part. text)
                    logger.info(f"Agent ({event.author}): {part.text}")
    
    final_response = "".join(response_parts)
    
    if final_response:
        processed_transactions.add(transaction_id)
        logger.info(f"Transaction {transaction_id} completed")
    
    return final_response


def callback(message):
    """Pub/Sub callback."""
    message_id = message.message_id
    
    try:
        logger. info(f"Received message ID:  {message_id}")
        raw_data = message.data. decode()
        
        # Parse the message (handles both JSON and Python dict strings)
        workflow_data = parse_message_data(raw_data)
        logger.info(f"Parsed workflow_data: {workflow_data.get('transaction_id')}")
        
        transaction_id = workflow_data.get("transaction_id")
        if not transaction_id:
            logger.error("Message missing transaction_id, acking")
            message.ack()
            return
        
        if transaction_id in processed_transactions: 
            logger.info(f"Transaction {transaction_id} already processed, acking")
            message. ack()
            return
        
        response = asyncio.run(process_workflow_async(workflow_data))
        
        logger.info(f"Completed transaction:  {transaction_id}")
        register_feedback({
            "transaction_id": transaction_id,
            "workflow_data": workflow_data,
            "response": response,
            "score": 1.0  # FIX: Added required score field (1.0 = success)
        })
        
        message. ack()
        
    except Exception as e:
        logger.error(f"Error processing message {message_id}: {e}")
        # Register feedback for failed transactions with score 0.0
        transaction_id = None
        try:
            raw_data = message. data.decode()
            workflow_data = parse_message_data(raw_data)
            transaction_id = workflow_data. get("transaction_id")
        except Exception:
            workflow_data = {}
        
        register_feedback({
            "transaction_id":  transaction_id or "unknown",
            "workflow_data":  workflow_data,
            "response": str(e),
            "score": 0.0  # FIX: Score 0.0 for failed transactions
        })
        
        message.ack()  # Ack to prevent infinite retry loop


def register_feedback(feedback: dict) -> None:
    """Log feedback into telemetry with error handling."""
    try:
        # Ensure required fields have defaults
        feedback_with_defaults = {
            "score": 0.0,  # Default score value
            **feedback,    # Override with actual values if provided
        }
        
        feedback_obj = Feedback.model_validate(feedback_with_defaults)
        logger.info(f"Telemetry logged:  {feedback_obj. model_dump()}")
    except Exception as e:
        # Log the feedback anyway even if validation fails
        logger. warning(f"Feedback validation failed: {e}")
        logger.info(f"Raw feedback: {feedback}")


def listen_to_messages() -> None:
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)
    
    flow_control = pubsub_v1.types.FlowControl(max_messages=5)
    
    logger.info(f"Listening for messages on {SUBSCRIPTION_NAME}...")
    streaming_pull_future = subscriber.subscribe(
        subscription_path,
        callback=callback,
        flow_control=flow_control,
    )
    
    try: 
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()
        logger.info("Stopped listening.")


if __name__ == "__main__": 
    setup_telemetry()
    listen_to_messages()