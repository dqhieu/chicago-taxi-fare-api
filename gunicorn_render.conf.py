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