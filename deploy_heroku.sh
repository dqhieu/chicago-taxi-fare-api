#!/bin/bash
# Chicago Taxi Fare API - Heroku Deployment Script

set -e

echo "🟣 HEROKU DEPLOYMENT - CHICAGO TAXI FARE API"
echo "============================================="

# Configuration
APP_NAME="chicago-taxi-fare-api"
REGION="us"

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Install it first:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Login check
if ! heroku auth:whoami &> /dev/null; then
    echo "🔐 Please login to Heroku first:"
    heroku login
fi

echo "🚀 Step 1: Creating Heroku app..."
heroku create $APP_NAME --region $REGION || echo "ℹ️  App may already exist"

echo "🔧 Step 2: Setting environment variables..."
heroku config:set -a $APP_NAME \
    MODEL_PATH="models/" \
    LOG_LEVEL="info" \
    SECRET_KEY="$(openssl rand -hex 32)" \
    WEB_CONCURRENCY="4"

echo "📦 Step 3: Adding buildpacks..."
heroku buildpacks:set heroku/python -a $APP_NAME

echo "🎯 Step 4: Deploying application..."
git add .
git commit -m "Deploy Chicago Taxi Fare API to Heroku" || echo "ℹ️  No changes to commit"

# Deploy to Heroku
git push heroku main || git push heroku master

echo "🌐 Step 5: Opening application..."
heroku open -a $APP_NAME

echo "📊 Step 6: Testing deployment..."
APP_URL=$(heroku info -a $APP_NAME --json | jq -r '.app.web_url')
echo "Testing health endpoint: ${APP_URL}health"

if curl -f "${APP_URL}health"; then
    echo "✅ Deployment successful!"
    echo "🎯 API URL: $APP_URL"
    echo "📊 Health: ${APP_URL}health"
    echo "🔮 Predict: ${APP_URL}predict"
else
    echo "❌ Deployment failed. Check logs:"
    heroku logs --tail -a $APP_NAME
fi

echo ""
echo "📋 USEFUL COMMANDS:"
echo "   heroku logs --tail -a $APP_NAME        # View logs"
echo "   heroku ps -a $APP_NAME                 # Check dynos"
echo "   heroku config -a $APP_NAME             # View config"
echo "   heroku restart -a $APP_NAME            # Restart app"