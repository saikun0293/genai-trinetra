#!/bin/bash
set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}
REGION=${REGION:-us-central1}

echo "================================================"
echo "Deploying Full Stack to Cloud Run"
echo "================================================"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "================================================"

# Deploy backend first
echo ""
echo "📦 Step 1: Deploying Backend..."
echo "================================================"
bash deploy-backend.sh

# Get backend URL
BACKEND_URL=$(gcloud run services describe tri-netra-backend \
  --region ${REGION} \
  --format 'value(status.url)' \
  --project ${PROJECT_ID})

echo ""
echo "✅ Backend deployed at: ${BACKEND_URL}"
echo ""

# Deploy frontend with backend URL
echo "📦 Step 2: Deploying Frontend..."
echo "================================================"
BACKEND_URL=${BACKEND_URL} bash deploy-frontend.sh

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe tri-netra-frontend \
  --region ${REGION} \
  --format 'value(status.url)' \
  --project ${PROJECT_ID})

echo ""
echo "================================================"
echo "🎉 Full Stack Deployment Complete!"
echo "================================================"
echo "Frontend: ${FRONTEND_URL}"
echo "Backend:  ${BACKEND_URL}"
echo "API Docs: ${BACKEND_URL}/docs"
echo "================================================"
