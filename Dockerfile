# Chicago Taxi Fare Prediction API - Production Docker Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MODEL_PATH=/app/models
ENV PORT=8000

# Create non-root user for security
RUN groupadd -r apiuser && useradd -r -g apiuser apiuser

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/production_app.py app.py
COPY gunicorn.conf.py .
COPY models/ models/

# Copy startup script
COPY <<'EOF' start.sh
#!/bin/bash
set -e

echo "🚀 Starting Chicago Taxi Fare Prediction API..."
echo "📊 Model path: $MODEL_PATH"
echo "🌐 Port: $PORT"
echo "👥 Workers: $WEB_CONCURRENCY"

# Health check for model files
if [ ! -f "$MODEL_PATH/chicago_fare_model_metadata.json" ]; then
    echo "❌ Model metadata not found at $MODEL_PATH"
    exit 1
fi

if [ ! -f "$MODEL_PATH/chicago_fare_predictor_linear_regression.pkl" ]; then
    echo "❌ Model file not found at $MODEL_PATH"
    exit 1
fi

echo "✅ Model files verified"

# Start Gunicorn
exec gunicorn --config gunicorn.conf.py app:app
EOF

# Make startup script executable
RUN chmod +x start.sh

# Change ownership to non-root user
RUN chown -R apiuser:apiuser /app
USER apiuser

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Start the application
CMD ["./start.sh"]