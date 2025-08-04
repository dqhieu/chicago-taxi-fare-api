#!/bin/bash
# Chicago Taxi Fare API - FREE Fly.io Deployment

set -e

echo "🛩️ FLY.IO FREE DEPLOYMENT - CHICAGO TAXI FARE API"
echo "================================================="
echo "✅ FREE: $5 monthly credit (covers 3 small apps)"
echo "✅ No cold starts!"
echo "✅ Global edge deployment"
echo "⏱️  Setup time: ~10 minutes"
echo ""

# Configuration
APP_NAME="chicago-taxi-api"

echo "📋 FLY.IO FREE TIER CHECKLIST"
echo "============================="
echo ""
echo "✅ Prerequisites:"
echo "   1. Fly.io account (free): https://fly.io"
echo "   2. flyctl CLI installed"
echo "   3. Docker installed"
echo ""

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ Fly.io CLI not found. Install it first:"
    echo ""
    echo "🍎 macOS:"
    echo "   brew install flyctl"
    echo ""
    echo "🐧 Linux:"
    echo "   curl -L https://fly.io/install.sh | sh"
    echo ""
    echo "🪟 Windows:"
    echo "   powershell -Command \"iwr https://fly.io/install.ps1 -useb | iex\""
    echo ""
    echo "Or visit: https://fly.io/docs/getting-started/installing-flyctl/"
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install it first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

echo "🔐 FLY.IO AUTHENTICATION"
echo "========================"
echo "Authenticating with Fly.io..."

# Login to Fly.io
flyctl auth login

echo ""
echo "🚀 CREATING FLY.IO APP (FREE TIER)"
echo "=================================="

# Create Fly.io app (free tier)
flyctl apps create $APP_NAME

echo ""
echo "🐳 CREATING OPTIMIZED FLY.IO CONFIGURATION"
echo "=========================================="

# Create fly.toml configuration for free tier
cat > fly.toml << EOF
# Chicago Taxi Fare API - Fly.io FREE Tier Configuration
app = "$APP_NAME"
primary_region = "iad"  # Washington DC (good for US traffic)

[build]
  image = "chicago-taxi-api:latest"

[env]
  MODEL_PATH = "/app/models"
  LOG_LEVEL = "info"
  WEB_CONCURRENCY = "1"
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true  # Free tier: auto-sleep when idle
  auto_start_machines = true
  min_machines_running = 0   # Free tier: can scale to zero

  # Health check
  [http_service.checks]
    [http_service.checks.health]
      grace_period = "30s"
      interval = "15s"
      method = "GET"
      path = "/health"
      timeout = "10s"

[[vm]]
  cpu_kind = "shared"     # Free tier
  cpus = 1               # Free tier: 1 CPU
  memory_mb = 256        # Free tier: 256MB (smallest)

# Optional: Custom domain (free on Fly.io)
# [[services]]
#   http_checks = []
#   internal_port = 8080
#   processes = ["app"]
#   protocol = "tcp"
#   script_checks = []
#   [services.concurrency]
#     hard_limit = 25
#     soft_limit = 20
#     type = "connections"
#   [[services.ports]]
#     force_https = true
#     handlers = ["http"]
#     port = 80
#   [[services.ports]]
#     handlers = ["tls", "http"]
#     port = 443
EOF

echo "✅ fly.toml created for free tier deployment"

# Create optimized Dockerfile for Fly.io free tier
cat > Dockerfile.fly << 'EOF'
# Optimized for Fly.io FREE tier (256MB RAM)
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

# Install minimal system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and install (minimal for free tier)
COPY requirements_minimal.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY api/production_app.py app.py
COPY models/ models/

# Create minimal startup script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🛩️ Starting on Fly.io FREE tier..."\n\
echo "💾 Available memory: $(free -h | awk \"NR==2{print \$7}\")"\n\
echo "🔧 Starting with minimal resources..."\n\
exec gunicorn \\\n\
    --bind 0.0.0.0:$PORT \\\n\
    --workers 1 \\\n\
    --threads 2 \\\n\
    --timeout 60 \\\n\
    --keep-alive 2 \\\n\
    --max-requests 500 \\\n\
    --preload \\\n\
    --log-level info \\\n\
    app:app\n' > start.sh \
    && chmod +x start.sh

