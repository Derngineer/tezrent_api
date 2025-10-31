#!/bin/bash

echo "Starting application..."

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start Gunicorn (Azure provides PORT environment variable)
echo "Starting Gunicorn on port ${PORT:-8000}..."
gunicorn config.wsgi:application --bind=0.0.0.0:${PORT:-8000} --workers=2 --timeout=120 --access-logfile '-' --error-logfile '-'
