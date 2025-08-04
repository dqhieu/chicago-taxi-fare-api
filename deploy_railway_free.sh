#!/bin/bash
# Chicago Taxi Fare API - FREE Railway Deployment

set -e

echo "🚂 RAILWAY FREE DEPLOYMENT - CHICAGO TAXI FARE API"
echo "=================================================="
echo "✅ FREE: $5 monthly credit"
echo "✅ Easiest deployment ever!"
echo "✅ GitHub integration"
echo "⏱️  Setup time: ~5 minutes"
echo ""

# Configuration
APP_NAME="chicago-taxi-api"

echo "📋 RAILWAY FREE TIER CHECKLIST"
echo "=============================="
echo ""
echo "✅ Prerequisites:"
echo "   1. GitHub account (free)"
echo "   2. Railway account (free): https://railway.app"
echo "   3. Your code on GitHub"
echo ""

echo "🔧 CREATING RAILWAY CONFIGURATION"
echo "================================="

# Create railway.toml for easy deployment
cat > railway.toml << EOF
[build]
builder = "nixpacks"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyMaxRetries = 3
restartPolicyType = "always"

[environments.production]
PORT = "8000"
MODEL_PATH = "models/"
LOG_LEVEL = "info"
WEB_CONCURRENCY = "1"
PYTHONUNBUFFERED = "1"
EOF

echo "✅ railway.toml created"

# Create Procfile for Railway
cat > Procfile << 'EOF'
web: gunicorn --config gunicorn_railway.conf.py api.production_app:app
EOF

echo "✅ Procfile created"

# Create Railway-optimized gunicorn config
cat > gunicorn_railway.conf.py << 'EOF'
# Gunicorn configuration optimized for Railway FREE tier
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"

# Worker processes (FREE TIER: Limited resources)
workers = 1
worker_class = "sync"
worker_connections = 50
timeout = 60
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# Memory optimization
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = 'chicago_taxi_railway'

def when_ready(server):
    server.log.info("🚂 Chicago Taxi API ready on Railway!")
EOF

echo "✅ Railway gunicorn config created"

# Create lightweight requirements for Railway
cat > requirements_railway.txt << 'EOF'
# Railway FREE tier optimized requirements
Flask==2.3.2
gunicorn==21.2.0
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
joblib==1.3.2
Werkzeug==2.3.6
python-dotenv==1.0.0
EOF

echo "✅ Railway requirements created"

# Create .env example for Railway
cat > .env.example << 'EOF'
# Railway Environment Variables
PORT=8000
MODEL_PATH=models/
LOG_LEVEL=info
WEB_CONCURRENCY=1
PYTHONUNBUFFERED=1
EOF

echo "✅ Environment variables example created"

echo ""
echo "🚀 RAILWAY DEPLOYMENT INSTRUCTIONS"
echo "=================================="
echo ""
echo "📤 STEP 1: PUSH TO GITHUB"
echo "-------------------------"
echo "git add ."
echo "git commit -m 'Add Railway deployment config'"
echo "git push origin main"
echo ""

echo "🌐 STEP 2: DEPLOY ON RAILWAY"
echo "----------------------------"
echo "1. Go to: https://railway.app"
echo "2. Sign up/Login with GitHub (free)"
echo "3. Click 'Deploy from GitHub repo'"
echo "4. Select your repository"
echo "5. Railway will automatically:"
echo "   - Detect Python app"
echo "   - Install dependencies"
echo "   - Deploy your API"
echo "   - Provide HTTPS URL"
echo ""

echo "⚙️ STEP 3: CONFIGURE ENVIRONMENT (OPTIONAL)"
echo "------------------------------------------"
echo "In Railway dashboard:"
echo "1. Go to Variables tab"
echo "2. Add environment variables:"
echo "   MODEL_PATH=models/"
echo "   LOG_LEVEL=info"
echo "   WEB_CONCURRENCY=1"
echo ""

echo "🧪 STEP 4: TEST YOUR API"
echo "------------------------"
echo "Once deployed:"
echo "1. Copy the URL from Railway dashboard"
echo "2. Test: curl https://your-app.railway.app/health"
echo ""

echo "💰 RAILWAY FREE TIER BENEFITS"
echo "============================="
echo "✅ \$5 monthly credit (500 hours)"
echo "✅ One-click GitHub deployment"
echo "✅ Automatic HTTPS"
echo "✅ Environment variables"
echo "✅ Custom domains"
echo "✅ Built-in monitoring"
echo "✅ Automatic deploys on git push"
echo ""

echo "📊 FREE TIER LIMITS"
echo "==================="
echo "💰 \$5 credit/month"
echo "⏰ ~500 execution hours"
echo "💾 512MB RAM"
echo "🖥️  0.5 vCPU"
echo "💿 1GB disk"
echo "🌐 100GB bandwidth"
echo ""

echo "💡 RAILWAY TIPS"
echo "==============="
echo "✅ Perfect for prototypes and MVPs"
echo "✅ Auto-deploy on every git push"
echo "✅ Easy database integration"
echo "✅ Simple scaling when needed"
echo "✅ Great developer experience"
echo ""

echo "🔧 USEFUL RAILWAY COMMANDS"
echo "=========================="
echo "Install Railway CLI (optional):"
echo "  npm install -g @railway/cli"
echo ""
echo "Login:"
echo "  railway login"
echo ""
echo "Deploy from terminal:"
echo "  railway up"
echo ""
echo "View logs:"
echo "  railway logs"
echo ""
echo "Add environment variable:"
echo "  railway variables set KEY=value"
echo ""

echo "🎉 RAILWAY DEPLOYMENT READY!"
echo "============================"
echo ""
echo "Your Chicago Taxi Fare API is ready for the EASIEST"
echo "deployment experience with Railway!"
echo ""
echo "📋 Summary:"
echo "1. ✅ Configuration files created"
echo "2. 📤 Push code to GitHub"
echo "3. 🚂 Deploy on Railway.app"
echo "4. 🎯 Get instant HTTPS URL"
echo "5. 💰 Stay in \$5/month free tier"
echo ""
echo "🌟 Why Railway?"
echo "- Easiest deployment (literally 3 clicks)"
echo "- Auto-deploy on git push"
echo "- Great for beginners"
echo "- No Docker knowledge required"
echo "- Excellent free tier"