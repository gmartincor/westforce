# =============================================================================
# Gunicorn configuration for Westforce - Optimized for Hetzner CX23
# CX23: 2 vCPU, 4GB RAM, 40GB SSD
# =============================================================================

import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
backlog = 2048

# Worker configuration - Optimized for CX23 (2 vCPU)
# Formula: (2 * CPU) + 1 = 5, but we limit to 3 for 4GB RAM
workers = int(os.environ.get('GUNICORN_WORKERS', 3))
worker_class = "sync"
worker_connections = 1000
threads = 2  # 2 threads per worker for better concurrency

# Worker lifecycle - prevents memory leaks
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Timeouts
timeout = 30  # Reduced from 120 for better resource management
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
capture_output = True
enable_stdio_inheritance = True

# Process naming
proc_name = "westforce"

# Security & Performance
tmp_upload_dir = "/tmp"
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}
forwarded_allow_ips = '*'  # Trust Traefik proxy
worker_tmp_dir = "/dev/shm"  # Use RAM for temp files (faster)


# Lifecycle hooks
def on_starting(server):
    server.log.info("Starting Gunicorn for Westforce (Hetzner CX23)")


def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")


def post_worker_init(worker):
    worker.log.info(f"Worker initialized (pid: {worker.pid})")


def worker_abort(worker):
    worker.log.info(f"Worker aborted (pid: {worker.pid})")
