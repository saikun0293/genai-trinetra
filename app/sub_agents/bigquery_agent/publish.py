from google.cloud import pubsub_v1
import os
import json
import uuid
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set your Google Cloud project ID and topic name
PROJECT_ID = "ccibt-hack25ww7-714"
TOPIC_NAME = "bigquery-insert-topic"

def publish_message(data):
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)
        message_data = json.dumps(data)

        future = publisher.publish(topic_path, message_data.encode("utf-8"))
        logger.info(f"Published message to {TOPIC_NAME}: {future.result()}")
    except Exception as e:
        logger.error(f"Error while publishing message: {e}", exc_info=True)

def insert_and_publish():
    """
    Simulate record insertion into BigQuery and publish to Pub/Sub.
    Generates a unique UUID for each transaction to ensure uniqueness.
    """
    # Generate a unique UUID for each transaction
    transaction_id = str(uuid.uuid4())
    
    record = {
        "transaction_id": transaction_id,
        "payment_time": "50:32.2",
        "payer_id": "COMP0030",
        "payee_id": "PAYEE0319",
        "payment_amount": 22755.21,
        "payment_currency": "GBP",
        "payment_method": "Check",
        "payment_purpose": "Marketing Campaign",
        "vendor_id": "VEND0390",
        "payee_country": "Canada",
        "vendor_country": "Canada",
        "vendor_industry": "Manufacturing",
    }
    
    logger.info(f"Generated transaction with ID: {transaction_id}")
    logger.info(f"Record details: {json.dumps(record, indent=2)}")
    logger.info(f"Inserting record into BigQuery table...")

    # Publish the record to Pub/Sub
    publish_message(record)

if __name__ == "__main__":
    insert_and_publish()