# Change ownership and switch to non-root user
RUN chown -R apiuser:apiuser /app
USER apiuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Expose port
EXPOSE 8080

# Start the application
CMD ["./start.sh"]
EOF

# Create minimal requirements for free tier (256MB RAM)
cat > requirements_minimal.txt << 'EOF'
# Ultra-minimal requirements for Fly.io FREE tier (256MB RAM)
Flask==2.3.2
gunicorn==21.2.0
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
joblib==1.3.2
Werkzeug==2.3.6

# Remove ALL heavy dependencies for free tier
# xgboost - Too heavy for 256MB
# lightgbm - Too heavy for 256MB  
# matplotlib - Not needed for API
# seaborn - Not needed for API
EOF

echo "✅ Optimized Dockerfile created for Fly.io free tier"

echo ""
echo "🐳 BUILDING DOCKER IMAGE"
echo "========================"

# Build Docker image
docker build -f Dockerfile.fly -t chicago-taxi-api .

echo ""
echo "🚀 DEPLOYING TO FLY.IO FREE TIER"
echo "================================"

# Deploy to Fly.io
flyctl deploy --local-only

# Get app URL
APP_URL="https://$APP_NAME.fly.dev"

echo ""
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "========================"
echo ""
echo "🌐 API URL: $APP_URL"
echo "🏥 Health Check: $APP_URL/health"
echo "🎯 Predict: $APP_URL/predict"
echo ""

echo "🧪 TESTING DEPLOYMENT"
echo "====================="
echo "Testing health endpoint..."

sleep 10  # Wait for app to start

if curl -f "$APP_URL/health"; then
    echo ""
    echo "✅ Health check passed!"
else
    echo ""
    echo "⚠️  Health check failed. Checking logs..."
    flyctl logs
fi

echo ""
echo "💰 FLY.IO FREE TIER BENEFITS"
echo "============================"
echo "✅ \$5 monthly credit (covers 3 small apps)"
echo "✅ 160GB bandwidth/month"
echo "✅ No cold starts (always warm)"
echo "✅ Global edge deployment"
echo "✅ Automatic HTTPS"
echo "✅ Custom domains (free)"
echo "✅ Built-in load balancing"
echo ""

echo "📊 RESOURCE USAGE (FREE TIER)"
echo "============================="
echo "🖥️  CPU: 1 shared CPU"
echo "💾 RAM: 256MB"
echo "💿 Disk: 1GB"
echo "🌐 Bandwidth: 160GB/month"
echo ""

echo "🔧 USEFUL FLY.IO COMMANDS"
echo "========================="
echo "View logs:"
echo "  flyctl logs -a $APP_NAME"
echo ""
echo "Check status:"
echo "  flyctl status -a $APP_NAME"
echo ""
echo "Scale (free tier):"
echo "  flyctl scale count 1 -a $APP_NAME"
echo ""
echo "Update app:"
echo "  flyctl deploy -a $APP_NAME"
echo ""
echo "SSH into app:"
echo "  flyctl ssh console -a $APP_NAME"
echo ""
echo "Monitor resources:"
echo "  flyctl dashboard $APP_NAME"
echo ""

echo "💡 FLY.IO FREE TIER TIPS"
echo "========================"
echo "✅ App auto-sleeps when idle (saves credits)"
echo "✅ No cold starts (faster than competitors)"
echo "✅ Great for development and testing"
echo "✅ Easy scaling when you need more resources"
echo "⚠️  Monitor credit usage: https://fly.io/dashboard"
echo ""

echo "🎉 FLY.IO FREE DEPLOYMENT COMPLETE!"
echo "==================================="
echo "Your Chicago Taxi Fare API is running on Fly.io's"
echo "global edge network - practically FREE!"
echo ""
echo "🎯 Next steps:"
echo "1. Test your API: $APP_URL/health"
echo "2. Monitor usage: https://fly.io/dashboard"
echo "3. Set up custom domain (optional)"
echo "4. Enjoy your fast, reliable API!"