from google.cloud import pubsub_v1
from google.cloud import bigquery
import json
import uuid
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging. INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set your Google Cloud project ID and topic name
PROJECT_ID = "ccibt-hack25ww7-714"
TOPIC_NAME = "bigquery-insert-topic"
DATASET_ID = "tri_netra_payments"
TABLE_ID = "PaymentsCompliance"

# Initialize BigQuery client
bq_client = bigquery.Client(project=PROJECT_ID)


def insert_into_bigquery(record:  dict) -> bool:
    """Insert a record into BigQuery table."""
    try:
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
        errors = bq_client.insert_rows_json(table_ref, [record])
        
        if errors: 
            logger.error(f"BigQuery insert errors: {errors}")
            return False
        
        logger.info(f"✓ Inserted into BigQuery:  {record['transaction_id']}")
        return True
    except Exception as e: 
        logger.error(f"Error inserting into BigQuery: {e}")
        return False


def publish_message(data: dict) -> bool:
    """Publish a message to Pub/Sub topic."""
    try: 
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)
        message_data = json. dumps(data)

        future = publisher. publish(topic_path, message_data. encode("utf-8"))
        logger.info(f"✓ Published to {TOPIC_NAME}:  {future.result()}")
        return True
    except Exception as e:
        logger.error(f"Error publishing message: {e}")
        return False


def insert_and_publish():
    """Insert record into BigQuery and publish to Pub/Sub."""
    
    # =============================================================================
    # EDIT THIS RECORD TO TEST DIFFERENT SCENARIOS
    # =============================================================================
    record = {
        "transaction_id": str(uuid.uuid4()),
        "payment_time": "41:32. 2",
        "payer_id": "COMP0098",
        "payee_id": "PAYEE0076",
        "payment_amount": 950.00,
        "payment_currency": "JPY",
        "payment_method": "Credit Card",
        "payment_purpose": "Rent Payment",
        "vendor_id": "VEND0232",
        "payee_country": "China",
        "vendor_country": "India",
        "vendor_industry": "Shell Corporations",
        "approval_status": "",
        "reject_reason": ""
    }
    # =============================================================================
    
    # Print transaction info
    print(f"\n{'='*60}")
    print(f"Transaction ID:  {record['transaction_id']}")
    print(f"Amount: {record['payment_amount']} {record['payment_currency']}")
    print(f"Industry: {record['vendor_industry']}")
    print(f"Purpose: {record['payment_purpose']}")
    print(f"Route:  {record['payee_country']} → {record['vendor_country']}")
    print(f"{'='*60}\n")
    
    # Insert into BigQuery
    insert_into_bigquery(record)
    
    # Publish to Pub/Sub
    publish_message(record)


if __name__ == "__main__":
    insert_and_publish()