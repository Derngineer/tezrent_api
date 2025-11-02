# PostgreSQL Setup - Quick Reference

## 🚀 Quick Start Steps

### Current Setup (No PgBouncer)

**You are using:**
- Direct PostgreSQL connection (port 5432)
- Django's built-in connection pooling (`CONN_MAX_AGE=600`)
- Azure PostgreSQL Flexible Server (which has its own built-in pooling)

**PgBouncer is NOT needed yet** - add it later if you hit connection limits.

---

### 1. Install PostgreSQL locally (macOS):
```bash
brew install postgresql@15
brew services start postgresql@15
createdb tezrentdb
```

### 2. Update settings (already done):
- PostgreSQL packages installed ✅
- settings.py configured ✅
- Will use DATABASE_URL env variable in production

### 3. Create Azure PostgreSQL:
1. Azure Portal → Create Resource → "Azure Database for PostgreSQL - Flexible Server"
2. Server name: `tezrent-db`
3. Admin username: `tezrentadmin`
4. Choose strong password
5. Allow Azure services in firewall

### 4. Set Azure Environment Variable:
```bash
DATABASE_URL=postgresql://tezrentadmin:PASSWORD@tezrent-db.postgres.database.azure.com:5432/tezrentdb?sslmode=require
```

Add this in Azure Portal → App Service → Configuration → Application Settings

### 5. Run Migrations:
```bash
# Local (after setting up local PostgreSQL)
python manage.py migrate

# Azure will run automatically via startup.sh
```

---

## 🎯 Query Optimization Patterns (Quick Reference)

### Pattern 1: select_related (ForeignKey)
```python
Rental.objects.select_related('equipment', 'customer__user', 'seller')
```

### Pattern 2: prefetch_related (ManyToMany/Reverse FK)
```python
FavoriteCollection.objects.prefetch_related('equipment')
```

### Pattern 3: only() - Limit fields
```python
Equipment.objects.only('id', 'name', 'daily_rate')
```

### Pattern 4: Aggregation
```python
from django.db.models import Count, Sum
Rental.objects.aggregate(total=Sum('total_amount'))
```

### Pattern 5: exists() - Fast checking
```python
if Rental.objects.filter(status='pending').exists():
    # ...
```

---

## 📊 Common Indexes to Add

### Rental Model:
```python
class Meta:
    indexes = [
        models.Index(fields=['status', '-created_at']),
        models.Index(fields=['seller', 'status']),
        models.Index(fields=['customer', 'status']),
    ]
```

### Equipment Model:
```python
class Meta:
    indexes = [
        models.Index(fields=['is_active', 'availability_status']),
        models.Index(fields=['category', 'is_active']),
        models.Index(fields=['seller_company', 'is_active']),
    ]
```

---

## 🔍 Performance Check Commands

```python
# Count queries
from django.db import connection, reset_queries
reset_queries()
# ... your code ...
print(len(connection.queries))

# Explain query
print(Rental.objects.filter(status='active').explain())
```

---

## ⚡ PgBouncer (Optional - Not Currently Used)

**Current Status:** ❌ Not configured (not needed yet)

Azure PostgreSQL Flexible Server has **built-in connection pooling** at the server level.

**When to add PgBouncer:**
- You get "too many connections" errors
- Scaling beyond 50 workers
- Multiple applications sharing one database

**For now:** Django's `CONN_MAX_AGE=600` is sufficient! ✅

---

## 📝 Files Created:
1. ✅ POSTGRES_PGBOUNCER_SETUP.md - Full setup guide
2. ✅ MODEL_OPTIMIZATION_GUIDE.md - Model-specific optimizations
3. ✅ requirements.txt - Updated with PostgreSQL packages
4. ✅ settings.py - Configured for PostgreSQL

---

## 🎯 Next Steps:

1. **Setup Azure PostgreSQL database** (or local PostgreSQL for development)
2. **Add DATABASE_URL to Azure App Service environment variables**
3. **Restart Azure App Service** (migrations will run automatically)
4. **Add indexes to models** (see MODEL_OPTIMIZATION_GUIDE.md)
5. **Update views with optimized queries** (see examples in guides)

---

## 🚨 Important Notes:

- **Local development**: Still uses SQLite (unless you uncomment PostgreSQL config)
- **Production (Azure)**: Will automatically use PostgreSQL via DATABASE_URL
- **Migrations**: Run automatically on Azure via startup.sh
- **Connection pooling**: Built-in on Azure, no PgBouncer setup needed
- **Query optimization**: Already using select_related in many places ✅

---

**Ready to proceed with Azure PostgreSQL setup?**
