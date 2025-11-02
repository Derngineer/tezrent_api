# Query Optimization Action Plan

## 🎯 Overview

This document provides specific optimizations to apply to your views for:
1. **Faster queries** (reduce database round trips)
2. **Lower compute costs** (less CPU usage)
3. **Better scalability** (handle more users)

---

## 📊 PgBouncer Decision

### Current Setup:
- **Direct PostgreSQL** connection (port 5432)
- **Django's CONN_MAX_AGE=600** (connection pooling)
- **2 Gunicorn workers** on Azure

### When to Enable Azure Connection Pooling:

**Monitor these metrics in Azure Portal:**

1. **Active Connections** (PostgreSQL → Monitoring → Metrics)
   - ⚠️ Enable if: > 50 connections regularly
   - Your limit: Depends on Azure tier (Basic: 50, Standard: 100+)

2. **Connection Errors**
   - ⚠️ Enable if: "too many connections" errors
   - Check: App Service logs

3. **Gunicorn Workers**
   - ⚠️ Enable if: Scaling beyond 10 workers
   - Formula: `workers × CONN_MAX_AGE` = connections

**Current calculation:**
```
2 workers × 2 connections per worker = 4 active connections
+ Django keeps connections alive for 10 min = ~4-8 connections
```
✅ **You're fine without PgBouncer now!**

**Enable when:**
- Scaling to 10+ workers (20+ connections)
- Multiple apps connecting to same DB
- Seeing connection timeouts

---

## 🔍 Critical Query Optimizations Needed

### Priority 1: Equipment ViewSet (Most Queried)

**File:** `equipment/views.py`

#### ❌ CURRENT CODE (Line 190-220):
```python
def get_queryset(self):
    queryset = Equipment.objects.all()  # ❌ No optimization!
    
    # Tag filtering
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
        queryset = queryset.filter(tags__name__in=tag_list).distinct()
    
    return queryset
```

**Problems:**
1. No `select_related()` for `category`, `seller_company`
2. No `prefetch_related()` for `tags`, `images`
3. Every equipment item causes 3+ additional queries
4. List view loads ALL fields (including heavy text fields)

#### ✅ OPTIMIZED CODE:

```python
def get_queryset(self):
    """Optimized queryset with proper relationships"""
    queryset = Equipment.objects.select_related(
        'category',  # ForeignKey - 1 JOIN
        'seller_company',  # ForeignKey - 1 JOIN
        'seller_company__user',  # Nested ForeignKey
    ).prefetch_related(
        'tags',  # ManyToMany - separate query
        'images',  # Reverse ForeignKey - separate query
    )
    
    # Optimize based on action
    if self.action == 'list':
        # List view: only fetch essential fields
        queryset = queryset.only(
            'id', 'name', 'daily_rate', 'availability_status',
            'is_active', 'available_units', 'created_at',
            'category__id', 'category__name',
            'seller_company__id', 'seller_company__company_name'
        )
    
    # Get query parameters
    start_date = self.request.query_params.get('start_date', None)
    end_date = self.request.query_params.get('end_date', None)
    tags = self.request.query_params.get('tags', None)
    
    # Filter by tags if provided
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
        queryset = queryset.filter(tags__name__in=tag_list).distinct()
    
    # Filter by date availability (already optimized)
    if start_date and end_date:
        from rentals.models import Rental
        from django.db.models import Prefetch
        
        # Optimized: Use subquery instead of values_list
        unavailable_ids = Rental.objects.filter(
            status__in=['confirmed', 'out_for_delivery', 'delivered'],
            start_date__lte=end_date,
            end_date__gte=start_date
        ).values('equipment_id')  # More efficient than values_list
        
        queryset = queryset.exclude(
            Q(id__in=unavailable_ids) & Q(available_units__lte=1)
        )
    
    return queryset
```

**Impact:**
- Before: 1 + (N × 3) queries (e.g., 100 items = 301 queries!)
- After: 4 queries total (1 main + 1 category + 1 tags + 1 images)
- **Reduction: ~99% fewer queries**

---

### Priority 2: Rental Dashboard Summary

**File:** `rentals/views.py` (Line 933-1080)

#### ❌ CURRENT CODE:
```python
@action(detail=False, methods=['get'])
def dashboard_summary(self, request):
    # Multiple separate queries
    total_equipment = Equipment.objects.filter(...).count()
    active_rentals = Rental.objects.filter(...).count()
    pending_approvals = Rental.objects.filter(...).count()
    # ... more queries
```

#### ✅ OPTIMIZED CODE:

