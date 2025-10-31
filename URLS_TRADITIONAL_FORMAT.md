# Your API URLs - Traditional Django Format
# This is what router.register() creates automatically

## Location: rentals/urls.py
```python
router.register(r'rentals', RentalViewSet, basename='rental')
```

## Equivalent to this traditional Django urls.py:

```python
from django.urls import path
from rentals import views

urlpatterns = [
    # ============================================================================
    # STANDARD REST ENDPOINTS (Auto-generated from ModelViewSet)
    # ============================================================================
    
    # List all rentals / Create new rental
    path('api/rentals/rentals/', 
         views.RentalViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='rental-list'),
    
    # Get/Update/Delete specific rental
    path('api/rentals/rentals/<int:pk>/', 
         views.RentalViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy'
         }),
         name='rental-detail'),
    
    
    # ============================================================================
    # CUSTOM ENDPOINTS (From @action decorators in RentalViewSet)
    # ============================================================================
    
    # ──────────────────────────────────────────────────────────────────────────
    # List-level actions (detail=False - no ID required)
    # ──────────────────────────────────────────────────────────────────────────
    
    path('api/rentals/rentals/active_rentals/',
         views.RentalViewSet.as_view({'get': 'active_rentals'}),
         name='rental-active-rentals'),
    
    path('api/rentals/rentals/pending_approvals/',
         views.RentalViewSet.as_view({'get': 'pending_approvals'}),
         name='rental-pending-approvals'),
    
    path('api/rentals/rentals/my_rentals/',
         views.RentalViewSet.as_view({'get': 'my_rentals'}),
         name='rental-my-rentals'),
    
    path('api/rentals/rentals/rental_history/',
         views.RentalViewSet.as_view({'get': 'rental_history'}),
         name='rental-rental-history'),
    
    path('api/rentals/rentals/customer_dashboard/',
         views.RentalViewSet.as_view({'get': 'customer_dashboard'}),
         name='rental-customer-dashboard'),
    
    path('api/rentals/rentals/seller_dashboard/',
         views.RentalViewSet.as_view({'get': 'seller_dashboard'}),
         name='rental-seller-dashboard'),
    
    # 💰 Financial Endpoints
    path('api/rentals/rentals/sales/',
         views.RentalViewSet.as_view({'get': 'sales'}),
         name='rental-sales'),
    
    path('api/rentals/rentals/revenue_summary/',
         views.RentalViewSet.as_view({'get': 'revenue_summary'}),
         name='rental-revenue-summary'),
    
    path('api/rentals/rentals/transactions/',
         views.RentalViewSet.as_view({'get': 'transactions'}),
         name='rental-transactions'),
    
    # 📊 Dashboard Summary (YOUR NEW ENDPOINT!)
    path('api/rentals/rentals/dashboard_summary/',
         views.RentalViewSet.as_view({'get': 'dashboard_summary'}),
         name='rental-dashboard-summary'),
    
    
    # ──────────────────────────────────────────────────────────────────────────
    # Detail-level actions (detail=True - requires rental ID)
    # ──────────────────────────────────────────────────────────────────────────
    
    path('api/rentals/rentals/<int:pk>/approve/',
         views.RentalViewSet.as_view({'post': 'approve'}),
         name='rental-approve'),
    
    path('api/rentals/rentals/<int:pk>/reject/',
         views.RentalViewSet.as_view({'post': 'reject'}),
         name='rental-reject'),
    
    path('api/rentals/rentals/<int:pk>/cancel/',
         views.RentalViewSet.as_view({'post': 'cancel'}),
         name='rental-cancel'),
    
    path('api/rentals/rentals/<int:pk>/update_status/',
         views.RentalViewSet.as_view({'post': 'update_status'}),
         name='rental-update-status'),
    
    path('api/rentals/rentals/<int:pk>/upload_image/',
         views.RentalViewSet.as_view({'post': 'upload_image'}),
         name='rental-upload-image'),
    
    path('api/rentals/rentals/<int:pk>/upload_document/',
         views.RentalViewSet.as_view({'post': 'upload_document'}),
         name='rental-upload-document'),
    
    path('api/rentals/rentals/<int:pk>/documents/',
         views.RentalViewSet.as_view({'get': 'documents'}),
         name='rental-documents'),
    
    path('api/rentals/rentals/<int:pk>/upload_payment_receipt/',
         views.RentalViewSet.as_view({'post': 'upload_payment_receipt'}),
         name='rental-upload-payment-receipt'),
    
    path('api/rentals/rentals/<int:pk>/submit_review/',
         views.RentalViewSet.as_view({'post': 'submit_review'}),
         name='rental-submit-review'),
]
```

---

## 🔍 URL Name Pattern

The router creates names using this pattern:
```
{basename}-{action}
```

Where:
- **basename** = `'rental'` (from `router.register(..., basename='rental')`)
- **action** = method name or standard REST action

### Examples:

