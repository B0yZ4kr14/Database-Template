#!/usr/bin/env python3
"""
Database WSGI Configuration
===========================
Configuração para deployment com Gunicorn
"""

from main import app

# Configuração Gunicorn
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "database-api"
