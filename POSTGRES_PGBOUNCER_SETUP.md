# PostgreSQL + PgBouncer Setup Guide

## 🎯 Overview
This guide covers:
1. Setting up PostgreSQL database
2. Configuring PgBouncer (connection pooling)
3. Django query optimization patterns
4. Model indexing strategies

---

## 📦 Step 1: Install Required Packages

```bash
pip install psycopg2-binary dj-database-url
```

---

## 🗄️ Step 2: PostgreSQL Configuration

### A. Azure PostgreSQL Setup (Recommended for Production)

1. **Create PostgreSQL Server in Azure Portal:**
   - Go to Azure Portal → Create Resource → "Azure Database for PostgreSQL"
   - Choose "Flexible Server"
   - Server name: `tezrent-db`
   - Admin username: `tezrentadmin`
   - Create strong password
   - Choose region (same as your App Service)
   - Compute + Storage: Basic or Standard tier

2. **Configure Firewall:**
   - Add your local IP for development
   - Add Azure services (for App Service connection)

3. **Get Connection String:**
   ```
   postgres://tezrentadmin:PASSWORD@tezrent-db.postgres.database.azure.com:5432/tezrentdb?sslmode=require
   ```

### B. Local PostgreSQL (Development)

```bash
# macOS (using Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb tezrentdb
```

---

## 🔄 Step 3: PgBouncer Setup

### Why PgBouncer?
- **Connection pooling**: Reuses database connections (reduces overhead)
- **Better performance**: Especially for Django with multiple workers
- **Handles connection limits**: PostgreSQL has connection limits, PgBouncer helps manage them

### A. Azure PgBouncer (Built-in)

Azure PostgreSQL Flexible Server has **built-in connection pooling** - no extra setup needed!

Just ensure your connection string uses the correct port (usually 6432 for pgbouncer mode).

### B. Self-Hosted PgBouncer (If needed)

```bash
# macOS
brew install pgbouncer

# Create config file
sudo nano /usr/local/etc/pgbouncer.ini
```

**pgbouncer.ini:**
```ini
[databases]
tezrentdb = host=localhost port=5432 dbname=tezrentdb

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
auth_type = md5
auth_file = /usr/local/etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 100
default_pool_size = 20
min_pool_size = 10
reserve_pool_size = 5
reserve_pool_timeout = 3
max_db_connections = 50
max_user_connections = 50
server_idle_timeout = 600
```

**Start PgBouncer:**
```bash
pgbouncer -d /usr/local/etc/pgbouncer.ini
```

---

## ⚙️ Step 4: Django Settings Configuration

**config/settings.py:**

```python
import dj_database_url
import os

# PostgreSQL Configuration
if os.getenv('DATABASE_URL'):
    # Production (Azure) - uses environment variable
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,  # Connection pooling (10 minutes)
            conn_health_checks=True,  # Verify connections are alive
            ssl_require=True,
        )
    }
else:
    # Local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'tezrentdb',
            'USER': 'your_username',  # Your local postgres user
            'PASSWORD': 'your_password',  # Your local postgres password
            'HOST': '127.0.0.1',
            'PORT': '6432',  # PgBouncer port (or 5432 for direct connection)
            'CONN_MAX_AGE': 600,  # Connection pooling
            'OPTIONS': {
                'connect_timeout': 10,
            }
        }
    }

# Disable persistent connections in development if needed
# DATABASES['default']['CONN_MAX_AGE'] = 0
```

---

## 🚀 Step 5: Migration to PostgreSQL

```bash
# 1. Backup current SQLite data
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > backup.json

# 2. Update settings.py to use PostgreSQL

# 3. Run migrations
python manage.py migrate

# 4. Load data (optional - if you want to keep existing data)
python manage.py loaddata backup.json

# 5. Create superuser (if not loading data)
python manage.py createsuperuser
```

---

## 🎯 Step 6: Query Optimization Patterns

### Pattern 1: select_related() - For ForeignKey & OneToOne

**Use when:** You need related object data (follows foreign keys)

```python
# ❌ BAD - N+1 queries
rentals = Rental.objects.all()
for rental in rentals:
    print(rental.equipment.name)  # Additional query for each rental
    print(rental.customer.user.email)  # More queries!

# ✅ GOOD - 1 query with JOINs
rentals = Rental.objects.select_related(
    'equipment',
    'customer__user',
    'seller'
).all()
```

### Pattern 2: prefetch_related() - For ManyToMany & Reverse ForeignKey

**Use when:** You need multiple related objects

```python
# ❌ BAD - N+1 queries
collections = FavoriteCollection.objects.all()
for collection in collections:
    print(collection.equipment.all())  # Query for each collection

# ✅ GOOD - 2 queries total
collections = FavoriteCollection.objects.prefetch_related('equipment').all()
```

