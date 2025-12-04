

"""Gunicorn config - Westforce (VPS compartido, proyecto pequeño)"""
import os

# Server
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
backlog = 1024

# Workers
workers = int(os.environ.get('GUNICORN_WORKERS', 2))
worker_class = "sync"
worker_connections = 500
threads = 2

# Lifecycle
max_requests = 500
max_requests_jitter = 50
preload_app = True

# Timeouts
timeout = 30
graceful_timeout = 20
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "warning").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
capture_output = True

# Process
proc_name = "westforce"

# Security
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}
forwarded_allow_ips = '*'
worker_tmp_dir = "/dev/shm"