| Method in ViewSet | URL Name |
|------------------|----------|
| `.list()` | `rental-list` |
| `.retrieve()` | `rental-detail` |
| `.create()` | `rental-list` |
| `def dashboard_summary()` | `rental-dashboard-summary` |
| `def active_rentals()` | `rental-active-rentals` |
| `def approve()` | `rental-approve` |

**Pattern for custom actions:**
- Method name: `dashboard_summary` → URL name: `rental-dashboard-summary`
- Method name: `active_rentals` → URL name: `rental-active-rentals`
- Underscores become hyphens!

---

## 📝 Quick Reference Table

| URL | URL Name | HTTP Method | ViewSet Method |
|-----|----------|-------------|----------------|
| `/api/rentals/rentals/` | `rental-list` | GET | `list()` |
| `/api/rentals/rentals/` | `rental-list` | POST | `create()` |
| `/api/rentals/rentals/123/` | `rental-detail` | GET | `retrieve()` |
| `/api/rentals/rentals/123/` | `rental-detail` | PUT | `update()` |
| `/api/rentals/rentals/123/` | `rental-detail` | PATCH | `partial_update()` |
| `/api/rentals/rentals/dashboard_summary/` | `rental-dashboard-summary` | GET | `dashboard_summary()` |
| `/api/rentals/rentals/active_rentals/` | `rental-active-rentals` | GET | `active_rentals()` |
| `/api/rentals/rentals/pending_approvals/` | `rental-pending-approvals` | GET | `pending_approvals()` |
| `/api/rentals/rentals/revenue_summary/` | `rental-revenue-summary` | GET | `revenue_summary()` |
| `/api/rentals/rentals/transactions/` | `rental-transactions` | GET | `transactions()` |
| `/api/rentals/rentals/sales/` | `rental-sales` | GET | `sales()` |
| `/api/rentals/rentals/123/approve/` | `rental-approve` | POST | `approve()` |
| `/api/rentals/rentals/123/cancel/` | `rental-cancel` | POST | `cancel()` |
| `/api/rentals/rentals/123/update_status/` | `rental-update-status` | POST | `update_status()` |

---

## 💡 How to Use URL Names

### In Python/Django:
```python
from django.urls import reverse

# Get dashboard summary URL
url = reverse('rental-dashboard-summary')
# Returns: '/api/rentals/rentals/dashboard_summary/'

# Get specific rental URL
url = reverse('rental-detail', kwargs={'pk': 123})
# Returns: '/api/rentals/rentals/123/'

# Get approve URL for rental 456
url = reverse('rental-approve', kwargs={'pk': 456})
# Returns: '/api/rentals/rentals/456/approve/'
```

### In Templates:
```django
{% url 'rental-list' %}
{% url 'rental-detail' pk=rental.id %}
{% url 'rental-dashboard-summary' %}
```

### In DRF Serializers:
```python
from rest_framework.reverse import reverse

url = reverse('rental-dashboard-summary', request=request)
```

---

## 🎯 Where URL Names Come From

### 1. From `basename` parameter:
```python
router.register(r'rentals', RentalViewSet, basename='rental')
                                                    ^^^^^^^
                                                    This becomes the prefix!
```

### 2. From action/method name:
```python
@action(detail=False, methods=['get'])
def dashboard_summary(self, request):  # ← This becomes "dashboard-summary"
    pass
```

### 3. Combined with hyphen:
```
basename + '-' + action_name
'rental' + '-' + 'dashboard-summary'
= 'rental-dashboard-summary'
```

---

## 🔄 Comparison: Traditional Django vs DRF Router

### Traditional Django (what you're used to):
```python
# urls.py - You write every URL manually
urlpatterns = [
    path('rentals/', views.rental_list, name='rental-list'),
    path('rentals/<int:pk>/', views.rental_detail, name='rental-detail'),
    path('rentals/dashboard/', views.dashboard, name='dashboard'),
    # ... write 20+ more URLs manually
]
```

### DRF Router (what you have now):
```python
# urls.py - Router generates all URLs automatically
router = DefaultRouter()
router.register(r'rentals', RentalViewSet, basename='rental')
# This one line creates 20+ URLs automatically!
```

**Result:** Both create the same URLs, but the router does it automatically based on your ViewSet methods!

---

## ✅ Summary

Your dashboard summary endpoint:

**URL:** `/api/rentals/rentals/dashboard_summary/`  
**URL Name:** `rental-dashboard-summary`  
**How it's created:**
1. `config/urls.py` → routes `/api/rentals/` to `rentals.urls`
2. `rentals/urls.py` → router creates URL from ViewSet method name
3. `rentals/views.py` → method `dashboard_summary()` becomes the endpoint

The URL name follows this formula:
```
basename + '-' + method_name_with_hyphens
= 'rental' + '-' + 'dashboard-summary'
= 'rental-dashboard-summary'
```

Use it anywhere with: `reverse('rental-dashboard-summary')`
