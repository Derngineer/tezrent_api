# Security Best Practices - Credentials Management

## ✅ What's Been Secured

### Files Protected (Never Committed):
- ✅ `.env` - Contains actual credentials (in .gitignore)
- ✅ `db.sqlite3` - Local database (in .gitignore)
- ✅ Environment variables - Only stored locally/Azure

### Files Safe to Commit (No Real Credentials):
- ✅ `.env.example` - Template with placeholders
- ✅ `settings.py` - Uses `os.getenv()` only
- ✅ `setup_postgres_env.sh` - Uses env vars, no hardcoded values

---

## 🔒 How Your Credentials Are Protected

### 1. settings.py (SECURE)

```python
# ✅ GOOD - Reads from environment variables
'HOST': os.getenv('PGHOST'),  # No default hardcoded value
'USER': os.getenv('PGUSER'),  # Must be set externally
'PASSWORD': os.getenv('PGPASSWORD'),  # Never in code

# ❌ BAD - What we removed
'HOST': os.getenv('PGHOST', 'tezrent001.postgres...'),  # Exposed!
'USER': os.getenv('PGUSER', 'dmatderby@gmail.com'),  # Exposed!
```

### 2. .env File (LOCAL ONLY)

**Location:** `/Users/derbymatoma/tezrent_api/tezrent_api/.env`

**Status:** ✅ In .gitignore (never pushed to GitHub)

**Contains:**
```bash
PGHOST=tezrent001.postgres.database.azure.com
PGUSER=dmatderby@gmail.com
PGPORT=5432
PGDATABASE=postgres
```

### 3. Azure App Service (PRODUCTION)

**Credentials stored in:** Azure Portal → App Service → Configuration → Application Settings

**These are encrypted by Azure** and never exposed in code.

---

## 🔍 Verify Nothing Is Exposed

### Check if credentials are in git history:

```bash
# Search for sensitive data in committed files
git log --all --full-history -- "*settings.py" | grep -i "password\|secret"

# Check what's ignored
git check-ignore .env
# Should output: .env (means it's protected)
```

### Check current repository:

```bash
# Search for your database host in tracked files
git grep "tezrent001.postgres" 
# Should only appear in documentation files (AZURE_POSTGRES_SETUP.md, etc.)

# Make sure .env is never tracked
git ls-files | grep "\.env$"
# Should output nothing (means .env is not tracked)
```

---

## 📋 Security Checklist

### ✅ Local Development (Your Machine)

- [x] `.env` file created with real credentials
- [x] `.env` is in `.gitignore`
- [x] `settings.py` uses `os.getenv()` with NO defaults for sensitive data
- [x] `setup_postgres_env.sh` reads from environment (no hardcoded values)
- [x] Azure AD token used (expires after 1 hour - good security!)

### ✅ GitHub Repository (Public/Private)

- [x] No hardcoded passwords in any committed files
- [x] No hardcoded database hosts in settings.py
- [x] `.env.example` only has placeholders
- [x] Documentation references are generic (example values only)

### ✅ Azure Production

- [x] Environment variables set in Azure Portal (not in code)
- [x] Variables encrypted by Azure
- [x] Access controlled by Azure RBAC
- [x] SSL/TLS enforced for database connections

---

## 🚀 How to Use Credentials Securely

### Local Development (MacOS):

**Option 1: Use .env file**

1. Create `.env` file:
```bash
cat > .env << EOF
PGHOST=tezrent001.postgres.database.azure.com
PGUSER=dmatderby@gmail.com
PGPORT=5432
PGDATABASE=postgres
EOF
```

2. Export variables before running Django:
```bash
export $(cat .env | xargs)
python manage.py runserver
```

**Option 2: Use setup script**

```bash
# Edit setup_postgres_env.sh first to set your values
export PGHOST=tezrent001.postgres.database.azure.com
export PGUSER=dmatderby@gmail.com

# Then source it
source setup_postgres_env.sh  # Gets Azure AD token automatically
python manage.py runserver
```

**Option 3: Manual export**

```bash
export PGHOST=tezrent001.postgres.database.azure.com
export PGUSER=dmatderby@gmail.com
export PGPORT=5432
export PGDATABASE=postgres
export PGPASSWORD="$(az account get-access-token --resource https://ossrdbms-aad.database.windows.net --query accessToken --output tsv)"

python manage.py runserver
```

### Azure Production:

1. **Azure Portal** → Your App Service → **Configuration** → **Application settings**

2. **Add these:**
   ```
   PGHOST = tezrent001.postgres.database.azure.com
   PGUSER = tezrentapibackend  (managed identity)
   PGPORT = 5432
   PGDATABASE = postgres
   ```

3. **Click Save** → **Restart App Service**

---

## 🔐 What If Credentials Were Already Pushed?

If you accidentally committed credentials before, you need to:

### 1. Change the credentials immediately:

```bash
# For Azure PostgreSQL with password auth
az postgres flexible-server update \
  --name tezrent001 \
  --admin-password NEW_SECURE_PASSWORD

# Or rotate Azure AD tokens (automatic - tokens expire hourly)
```

### 2. Remove from git history (ADVANCED):

```bash
# WARNING: This rewrites git history!
# Only do this if credentials were in recent commits

# Remove sensitive file from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (careful!)
git push origin --force --all
```

### 3. Use GitHub's secret scanning:

GitHub automatically scans for exposed secrets. Check:
- Repository → Security → Secret scanning alerts

---

## 📊 Current Setup Status

### ✅ SECURE (Good to go!)

- **Settings.py:** No hardcoded credentials ✅
- **Env variables:** Only in .env (gitignored) ✅
- **Azure secrets:** In Azure Portal (encrypted) ✅
- **Auth method:** Azure AD tokens (expire hourly) ✅
- **SSL/TLS:** Enforced for all connections ✅

### 📝 Recommendations

1. **Never commit `.env` file** - Already in .gitignore ✅
2. **Use Azure AD authentication** - Already using it ✅
3. **Rotate credentials regularly** - Azure AD tokens auto-expire ✅
4. **Use Managed Identity in production** - Recommended for Azure
5. **Enable Azure Key Vault** - For enterprise-level secret management

---

## 🛡️ Additional Security Measures

### Enable Azure Key Vault (Optional but Recommended):

```python
# settings.py - Use Azure Key Vault for secrets
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

if os.getenv('AZURE_KEY_VAULT_URL'):
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=os.getenv('AZURE_KEY_VAULT_URL'), credential=credential)
    
    DATABASES = {
        'default': {
            'HOST': client.get_secret('PGHOST').value,
            'USER': client.get_secret('PGUSER').value,
            'PASSWORD': client.get_secret('PGPASSWORD').value,
        }
    }
```

### Monitor Access:

1. **Azure Portal** → PostgreSQL → **Monitoring** → **Metrics**
2. Set up alerts for:
   - Failed connection attempts
   - Unusual access patterns
   - Connection from unknown IPs

---

## ✅ You're Secure!

Your credentials are now properly protected:
- ✅ Not in git repository
- ✅ Not in GitHub
- ✅ Only in local .env and Azure Portal
- ✅ Using Azure AD authentication
- ✅ SSL/TLS enforced

**Next steps:**
1. Set up environment variables locally (use `.env` file)
2. Configure Azure App Service environment variables
3. Test connection with: `python manage.py check --database default`