### Pattern 3: Prefetch() - Advanced prefetching with filtering

```python
from django.db.models import Prefetch

# Only prefetch active equipment
active_equipment = Equipment.objects.filter(is_active=True)

collections = FavoriteCollection.objects.prefetch_related(
    Prefetch('equipment', queryset=active_equipment)
).all()
```

### Pattern 4: only() & defer() - Select specific fields

```python
# ✅ Only get fields you need (smaller query)
rentals = Rental.objects.only('id', 'status', 'total_amount')

# ✅ Exclude heavy fields (like text fields)
equipment = Equipment.objects.defer('description', 'terms_and_conditions')
```

### Pattern 5: values() & values_list() - Dictionary/tuple results

```python
# For simple data (not model instances)
rental_statuses = Rental.objects.values('id', 'status')
# Returns: [{'id': 1, 'status': 'active'}, ...]

equipment_ids = Equipment.objects.values_list('id', flat=True)
# Returns: [1, 2, 3, 4, ...]
```

### Pattern 6: annotate() & aggregate() - Database-level calculations

```python
from django.db.models import Count, Sum, Avg

# Count rentals per equipment
equipment_with_rentals = Equipment.objects.annotate(
    rental_count=Count('rentals')
).filter(rental_count__gt=5)

# Calculate totals
total_revenue = Rental.objects.aggregate(
    total=Sum('total_amount'),
    average=Avg('total_amount')
)
```

### Pattern 7: exists() & count() - Efficient checks

```python
# ❌ BAD
if len(Rental.objects.filter(status='pending')) > 0:
    # ...

# ✅ GOOD
if Rental.objects.filter(status='pending').exists():
    # ...

# For actual count
count = Rental.objects.filter(status='pending').count()
```

---

## 📊 Step 7: Model Indexing Strategy

### Already Indexed (in your models):

```python
# favorites/models.py - RecentlyViewed
class Meta:
    indexes = [
        models.Index(fields=['customer', '-last_viewed_at']),
    ]

# favorites/models.py - Favorite
class Meta:
    indexes = [
        models.Index(fields=['customer', '-created_at']),
        models.Index(fields=['equipment', '-created_at']),
    ]
```

### Recommended Additional Indexes:

See `MODEL_OPTIMIZATION_GUIDE.md` for model-specific indexes to add.

---

## 🔍 Step 8: Query Performance Monitoring

### Enable Query Logging (Development)

```python
# settings.py - Add to LOGGING config
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Use Django Debug Toolbar

```bash
pip install django-debug-toolbar
```

### Use explain() to analyze queries

```python
# See query execution plan
print(Rental.objects.filter(status='active').explain())
```

---

## ✅ Step 9: Environment Variables Setup

### Local (.env file):

```bash
DATABASE_URL=postgresql://user:password@localhost:6432/tezrentdb
```

### Azure App Service:

1. Go to App Service → Configuration → Application Settings
2. Add: `DATABASE_URL` = `postgres://tezrentadmin:PASSWORD@tezrent-db.postgres.database.azure.com:5432/tezrentdb?sslmode=require`
3. Save and restart

---

## 🧪 Step 10: Test Connection

```bash
# Test database connection
python manage.py dbshell

# Or check with Django shell
python manage.py shell
>>> from django.db import connection
>>> connection.cursor()
>>> print("Database connected successfully!")
```

---

## 📈 Performance Improvements Expected

| Metric | SQLite | PostgreSQL + PgBouncer |
|--------|---------|------------------------|
| Concurrent Users | ~10 | 100+ |
| Query Speed | Baseline | 2-5x faster |
| Connection Overhead | N/A | 70% reduction |
| Scalability | Limited | Excellent |

---

## 🚨 Common Issues & Solutions

### Issue 1: "too many connections"
**Solution:** Lower `CONN_MAX_AGE` or configure PgBouncer

### Issue 2: SSL/TLS errors
**Solution:** Add `?sslmode=require` to connection string

### Issue 3: Slow migrations
**Solution:** Use `--fake-initial` if structure already exists

### Issue 4: Lost connections
**Solution:** Enable `conn_health_checks=True`

---

## 📝 Next Steps

1. ✅ Install packages
2. ✅ Create PostgreSQL database
3. ✅ Configure PgBouncer (if self-hosting)
4. ✅ Update settings.py
5. ✅ Run migrations
6. ✅ Review MODEL_OPTIMIZATION_GUIDE.md
7. ✅ Update views with optimized queries
8. ✅ Test performance

**Ready to proceed? Let's start with Step 1!**
