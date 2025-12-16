from google.cloud import pubsub_v1
import os
import json
# Set your Google Cloud project ID and topic name
PROJECT_ID = "ccibt-hack25ww7-714"
TOPIC_NAME = "bigquery-insert-topic"

def publish_message(data):
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)
        message_data = json.dumps(data)

        future = publisher.publish(topic_path, message_data.encode("utf-8"))
        print(f"Published message: {future.result()}")
    except Exception as e:
        print(f"Error while publishing message: {e}")

def insert_and_publish():
    # Simulate record insertion into BigQuery
    record = {
  "transaction_id": "ba2ec603-c16b-4e1a-943a-47060e42f496",
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
  "approval_status": "REJECTED",
  "reject_reason": "High Value Transaction"
}
    print(f"Inserted record into BigQuery: {record}")

    # Publish the record to Pub/Sub
    publish_message(str(record))

if __name__ == "__main__":
    insert_and_publish()