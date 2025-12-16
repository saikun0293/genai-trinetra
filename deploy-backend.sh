#!/bin/bash
set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}
REGION=${REGION:-us-central1}
SERVICE_NAME="tri-netra-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "================================================"
echo "Deploying Backend to Cloud Run"
echo "================================================"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "================================================"

# Ensure we're in the project root
cd "$(dirname "$0")"

# Build and push the Docker image
echo "Building Docker image..."
gcloud builds submit --tag ${IMAGE_NAME} --project ${PROJECT_ID}

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --concurrency 80 \
  --min-instances 1 \
  --max-instances 10 \
  --project ${PROJECT_ID}

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --region ${REGION} \
  --format 'value(status.url)' \
  --project ${PROJECT_ID})

echo "================================================"
echo "✅ Backend deployed successfully!"
echo "URL: ${SERVICE_URL}"
echo "================================================"
echo ""
echo "API endpoints available:"
echo "  - ${SERVICE_URL}/docs (Swagger UI)"
echo "  - ${SERVICE_URL}/run (Agent endpoint)"
echo "  - ${SERVICE_URL}/getTransactions"
echo "  - ${SERVICE_URL}/analysis/{transaction_id}"
echo "  - ${SERVICE_URL}/updateApprovalStatus"
echo "================================================"
echo ""
echo "To deploy frontend with this backend:"
echo "  BACKEND_URL=${SERVICE_URL} bash deploy-frontend.sh"
echo "================================================"
