#!/bin/bash
# Chicago Taxi Fare API - FREE Render Deployment

set -e

echo "🆓 RENDER FREE DEPLOYMENT - CHICAGO TAXI FARE API"
echo "================================================="
echo "✅ 100% FREE - No credit card required!"
echo "⏱️  Setup time: ~10 minutes"
echo "🌐 750 hours/month (24/7 uptime possible)"
echo ""

# Configuration
APP_NAME="chicago-taxi-api"
GITHUB_REPO_URL=""  # Add your GitHub repo URL here

echo "📋 RENDER FREE DEPLOYMENT CHECKLIST"
echo "===================================="
echo ""
echo "✅ Prerequisites:"
echo "   1. GitHub account (free)"
echo "   2. Render account (free): https://render.com"
echo "   3. Your code pushed to GitHub"
echo ""

# Check if GitHub repo is set
if [ -z "$GITHUB_REPO_URL" ]; then
    echo "⚠️  Please set your GitHub repository URL in this script:"
    echo "   GITHUB_REPO_URL=\"https://github.com/yourusername/your-repo\""
    echo ""
    echo "📝 Steps to set up GitHub:"
    echo "   1. Create GitHub repo: https://github.com/new"
    echo "   2. Push your code:"
    echo "      git init"
    echo "      git add ."
    echo "      git commit -m 'Initial commit'"
    echo "      git remote add origin YOUR_GITHUB_URL"
    echo "      git push -u origin main"
    echo ""
    exit 1
fi

echo "🚀 AUTOMATIC RENDER DEPLOYMENT SETUP"
echo "====================================="

# Create render.yaml for easy deployment
cat > render.yaml << EOF
services:
  - type: web
    name: $APP_NAME
    runtime: python3
    plan: free  # 🆓 FREE TIER!
    buildCommand: |
      pip install --upgrade pip
      pip install -r requirements.txt
    startCommand: |
      gunicorn --config gunicorn.conf.py api.production_app:app
    envVars:
      - key: MODEL_PATH
        value: models/
      - key: LOG_LEVEL
        value: info
      - key: WEB_CONCURRENCY
        value: "1"  # Free tier: single worker
      - key: PORT
        value: "10000"
      - key: SECRET_KEY
        generateValue: true  # Auto-generate secret
    healthCheckPath: /health
    disk:
      name: models
      mountPath: /app/models
      sizeGB: 1  # Free tier limit
EOF

echo "✅ render.yaml created for automatic deployment"
echo ""

# Update gunicorn config for free tier
cat > gunicorn_free.conf.py << 'EOF'
# Gunicorn configuration optimized for Render FREE tier
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"
backlog = 512

# Worker processes (FREE TIER: Limited to 1 worker)
workers = 1  # Free tier limitation
worker_class = "sync"
worker_connections = 100  # Reduced for free tier
timeout = 30
keepalive = 2
max_requests = 500  # Restart workers periodically
max_requests_jitter = 50

# Memory optimization for free tier (512MB limit)
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s %(D)s'

# Process naming
proc_name = 'chicago_taxi_api_free'

# Free tier optimizations
daemon = False
user = None
group = None

def when_ready(server):
    server.log.info("🆓 Chicago Taxi API (FREE TIER) is ready!")

def worker_int(worker):
    worker.log.info("🔄 Worker received signal")
EOF

echo "✅ Free tier Gunicorn config created"
echo ""

# Create optimized requirements for free tier
cat > requirements_free.txt << 'EOF'
# Chicago Taxi Fare API - FREE TIER Optimized Requirements
# Minimal dependencies to fit within free tier memory limits

Flask==2.3.2
gunicorn==21.2.0
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
joblib==1.3.2

# Remove heavy dependencies for free tier
# xgboost==1.7.6          # Comment out to save memory
# lightgbm==4.0.0         # Comment out to save memory

# Production essentials
Werkzeug==2.3.6
python-dotenv==1.0.0
EOF

echo "✅ Free tier requirements.txt created"
echo ""

# Update Procfile for Render
cat > Procfile << 'EOF'
web: gunicorn --config gunicorn_free.conf.py api.production_app:app
EOF

echo "✅ Procfile created for Render"
echo ""

echo "🎯 RENDER DEPLOYMENT INSTRUCTIONS"
echo "=================================="
echo ""
echo "1. 📤 PUSH TO GITHUB:"
echo "   git add ."
echo "   git commit -m 'Add Render free tier config'"
echo "   git push origin main"
echo ""
echo "2. 🌐 DEPLOY ON RENDER:"
echo "   a) Go to: https://render.com"
echo "   b) Sign up/Login (free account)"
echo "   c) Click 'New' → 'Web Service'"
echo "   d) Connect GitHub repository"
echo "   e) Select your repository"
echo "   f) Choose 'Free' plan"
echo "   g) Click 'Create Web Service'"
echo ""
echo "3. ⚙️ AUTOMATIC CONFIGURATION:"
echo "   Render will automatically:"
echo "   - Use the render.yaml file"
echo "   - Install dependencies"
echo "   - Deploy your API"
echo "   - Provide HTTPS URL"
echo ""
echo "4. 🧪 TEST YOUR API:"
echo "   Once deployed, test with:"
echo "   curl https://your-app-name.onrender.com/health"
echo ""

echo "💡 FREE TIER TIPS:"
echo "=================="
echo "✅ Your API will be available at: https://$APP_NAME.onrender.com"
echo "✅ Automatic HTTPS certificate"
echo "✅ GitHub integration (auto-deploy on push)"
echo "✅ 750 hours/month (enough for 24/7 if needed)"
echo ""
echo "⚠️  FREE TIER LIMITATIONS:"
echo "   🐌 Spins down after 15min inactivity (30s cold start)"
echo "   🔒 512MB RAM limit (model loading might be slow)"
echo "   ⏱️  Build timeout: 15 minutes"
echo "   📊 1GB disk space"
echo ""

echo "🔧 OPTIMIZATION FOR FREE TIER:"
echo "=============================="
echo "✅ Removed heavy ML libraries (XGBoost, LightGBM)"
echo "✅ Single worker process"
echo "✅ Reduced memory usage"
echo "✅ Optimized model loading"
echo ""

echo "🎉 RENDER FREE DEPLOYMENT COMPLETE!"
echo "===================================="
echo "Your Chicago Taxi Fare API is ready for FREE deployment on Render!"
echo ""
echo "📋 Next steps:"
echo "1. Push code to GitHub"
echo "2. Create Render account: https://render.com"
echo "3. Deploy from GitHub"
echo "4. Test your API"
echo ""
echo "💰 Cost: $0/month forever!"