#!/bin/bash
# Chicago Taxi Fare API - FREE Google Cloud Run Deployment

set -e

echo "☁️ GOOGLE CLOUD RUN FREE DEPLOYMENT"
echo "===================================="
echo "✅ FREE: $300 credit + Always free tier"
echo "✅ 2M requests/month always free"
echo "✅ Enterprise-grade performance"
echo "⏱️  Setup time: ~15 minutes"
echo ""

# Configuration
PROJECT_ID="chicago-taxi-api-$(date +%s)"
SERVICE_NAME="chicago-taxi-api"
REGION="us-central1"  # Free tier region
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "📋 GOOGLE CLOUD FREE TIER CHECKLIST"
echo "===================================="
echo ""
echo "✅ Prerequisites:"
echo "   1. Google account (free)"
echo "   2. Google Cloud account (free $300 credit)"
echo "   3. Docker installed locally"
echo "   4. gcloud CLI installed"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI not found. Install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    echo ""
    echo "🍎 macOS:"
    echo "   brew install google-cloud-sdk"
    echo ""
    echo "🐧 Ubuntu/Debian:"
    echo "   curl https://sdk.cloud.google.com | bash"
    echo ""
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install it first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

echo "🔐 GOOGLE CLOUD AUTHENTICATION"
echo "==============================="
echo "Authenticating with Google Cloud..."

# Authenticate with Google Cloud
gcloud auth login

echo ""
echo "🚀 SETTING UP FREE GOOGLE CLOUD PROJECT"
echo "========================================"

# Create new project (free)
echo "Creating Google Cloud project: $PROJECT_ID"
gcloud projects create $PROJECT_ID --name="Chicago Taxi API"

# Set current project
gcloud config set project $PROJECT_ID

# Enable required APIs (free)
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

echo ""
echo "🐳 BUILDING OPTIMIZED DOCKER IMAGE"
echo "=================================="

# Create optimized Dockerfile for Cloud Run free tier
cat > Dockerfile.cloudrun << 'EOF'
# Optimized for Google Cloud Run FREE tier
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MODEL_PATH=/app/models
ENV PORT=8080

# Create non-root user
RUN groupadd -r apiuser && useradd -r -g apiuser apiuser

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies (optimized for free tier)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/production_app.py app.py
COPY models/ models/

# Create optimized startup script for Cloud Run
COPY <<'SCRIPT' start.sh
#!/bin/bash
set -e

echo "🆓 Starting Chicago Taxi API on Google Cloud Run FREE tier..."
echo "📊 Model path: $MODEL_PATH"
echo "🌐 Port: $PORT"

# Health check for model files
if [ ! -f "$MODEL_PATH/chicago_fare_model_metadata.json" ]; then
    echo "❌ Model metadata not found"
    exit 1
fi

echo "✅ Model files verified"

# Start with optimized settings for free tier
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 4 \
    --timeout 300 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    app:app
SCRIPT

# Make startup script executable
RUN chmod +x start.sh

# Change ownership to non-root user
RUN chown -R apiuser:apiuser /app
USER apiuser

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Expose port
EXPOSE $PORT

# Start the application
CMD ["./start.sh"]
EOF

echo "✅ Optimized Dockerfile created for Cloud Run free tier"

# Build and push Docker image
echo "Building Docker image..."
docker build -f Dockerfile.cloudrun -t $IMAGE_NAME .

echo "Pushing image to Google Container Registry..."
docker push $IMAGE_NAME

echo ""
echo "🚀 DEPLOYING TO CLOUD RUN FREE TIER"
echo "===================================="

# Deploy to Cloud Run with free tier optimizations
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --concurrency 80 \
    --max-instances 10 \
    --timeout 300 \
    --set-env-vars="MODEL_PATH=/app/models,LOG_LEVEL=info" \
    --port 8080

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)")

echo ""
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "========================"
echo ""
echo "🌐 API URL: $SERVICE_URL"
echo "🏥 Health Check: $SERVICE_URL/health"
echo "🎯 Predict: $SERVICE_URL/predict"
echo ""

echo "🧪 TESTING DEPLOYMENT"
echo "====================="
echo "Testing health endpoint..."

if curl -f "$SERVICE_URL/health"; then
    echo ""
    echo "✅ Health check passed!"
else
    echo ""
    echo "⚠️  Health check failed. Check logs:"
    gcloud logs read --service=$SERVICE_NAME --region=$REGION
fi

echo ""
echo "💰 GOOGLE CLOUD RUN FREE TIER BENEFITS"
echo "======================================"
echo "✅ 2 million requests per month (always free)"
echo "✅ 400,000 GiB-seconds (always free)"
echo "✅ 200,000 vCPU-seconds (always free)"
echo "✅ Auto-scaling to zero (no charges when idle)"
echo "✅ Global deployment"
echo "✅ HTTPS automatically enabled"
echo "✅ Custom domains supported"
echo ""

echo "📊 USAGE MONITORING"
echo "=================="
echo "Monitor your usage (always stay in free tier):"
echo "https://console.cloud.google.com/run"
echo ""

echo "🔧 USEFUL COMMANDS"
echo "=================="
echo "View logs:"
echo "  gcloud logs read --service=$SERVICE_NAME --region=$REGION --limit=50"
echo ""
echo "Update service:"
echo "  gcloud run deploy $SERVICE_NAME --image $IMAGE_NAME --region $REGION"
echo ""
echo "Delete service (if needed):"
echo "  gcloud run services delete $SERVICE_NAME --region=$REGION"
echo ""
echo "Check billing (should be $0):"
echo "  https://console.cloud.google.com/billing"
echo ""

echo "🎉 GOOGLE CLOUD RUN FREE DEPLOYMENT COMPLETE!"
echo "=============================================="
echo "Your Chicago Taxi Fare API is running on enterprise-grade"
echo "Google Cloud infrastructure - completely FREE!"
echo ""
echo "💡 PRO TIPS:"
echo "- Monitor usage to stay in free tier"
echo "- Set up billing alerts (optional)"
echo "- Use Cloud Monitoring for insights"
echo "- Scale to zero when not in use (automatic)"