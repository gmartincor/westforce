#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating cache table..."
python manage.py createcachetable --noinput 2>/dev/null || true

echo "Starting gunicorn..."
exec gunicorn -c gunicorn.conf.py config.wsgi:application
