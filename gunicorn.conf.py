import os

wsgi_app = "config.wsgi:application"
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
workers = os.getenv("GUNICORN_WORKERS", 4)
workers_connections = os.getenv("GUNICORN_WORKERS_CONNECTIONS", 1001)
timeout = os.getenv("GUNICORN_TIMEOUT", 300)
