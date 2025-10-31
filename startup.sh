#!/bin/bash

echo "Starting application..."

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
# python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@tezrent.com').exists() or User.objects.create_superuser('admin@tezrent.com', 'admin@tezrent.com', 'changeme123')"

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn config.wsgi:application --bind=0.0.0.0:8000 --workers=4 --timeout=120
