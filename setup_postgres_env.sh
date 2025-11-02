#!/bin/bash

# Azure PostgreSQL Environment Variables
# Run this script with: source setup_postgres_env.sh

echo "Setting up Azure PostgreSQL environment variables..."

# TODO: Replace these with your actual credentials or source from .env file
export PGHOST=${PGHOST:-"your-postgres-host.database.azure.com"}
export PGUSER=${PGUSER:-"your-database-user@yourdomain.com"}
export PGPORT=${PGPORT:-5432}
export PGDATABASE=${PGDATABASE:-"postgres"}

# Get Azure AD access token (requires Azure CLI)
if command -v az &> /dev/null; then
    echo "Fetching Azure AD access token..."
    export PGPASSWORD="$(az account get-access-token --resource https://ossrdbms-aad.database.windows.net --query accessToken --output tsv)"
    
    if [ -z "$PGPASSWORD" ]; then
        echo "❌ Failed to get access token. Make sure you're logged in to Azure CLI:"
        echo "   az login"
    else
        echo "✅ Environment variables set successfully!"
        echo ""
        echo "📊 Connection Details:"
        echo "   Host: $PGHOST"
        echo "   User: $PGUSER"
        echo "   Port: $PGPORT"
        echo "   Database: $PGDATABASE"
        echo "   Password: [Access Token Set]"
        echo ""
        echo "🚀 You can now run Django with PostgreSQL:"
        echo "   python manage.py migrate"
        echo "   python manage.py runserver"
    fi
else
    echo "❌ Azure CLI not found. Please install it:"
    echo "   brew install azure-cli"
    echo "   az login"
fi
