# Gunicorn configuration for Chicago Taxi Fare API
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50

# Restart workers after this many requests, with up to 50 requests jitter
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'chicago_taxi_api'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (if using HTTPS)
# keyfile = os.environ.get('SSL_KEYFILE')
# certfile = os.environ.get('SSL_CERTFILE')

def when_ready(server):
    server.log.info("🚀 Chicago Taxi Fare API server is ready. Accepting connections.")

def worker_int(worker):
    worker.log.info("🔄 Worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("📦 Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("✅ Worker spawned (pid: %s)", worker.pid)