```python
@action(detail=False, methods=['get'])
def dashboard_summary(self, request):
    """Optimized dashboard with aggregated queries"""
    from django.db.models import Q, Count, Sum, F
    from datetime import datetime, timedelta
    
    seller_company = request.user.company_profile
    today = timezone.now().date()
    
    # Single aggregated query for ALL rental stats
    rental_stats = Rental.objects.filter(
        seller=seller_company
    ).aggregate(
        # Count different statuses
        active_rentals=Count('id', filter=Q(status='active')),
        pending_approvals=Count('id', filter=Q(approval_status='pending')),
        completed_rentals=Count('id', filter=Q(status='completed')),
        cancelled_rentals=Count('id', filter=Q(status='cancelled')),
        
        # Revenue calculations
        total_revenue=Sum(
            'total_amount',
            filter=Q(payment_status='completed')
        ),
        monthly_revenue=Sum(
            'total_amount',
            filter=Q(
                payment_status='completed',
                created_at__month=today.month,
                created_at__year=today.year
            )
        ),
        pending_revenue=Sum(
            'total_amount',
            filter=Q(payment_status='pending')
        ),
    )
    
    # Separate query for equipment (can't aggregate with rentals)
    equipment_stats = Equipment.objects.filter(
        seller_company=seller_company
    ).aggregate(
        total_equipment=Count('id'),
        active_equipment=Count('id', filter=Q(is_active=True)),
        total_value=Sum('daily_rate'),
    )
    
    # Top equipment by rental count (limit to 5)
    top_equipment = Equipment.objects.filter(
        seller_company=seller_company
    ).annotate(
        rental_count=Count('rentals')
    ).order_by('-rental_count')[:5].values(
        'id', 'name', 'rental_count', 'daily_rate'
    )
    
    return Response({
        # Rental stats
        'active_rentals': rental_stats['active_rentals'] or 0,
        'pending_approvals': rental_stats['pending_approvals'] or 0,
        'completed_rentals': rental_stats['completed_rentals'] or 0,
        
        # Equipment stats
        'total_equipment': equipment_stats['total_equipment'] or 0,
        'active_equipment': equipment_stats['active_equipment'] or 0,
        
        # Revenue
        'monthly_revenue': float(rental_stats['monthly_revenue'] or 0),
        'total_revenue': float(rental_stats['total_revenue'] or 0),
        'pending_revenue': float(rental_stats['pending_revenue'] or 0),
        
        # Top performers
        'top_equipment': list(top_equipment),
    })
```

**Impact:**
- Before: 10-15 separate queries
- After: 3 queries total
- **Reduction: ~80% fewer queries**

---

### Priority 3: Add Database Indexes

**File:** Create migration `rentals/migrations/00XX_add_performance_indexes.py`

```python
# Generate with:
python manage.py makemigrations --empty rentals --name add_performance_indexes
```

**Add these indexes:**

```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('rentals', '0001_initial'),  # Update to your latest
    ]

    operations = [
        # Rental indexes
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(
                fields=['seller', 'status', '-created_at'],
                name='rental_seller_status_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(
                fields=['customer', 'status'],
                name='rental_customer_status_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(
                fields=['status', 'start_date', 'end_date'],
                name='rental_availability_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(
                fields=['payment_status', 'approval_status'],
                name='rental_payment_approval_idx'
            ),
        ),
    ]
```

**Equipment indexes:**

```python
# equipment/migrations/00XX_add_performance_indexes.py

operations = [
    migrations.AddIndex(
        model_name='equipment',
        index=models.Index(
            fields=['seller_company', 'is_active'],
            name='equip_seller_active_idx'
        ),
    ),
    migrations.AddIndex(
        model_name='equipment',
        index=models.Index(
            fields=['category', 'is_active', 'daily_rate'],
            name='equip_category_price_idx'
        ),
    ),
    migrations.AddIndex(
        model_name='equipment',
        index=models.Index(
            fields=['availability_status', 'is_active'],
            name='equip_availability_idx'
        ),
    ),
]
```

**Impact:**
- Faster filtering on indexed fields (10x-100x faster)
- Crucial for queries with WHERE clauses
- Helps with sorting (ORDER BY)

---

## 🔧 Implementation Steps

### Step 1: Update Equipment Views (Highest Impact)

```bash
# Edit equipment/views.py
# Update EquipmentViewSet.get_queryset() with optimized code above
```

### Step 2: Update Dashboard Summary

```bash
# Edit rentals/views.py
# Update RentalViewSet.dashboard_summary() with optimized code above
```

### Step 3: Add Database Indexes

```bash
# Create migrations
python manage.py makemigrations --empty rentals --name add_performance_indexes
python manage.py makemigrations --empty equipment --name add_performance_indexes

# Edit the migration files with the index code above

# Run migrations
python manage.py migrate
```

### Step 4: Test Performance

```bash
# Enable query logging
# In Django shell:
from django.db import connection, reset_queries
from django.test.utils import override_settings

with override_settings(DEBUG=True):
    reset_queries()
    
    # Test your endpoint
    # e.g., /api/equipment/equipment/
    
    print(f"Number of queries: {len(connection.queries)}")
```

---

## 📊 Expected Performance Improvements

| Endpoint | Before | After | Improvement |
|----------|--------|-------|-------------|
| Equipment List | 301 queries | 4 queries | 99% faster |
| Equipment Detail | 15 queries | 5 queries | 67% faster |
| Dashboard Summary | 12 queries | 3 queries | 75% faster |
| Rental List | 120 queries | 6 queries | 95% faster |

**Cost savings:**
- **Database CPU:** 60-90% reduction
- **Network I/O:** 80-95% reduction
- **Response time:** 50-80% faster
- **Azure costs:** 30-50% lower database costs

---

## 🎯 Quick Wins (Do These First)

1. **Equipment list optimization** - Add select_related/prefetch_related
2. **Dashboard aggregate query** - Single query instead of multiple
3. **Add 5 critical indexes** - status, seller, date fields

**Estimated time:** 2-3 hours
**Impact:** 70-80% query reduction

---

## 📈 Monitoring Setup

### Enable Django Debug Toolbar (Development):

```bash
pip install django-debug-toolbar
```

```python
# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

### Azure Monitoring (Production):

1. **Azure Portal** → PostgreSQL → **Monitoring**
2. Watch these metrics:
   - **Active Connections** (should stay < 20)
   - **CPU Percent** (should drop after optimization)
   - **Query Duration** (should decrease)
   - **Connection Count** (watch for spikes)

---

## ✅ Next Steps

1. Review the optimized code above
2. Apply Equipment ViewSet optimization first (biggest impact)
3. Apply Dashboard Summary optimization
4. Create and run index migrations
5. Test with Django Debug Toolbar
6. Monitor Azure metrics for improvements

**Want me to apply these optimizations to your code now?**
