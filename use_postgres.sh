#!/bin/bash
# Script to switch to PostgreSQL and run Django commands

# Get Azure AD token for PostgreSQL authentication
echo "🔑 Getting Azure AD access token..."
export PGPASSWORD=$(az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv)

if [ -z "$PGPASSWORD" ]; then
    echo "❌ Failed to get Azure AD token. Please run: az login"
    exit 1
fi

# Set PostgreSQL environment variables
export PGHOST=tezrent001.postgres.database.azure.com
export PGUSER=dmatderby@gmail.com
export PGPORT=5432
export PGDATABASE=postgres

echo "✅ Azure AD token obtained"
echo "🔄 Switched to PostgreSQL database"
echo "📍 Host: $PGHOST"
echo "👤 User: $PGUSER"
echo ""

# Check if a command was provided
if [ $# -eq 0 ]; then
    echo "✅ PostgreSQL environment variables set!"
    echo ""
    echo "You can now run:"
    echo "  python manage.py createsuperuser    # Create superuser"
    echo "  python manage.py migrate             # Run migrations"
    echo "  python manage.py dbshell             # Open PostgreSQL shell"
    echo "  python manage.py shell               # Django shell with PostgreSQL"
    echo "  python manage.py runserver           # Run server with PostgreSQL"
    echo ""
    echo "Note: You'll be prompted for password when connecting"
else
    # Run the provided command
    echo "Running: python manage.py $@"
    python manage.py "$@"
fi
