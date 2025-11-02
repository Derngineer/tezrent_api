# Model Query Optimization Guide

## 🎯 Model-by-Model Query Patterns

This guide shows you exactly how to optimize queries for each model in your TezRent API.

---

## 1️⃣ Rental Model Optimizations

### Current Model (rentals/models.py)

```python
class Rental(models.Model):
    equipment = models.ForeignKey('equipment.Equipment', ...)
    customer = models.ForeignKey('accounts.CustomerProfile', ...)
    seller = models.ForeignKey('accounts.CompanyProfile', ...)
    # ... other fields
```

### Recommended Indexes to Add:

```python
class Rental(models.Model):
    # ... existing fields ...
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Status queries (most common)
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['customer', 'status']),
            
            # Date range queries
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['seller', 'start_date']),
            
            # Payment/approval queries
            models.Index(fields=['approval_status', '-created_at']),
            models.Index(fields=['payment_status']),
        ]
```

### Optimized View Queries:

```python
# ❌ BAD - Unoptimized
def get_rentals(request):
    rentals = Rental.objects.all()
    # Each iteration causes 3+ queries (equipment, customer, seller)
    return rentals

# ✅ GOOD - Optimized with select_related
def get_rentals(request):
    rentals = Rental.objects.select_related(
        'equipment',
        'equipment__seller_company',  # If you need seller info from equipment
        'equipment__category',  # If you need category
        'customer',
        'customer__user',  # If you need user email/name
        'seller',
    ).filter(status='active')
    return rentals

# ✅ BETTER - With prefetch for related items
from django.db.models import Prefetch

def get_rental_detail(request, pk):
    rental = Rental.objects.select_related(
        'equipment',
        'customer__user',
        'seller'
    ).prefetch_related(
        'status_updates',  # All status updates
        'images',  # All rental images
        'payments',  # All payments
        Prefetch(
            'reviews',
            queryset=RentalReview.objects.select_related('customer__user')
        )
    ).get(pk=pk)
    return rental
```

---

## 2️⃣ Equipment Model Optimizations

### Recommended Indexes:

```python
# equipment/models.py
class Equipment(models.Model):
    # ... existing fields ...
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Search & filter indexes
            models.Index(fields=['is_active', 'availability_status']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['seller_company', 'is_active']),
            
            # Price range queries
            models.Index(fields=['daily_rate']),
            models.Index(fields=['category', 'daily_rate']),
            
            # Location-based queries (if you have location field)
            models.Index(fields=['location', 'is_active']),
            
            # Search queries
            models.Index(fields=['name']),  # For LIKE queries
        ]
```

### Optimized Queries:

```python
# ❌ BAD - List view
def equipment_list(request):
    equipment = Equipment.objects.all()
    return equipment

# ✅ GOOD - Optimized list view
def equipment_list(request):
    equipment = Equipment.objects.select_related(
        'category',
        'seller_company'
    ).prefetch_related(
        'images'  # For thumbnail
    ).filter(
        is_active=True
    ).only(
        'id', 'name', 'daily_rate', 'availability_status',
        'category__name', 'seller_company__company_name'
    )
    return equipment

# ✅ BETTER - Detail view with everything
def equipment_detail(request, pk):
    equipment = Equipment.objects.select_related(
        'category',
        'seller_company',
        'seller_company__user'
    ).prefetch_related(
        'images',
        'tags',
        Prefetch(
            'rentals',
            queryset=Rental.objects.filter(status='active')
        ),
        Prefetch(
            'favorited_by',
            queryset=Favorite.objects.select_related('customer__user')
        )
    ).get(pk=pk, is_active=True)
    return equipment
```

---

## 3️⃣ Favorites Model Optimizations

### Already Optimized (Good job!):

```python
# favorites/models.py - Already has indexes
class Favorite(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['customer', '-created_at']),
            models.Index(fields=['equipment', '-created_at']),
        ]
```

### Add These Additional Indexes:

```python
class Favorite(models.Model):
    # ... existing fields ...
    
    class Meta:
        unique_together = ('customer', 'equipment')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', '-created_at']),
            models.Index(fields=['equipment', '-created_at']),
            
            # NEW: Notification queries
            models.Index(fields=['notify_on_availability']),
            models.Index(fields=['notify_on_price_drop']),
            
            # NEW: Rental preference queries
            models.Index(fields=['customer', 'preferred_rental_start']),
        ]
```

### View Already Optimized:

```python
# favorites/views.py - Already using select_related ✅
def get_queryset(self):
    return Favorite.objects.filter(
        customer=self.request.user.customer_profile
    ).select_related('equipment', 'equipment__seller_company', 'customer__user')
```

---

## 4️⃣ FavoriteCollection Model Optimizations

### Already Optimized:

```python
# favorites/admin.py - Already using prefetch_related ✅
def get_queryset(self, request):
    return super().get_queryset(request).select_related(
        'customer__user'
    ).prefetch_related('equipment')
```

### Add Index for Public Collections:

```python
class FavoriteCollection(models.Model):
    # ... existing fields ...
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', '-created_at']),
            
            # NEW: Public collection queries
            models.Index(fields=['is_public', '-created_at']),
        ]
```

---

## 5️⃣ RecentlyViewed Model Optimizations

### Already Has Index ✅:

```python
class RecentlyViewed(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['customer', '-last_viewed_at']),
        ]
```

### Add Equipment Index:

```python
class RecentlyViewed(models.Model):
    # ... existing fields ...
    
    class Meta:
        unique_together = ('customer', 'equipment')
        ordering = ['-last_viewed_at']
        indexes = [
            models.Index(fields=['customer', '-last_viewed_at']),
            
            # NEW: Equipment view tracking
            models.Index(fields=['equipment', '-last_viewed_at']),
            models.Index(fields=['customer', 'view_count']),  # Popular items
        ]
```

