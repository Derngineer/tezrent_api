# Azure PostgreSQL Connection Setup

## 🎯 Your Azure PostgreSQL Details

**Connection Information:**
- **Host:** `tezrent001.postgres.database.azure.com`
- **User:** `dmatderby@gmail.com`
- **Port:** `5432`
- **Database:** `postgres`
- **Auth Method:** Azure AD (Access Token)

---

## 📋 Setup Steps

### Step 1: Install Azure CLI (if not installed)

```bash
# macOS
brew install azure-cli

# Verify installation
az --version
```

### Step 2: Login to Azure

```bash
az login
```

This will open a browser window for authentication.

### Step 3: Set Environment Variables

**Option A: Using the setup script (Recommended)**

```bash
# Source the script to set environment variables
source setup_postgres_env.sh
```

**Option B: Manual setup**

```bash
export PGHOST=tezrent001.postgres.database.azure.com
export PGUSER=dmatderby@gmail.com
export PGPORT=5432
export PGDATABASE=postgres
export PGPASSWORD="$(az account get-access-token --resource https://ossrdbms-aad.database.windows.net --query accessToken --output tsv)"
```

### Step 4: Test PostgreSQL Connection

```bash
# Activate virtual environment
source env/bin/activate

# Test Django database connection
python manage.py check --database default
```

### Step 5: Run Migrations

```bash
# Create all database tables
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 6: Run Development Server

```bash
python manage.py runserver
```

---

## 🔄 For Production (Azure App Service)

Since your PostgreSQL uses **Azure AD authentication**, you need to configure the App Service to use a **Managed Identity**.

### Configure Managed Identity (Azure Portal):

1. **Go to your App Service** (`tezrentapibackend`)

2. **Enable System-assigned Managed Identity:**
   - Navigate to: **Identity** (in left sidebar)
   - Turn **Status** to **On**
   - Click **Save**
   - Copy the **Object (principal) ID**

3. **Grant Database Access to Managed Identity:**
   ```bash
   # Connect to PostgreSQL as admin
   az postgres flexible-server connect \
     --name tezrent001 \
     --admin-user dmatderby@gmail.com \
     --database postgres
   
   # In PostgreSQL shell, run:
   SET aad_validate_oids_in_tenant = off;
   CREATE ROLE tezrentapibackend WITH LOGIN PASSWORD 'not_used_with_aad' IN ROLE azure_ad_user;
   GRANT ALL PRIVILEGES ON DATABASE postgres TO tezrentapibackend;
   ```

4. **Update App Service Configuration:**
   
   Add these Application Settings in Azure Portal:
   ```
   PGHOST = tezrent001.postgres.database.azure.com
   PGUSER = tezrentapibackend
   PGPORT = 5432
   PGDATABASE = postgres
   ```

5. **Update startup.sh for Managed Identity:**

   The app will automatically use Managed Identity when deployed to Azure.

---

## 🔑 Alternative: Standard PostgreSQL Authentication

If Azure AD auth is complex, you can use standard username/password:

1. **Create standard PostgreSQL user:**
   ```sql
   CREATE USER tezrentadmin WITH PASSWORD 'your_strong_password';
   GRANT ALL PRIVILEGES ON DATABASE postgres TO tezrentadmin;
   ```

2. **Use DATABASE_URL instead:**
   ```bash
   # Local
   export DATABASE_URL="postgresql://tezrentadmin:password@tezrent001.postgres.database.azure.com:5432/postgres?sslmode=require"
   
   # Azure App Service (add to Configuration)
   DATABASE_URL=postgresql://tezrentadmin:password@tezrent001.postgres.database.azure.com:5432/postgres?sslmode=require
   ```

---

## 🧪 Testing Commands

### Check database connection:
```bash
python manage.py dbshell
```

### Check which database Django is using:
```python
python manage.py shell
>>> from django.db import connection
>>> print(connection.settings_dict)
```

### Test query:
```python
python manage.py shell
>>> from accounts.models import User
>>> User.objects.count()
```

---

## 🚨 Common Issues

### Issue 1: "FATAL: password authentication failed"
**Solution:** Ensure PGPASSWORD is set with valid Azure AD token:
```bash
export PGPASSWORD="$(az account get-access-token --resource https://ossrdbms-aad.database.windows.net --query accessToken --output tsv)"
```

### Issue 2: "SSL connection is required"
**Solution:** Already configured in settings.py with `sslmode: require`

### Issue 3: Access token expires
**Solution:** Tokens expire after 1 hour. Re-run the export command:
```bash
source setup_postgres_env.sh
```

### Issue 4: "could not connect to server"
**Solution:** Check firewall rules in Azure Portal:
- PostgreSQL server → Networking → Allow your IP address

---

## 📊 Current Configuration

**settings.py** now supports 3 modes:

1. **DATABASE_URL** (connection string) - Highest priority
2. **PGHOST, PGUSER, etc.** (individual variables) - Medium priority  
3. **SQLite** (fallback) - Lowest priority

**Current setup uses Mode 2** with your Azure PostgreSQL credentials.

---

## 🎯 Next Steps

1. ✅ Install Azure CLI: `brew install azure-cli`
2. ✅ Login: `az login`
3. ✅ Source environment setup: `source setup_postgres_env.sh`
4. ✅ Test connection: `python manage.py check --database default`
5. ✅ Run migrations: `python manage.py migrate`
6. ✅ Test with runserver: `python manage.py runserver`

**Then configure Azure App Service for production!**
