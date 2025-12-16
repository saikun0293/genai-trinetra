#!/bin/bash
set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}
REGION=${REGION:-us-central1}
SERVICE_NAME="tri-netra-frontend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Get backend URL if deploying both
BACKEND_URL=${BACKEND_URL:-""}

echo "================================================"
echo "Deploying Frontend to Cloud Run"
echo "================================================"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
if [ -n "${BACKEND_URL}" ]; then
  echo "Backend URL: ${BACKEND_URL}"
fi
echo "================================================"

cd frontend

# Update .env.production with backend URL if provided
if [ -n "${BACKEND_URL}" ]; then
  echo "VITE_API_URL=${BACKEND_URL}" > .env.production
  echo "Updated .env.production with backend URL"
fi

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
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --concurrency 80 \
  --min-instances 0 \
  --max-instances 10 \
  --project ${PROJECT_ID}

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --region ${REGION} \
  --format 'value(status.url)' \
  --project ${PROJECT_ID})

cd ..

echo "================================================"
echo "✅ Frontend deployed successfully!"
echo "URL: ${SERVICE_URL}"
echo "================================================"
