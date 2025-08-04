#!/bin/bash
# Chicago Taxi Fare API - DigitalOcean App Platform Deployment

set -e

echo "🌊 DIGITALOCEAN DEPLOYMENT - CHICAGO TAXI FARE API"
echo "=================================================="

# Configuration
APP_NAME="chicago-taxi-api"
REGION="nyc1"
PLAN="basic-xxs"  # $5/month
GITHUB_REPO=""    # Add your GitHub repo URL

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ DigitalOcean CLI (doctl) not found. Install it first:"
    echo "   https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check authentication
if ! doctl account get &> /dev/null; then
    echo "🔐 Please authenticate with DigitalOcean first:"
    doctl auth init
fi

echo "📋 Creating app specification..."
cat > app.yaml << EOF
name: $APP_NAME
services:
- name: api
  source_dir: /
  github:
    repo: $GITHUB_REPO
    branch: main
    deploy_on_push: true
  run_command: gunicorn --config gunicorn.conf.py api.production_app:app
  environment_slug: python
  instance_count: 2
  instance_size_slug: $PLAN
  http_port: 8000
  health_check:
    http_path: /health
  envs:
  - key: MODEL_PATH
    value: models/
  - key: LOG_LEVEL
    value: info
  - key: WEB_CONCURRENCY
    value: "2"
  - key: SECRET_KEY
    value: $(openssl rand -hex 32)
    type: SECRET
EOF

echo "🚀 Creating DigitalOcean App..."
APP_ID=$(doctl apps create app.yaml --format ID --no-header)

echo "✅ App created with ID: $APP_ID"
echo "🔄 Waiting for deployment to complete..."

# Wait for deployment
while true; do
    STATUS=$(doctl apps get $APP_ID --format Phase --no-header)
    echo "Current status: $STATUS"
    
    if [ "$STATUS" = "ACTIVE" ]; then
        echo "✅ Deployment successful!"
        break
    elif [ "$STATUS" = "ERROR" ]; then
        echo "❌ Deployment failed!"
        doctl apps get $APP_ID
        exit 1
    fi
    
    sleep 30
done

# Get app URL
APP_URL=$(doctl apps get $APP_ID --format LiveURL --no-header)
echo "🌐 App URL: $APP_URL"

echo "📊 Testing deployment..."
if curl -f "${APP_URL}/health"; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
fi

echo ""
echo "📋 USEFUL COMMANDS:"
echo "   doctl apps get $APP_ID                 # View app details"
echo "   doctl apps logs $APP_ID                # View logs"
echo "   doctl apps list                        # List all apps"
echo "   doctl apps delete $APP_ID              # Delete app"
echo ""
echo "🎯 API Endpoints:"
echo "   Health: ${APP_URL}/health"
echo "   Predict: ${APP_URL}/predict"