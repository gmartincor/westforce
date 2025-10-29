import os
import multiprocessing

bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
workers = min(4, multiprocessing.cpu_count() * 2 + 1)
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
timeout = 120
keepalive = 5

accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

tmp_upload_dir = "/tmp"
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}
worker_tmp_dir = "/dev/shm"

def on_starting(server):
    server.log.info("Starting Gunicorn for westforce.com")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def post_worker_init(worker):
    worker.log.info(f"Worker initialized (pid: {worker.pid})")

def worker_abort(worker):
    worker.log.info(f"Worker aborted (pid: {worker.pid})")
