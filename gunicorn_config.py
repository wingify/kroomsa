"""gunicorn WSGI server configuration."""
# Importing dependencies
from os import environ


bind = '0.0.0.0:' + environ.get('PORT', '5000')
limit_request_line = 0
worker_class = 'gthread'
workers = 1
timeout = 1000
graceful_timeout = 1000