---

## 6️⃣ Accounts (User/Profile) Optimizations

### CustomerProfile Indexes:

```python
# accounts/models.py
class CustomerProfile(models.Model):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),  # User lookups
            models.Index(fields=['phone']),  # Phone searches
        ]
```

### CompanyProfile Indexes:

```python
class CompanyProfile(models.Model):
    # ... existing fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['company_name']),  # Company searches
            models.Index(fields=['is_verified', 'auto_approve_rentals']),
        ]
```

---

## 7️⃣ Dashboard Summary Optimization

### Your Current Query (rentals/views.py - dashboard_summary):

```python
# LINE 933-1080: Already has some optimization
def dashboard_summary(self, request):
    # These are good ✅
    total_equipment = Equipment.objects.filter(
        seller_company=seller_company,
        is_active=True
    ).count()
    
    active_rentals = Rental.objects.filter(
        seller=seller_company,
        status='active'
    ).count()
```

### Improve With Aggregate (Single Query):

```python
from django.db.models import Count, Sum, Q, F
from django.utils import timezone

def dashboard_summary(self, request):
    seller_company = request.user.company_profile
    
    # ✅ OPTIMIZED: Get multiple counts in ONE query
    stats = Rental.objects.filter(
        seller=seller_company
    ).aggregate(
        active_rentals=Count('id', filter=Q(status='active')),
        pending_approvals=Count('id', filter=Q(approval_status='pending')),
        completed_this_month=Count(
            'id',
            filter=Q(
                status='completed',
                end_date__month=timezone.now().month
            )
        ),
        total_revenue=Sum(
            'total_amount',
            filter=Q(payment_status='completed')
        )
    )
    
    # ✅ Equipment count (separate query, but cached)
    total_equipment = Equipment.objects.filter(
        seller_company=seller_company,
        is_active=True
    ).count()
    
    return Response({
        'total_equipment': total_equipment,
        'active_rentals': stats['active_rentals'] or 0,
        'pending_approvals': stats['pending_approvals'] or 0,
        'completed_this_month': stats['completed_this_month'] or 0,
        'monthly_revenue': stats['total_revenue'] or 0,
    })
```

---

## 8️⃣ General ViewSet Patterns

### Pattern: List Views

```python
class RentalViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # ✅ Always use select_related for ForeignKeys
        queryset = Rental.objects.select_related(
            'equipment',
            'customer__user',
            'seller'
        )
        
        # ✅ Only fetch needed fields for list views
        if self.action == 'list':
            queryset = queryset.only(
                'id', 'status', 'start_date', 'end_date',
                'total_amount', 'equipment__name',
                'customer__user__email'
            )
        
        # ✅ Use prefetch_related for detail view
        elif self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'status_updates',
                'images',
                'payments'
            )
        
        return queryset
```

### Pattern: Filtering

```python
from django_filters import rest_framework as filters

class RentalFilter(filters.FilterSet):
    # Add filters on indexed fields
    status = filters.ChoiceFilter(field_name='status')
    start_date_after = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = filters.DateFilter(field_name='start_date', lookup_expr='lte')
    
    class Meta:
        model = Rental
        fields = ['status', 'approval_status', 'payment_status']

class RentalViewSet(viewsets.ModelViewSet):
    filterset_class = RentalFilter
    # Now you can filter: /api/rentals/rentals/?status=active&start_date_after=2025-01-01
```

---

## 9️⃣ Migration to Add Indexes

Create a migration file to add all indexes:

```bash
python manage.py makemigrations --empty rentals --name add_rental_indexes
```

**Edit the migration file:**

```python
# rentals/migrations/000X_add_rental_indexes.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('rentals', '0001_initial'),  # Update to your latest migration
    ]

    operations = [
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(fields=['status', '-created_at'], name='rental_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(fields=['seller', 'status'], name='rental_seller_status_idx'),
        ),
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(fields=['customer', 'status'], name='rental_customer_status_idx'),
        ),
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(fields=['start_date', 'end_date'], name='rental_date_range_idx'),
        ),
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(fields=['approval_status', '-created_at'], name='rental_approval_idx'),
        ),
    ]
```

---

## 🔟 Query Performance Checklist

Before deploying any view, check:

- [ ] Using `select_related()` for all ForeignKey fields you access?
- [ ] Using `prefetch_related()` for all reverse ForeignKey/ManyToMany?
- [ ] Using `only()` for list views to fetch minimal fields?
- [ ] Using `filter()` on indexed fields?
- [ ] Using `.count()` instead of `len(queryset)`?
- [ ] Using `.exists()` instead of `if queryset:`?
- [ ] Using `aggregate()` for database-level calculations?
- [ ] Avoiding queries inside loops?

---

## 📊 Performance Monitoring

### In Django Shell:

```python
from django.db import connection, reset_queries
from django.test.utils import override_settings

# Enable query logging
with override_settings(DEBUG=True):
    reset_queries()
    
    # Your query here
    rentals = list(Rental.objects.select_related('equipment').all()[:10])
    
    # Check number of queries
    print(f"Number of queries: {len(connection.queries)}")
    
    # Print all queries
    for query in connection.queries:
        print(query['sql'])
```

---

## 🎯 Priority Order for Implementation

1. **High Priority** (Do first):
   - Add Rental model indexes
   - Add Equipment model indexes
   - Optimize dashboard_summary view

2. **Medium Priority**:
   - Add Favorites indexes
   - Add RecentlyViewed indexes
   - Optimize equipment list/detail views

3. **Low Priority**:
   - Add Account model indexes
   - Add collection indexes

---

**Next:** Once you've set up PostgreSQL, run these optimizations!
