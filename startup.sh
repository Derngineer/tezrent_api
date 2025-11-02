#!/bin/bash

echo "Starting application..."

# If running on Azure and PGHOST is set, get Azure AD token for PostgreSQL
if [ ! -z "$PGHOST" ] && [ -z "$PGPASSWORD" ]; then
    echo "🔑 Getting Azure AD token for PostgreSQL authentication..."
    export PGPASSWORD=$(curl -s "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https%3A%2F%2Fossrdbms-aad.database.windows.net%2F" -H "Metadata: true" | jq -r .access_token)
    
    if [ ! -z "$PGPASSWORD" ] && [ "$PGPASSWORD" != "null" ]; then
        echo "✅ Azure AD token obtained via Managed Identity"
    else
        echo "⚠️  Could not get token via Managed Identity, will try Azure CLI..."
        export PGPASSWORD=$(az account get-access-token --resource https://ossrdbms-aad.database.windows.net --query accessToken -o tsv 2>/dev/null)
    fi
fi

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start Gunicorn (Azure provides PORT environment variable)
echo "Starting Gunicorn on port ${PORT:-8000}..."
gunicorn config.wsgi:application --bind=0.0.0.0:${PORT:-8000} --workers=2 --timeout=120 --access-logfile '-' --error-logfile '-'
