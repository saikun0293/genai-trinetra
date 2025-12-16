# Deployment Guide

## Prerequisites

1. Install Google Cloud SDK
2. Authenticate: `gcloud auth login`
3. Set project: `gcloud config set project YOUR_PROJECT_ID`
4. Enable APIs:

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

## Quick Start - Deploy Everything

```bash
# Deploy both frontend and backend (recommended)
bash deploy-fullstack.sh
```

## Individual Deployments

### Backend Only

```bash
# Initial deployment
bash deploy-backend.sh

# Redeploy after changes
bash deploy-backend.sh
```

### Frontend Only

```bash
# Initial deployment (auto-detects backend URL)
bash deploy-frontend.sh

# Or specify backend URL manually
BACKEND_URL=https://your-backend-url.run.app bash deploy-frontend.sh

# Redeploy after changes
bash deploy-frontend.sh
```

## Windows PowerShell Commands

If bash scripts don't work on Windows, use these commands:

### Backend Deployment

```powershell
# Set your project
$PROJECT_ID = "YOUR_PROJECT_ID"
$REGION = "us-central1"

# Build and deploy backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/tri-netra-backend --project $PROJECT_ID

gcloud run deploy tri-netra-backend `
  --image gcr.io/$PROJECT_ID/tri-netra-backend `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --port 8080 `
  --memory 2Gi `
  --cpu 2 `
  --timeout 300 `
  --min-instances 1 `
  --max-instances 10 `
  --project $PROJECT_ID
```

### Frontend Deployment

```powershell
# Build and deploy frontend
cd frontend

gcloud builds submit --tag gcr.io/$PROJECT_ID/tri-netra-frontend --project $PROJECT_ID

gcloud run deploy tri-netra-frontend `
  --image gcr.io/$PROJECT_ID/tri-netra-frontend `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --port 8080 `
  --memory 512Mi `
  --cpu 1 `
  --timeout 60 `
  --min-instances 0 `
  --max-instances 10 `
  --project $PROJECT_ID

cd ..
```

## Triggering Redeployment

### Any time you make changes:

**Backend changes** → Run: `bash deploy-backend.sh`
**Frontend changes** → Run: `bash deploy-frontend.sh`
**Both changed** → Run: `bash deploy-fullstack.sh`

Deployment takes 3-5 minutes and automatically:

- Builds new Docker image
- Pushes to Google Container Registry
- Updates Cloud Run service with zero downtime

## Getting Deployment URLs

```bash
# Backend URL
gcloud run services describe tri-netra-backend --region us-central1 --format 'value(status.url)'

# Frontend URL
gcloud run services describe tri-netra-frontend --region us-central1 --format 'value(status.url)'
```

## Connecting Frontend to Backend

The frontend automatically uses the backend URL set during deployment. To update:

1. Create `frontend/.env.production`:

```
VITE_API_URL=https://your-backend-url.run.app
```

2. Redeploy frontend:

```bash
bash deploy-frontend.sh
```

## Logs & Monitoring

```bash
# Backend logs
gcloud run services logs read tri-netra-backend --region us-central1

# Frontend logs
gcloud run services logs read tri-netra-frontend --region us-central1
```
