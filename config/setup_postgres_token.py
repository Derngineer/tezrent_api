#!/usr/bin/env python3
"""
Auto-set PostgreSQL password using Azure AD token before Django starts
"""
import os
import subprocess
import sys

def get_azure_ad_token():
    """Get Azure AD token for PostgreSQL"""
    try:
        result = subprocess.run(
            ['az', 'account', 'get-access-token', 
             '--resource', 'https://ossrdbms-aad.database.windows.net',
             '--query', 'accessToken', '-o', 'tsv'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        print(f"Warning: Could not get Azure AD token: {e}", file=sys.stderr)
    return None

# If PGHOST is set but PGPASSWORD is not, try to get token
if os.getenv('PGHOST') and not os.getenv('PGPASSWORD'):
    token = get_azure_ad_token()
    if token:
        os.environ['PGPASSWORD'] = token
        print("✅ Azure AD token set for PostgreSQL authentication")
    else:
        print("⚠️  Warning: Could not obtain Azure AD token. Database connection may fail.", file=sys.stderr)
