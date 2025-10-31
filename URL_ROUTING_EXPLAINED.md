# URL Routing System Explained - TezRent API

## How Your Dashboard Summary URL Works

Let's trace through the **complete URL routing flow** from client request to your view!

---

## 🌐 The URL Flow

```
http://localhost:8000/api/rentals/rentals/dashboard_summary/
│
└─── Breaks down to:
     ├── http://localhost:8000  → Base server URL
     ├── /api/rentals/           → From config/urls.py
     ├── /rentals/               → From router.register() in rentals/urls.py
     └── /dashboard_summary/     → From @action decorator in views.py
```

---

## 📁 File-by-File Breakdown

### **1. Main URL Configuration** (`config/urls.py`)

```python
# config/urls.py (Lines 26-37)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/equipment/', include('equipment.urls')),
    path('api/rentals/', include('rentals.urls')),  # ← THIS LINE!
    path('api/favorites/', include('favorites.urls')),
    path('api/crm/', include('crm.urls')),
]
```

**What happens:**
- Django sees request to `/api/rentals/...`
- Routes to `rentals.urls` (rentals app)
- Everything after `/api/rentals/` gets passed to rentals/urls.py

---

### **2. Rentals URL Configuration** (`rentals/urls.py`)

```python
# rentals/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RentalViewSet, RentalReviewViewSet

app_name = 'rentals'

# Create a DefaultRouter instance
router = DefaultRouter()

# Register ViewSets with the router
router.register(r'rentals', RentalViewSet, basename='rental')
router.register(r'reviews', RentalReviewViewSet, basename='review')

# Include router URLs
urlpatterns = [
    path('', include(router.urls)),
]
```

**What happens:**
- `router.register(r'rentals', RentalViewSet, basename='rental')`
- This creates MULTIPLE URLs automatically!
- The router looks at RentalViewSet and generates endpoints

---

## 🔧 How DefaultRouter Works

The `DefaultRouter` automatically generates these standard REST endpoints:

```python
router.register(r'rentals', RentalViewSet, basename='rental')
```

**Generates:**

| URL Pattern | HTTP Method | ViewSet Method | Purpose |
|------------|-------------|----------------|---------|
| `rentals/` | GET | `.list()` | List all rentals |
| `rentals/` | POST | `.create()` | Create new rental |
| `rentals/{id}/` | GET | `.retrieve()` | Get single rental |
| `rentals/{id}/` | PUT | `.update()` | Update rental |
| `rentals/{id}/` | PATCH | `.partial_update()` | Partial update |
| `rentals/{id}/` | DELETE | `.destroy()` | Delete rental |

**PLUS** all custom actions defined with `@action` decorator!

---

## 🎯 Custom Actions (@action decorator)

### **Your Dashboard Summary Action**

```python
# rentals/views.py (Line 934-935)

class RentalViewSet(viewsets.ModelViewSet):
    # ... other code ...
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """
        Platform-wide dashboard summary
        """
        # ... your implementation ...
```

**How @action creates URLs:**

```python
@action(detail=False, methods=['get'])
def dashboard_summary(self, request):
```

**Breakdown:**
- `@action` → Tell router to create custom endpoint
- `detail=False` → List-level action (not tied to specific object)
  - Creates: `/rentals/dashboard_summary/`
  - NOT: `/rentals/{id}/dashboard_summary/`
- `methods=['get']` → Only accept GET requests
- `dashboard_summary` → Function name becomes URL path

---

## 🔗 Complete URL Resolution Flow

Let's trace a request step by step:

```
📱 CLIENT REQUEST:
   GET http://localhost:8000/api/rentals/rentals/dashboard_summary/

   ⬇️

🌐 DJANGO URL RESOLVER (config/urls.py):
   Matches: path('api/rentals/', include('rentals.urls'))
   Remaining: rentals/dashboard_summary/
   
   ⬇️

📋 RENTALS URLS (rentals/urls.py):
   Router checks registered ViewSets
   router.register(r'rentals', RentalViewSet)
   Matches: rentals/
   Remaining: dashboard_summary/
   
   ⬇️

🎯 RENTALVIEWSET (rentals/views.py):
   Looks for @action methods
   Finds: @action(detail=False) def dashboard_summary()
   Matches: dashboard_summary/
   
   ⬇️

✅ EXECUTES:
   RentalViewSet.dashboard_summary(request)
   
   ⬇️

📤 RESPONSE:
   Returns JSON with dashboard data
```

---

## 📊 All URLs from RentalViewSet

Here are ALL the endpoints created from your RentalViewSet:

### **Standard REST Endpoints** (Auto-generated)

```
GET    /api/rentals/rentals/                → list()
POST   /api/rentals/rentals/                → create()
GET    /api/rentals/rentals/{id}/           → retrieve()
PUT    /api/rentals/rentals/{id}/           → update()
PATCH  /api/rentals/rentals/{id}/           → partial_update()
DELETE /api/rentals/rentals/{id}/           → destroy()
```

### **Custom Actions** (From @action decorators)

```
# List-level actions (detail=False)
GET /api/rentals/rentals/active_rentals/        → active_rentals()
GET /api/rentals/rentals/pending_approvals/     → pending_approvals()
GET /api/rentals/rentals/seller_dashboard/      → seller_dashboard()
GET /api/rentals/rentals/customer_dashboard/    → customer_dashboard()
GET /api/rentals/rentals/sales/                 → sales()
GET /api/rentals/rentals/revenue_summary/       → revenue_summary()
GET /api/rentals/rentals/transactions/          → transactions()
GET /api/rentals/rentals/dashboard_summary/     → dashboard_summary() ⭐

# Detail-level actions (detail=True)
POST /api/rentals/rentals/{id}/approve/         → approve_rental()
POST /api/rentals/rentals/{id}/cancel/          → cancel_rental()
POST /api/rentals/rentals/{id}/update_status/   → update_status()
```

---

## 🔍 How Router Determines URL Name

The router converts your method name to a URL:

```python
Method Name          →  URL Path
─────────────────────────────────────────
dashboard_summary    →  /dashboard_summary/
active_rentals       →  /active_rentals/
pending_approvals    →  /pending_approvals/
seller_dashboard     →  /seller_dashboard/
```

**Rules:**
- Underscores stay as underscores (no conversion to hyphens)
- All lowercase
- Exactly matches method name

---

## 🆚 detail=True vs detail=False

### **detail=False** (List-level action)
```python
@action(detail=False, methods=['get'])
def dashboard_summary(self, request):
    pass
```

**URL:** `/api/rentals/rentals/dashboard_summary/`

**Use case:** Operations on collection (not specific object)
- Dashboard stats
- Bulk operations
- List filtering

---

### **detail=True** (Object-level action)
```python
@action(detail=True, methods=['post'])
def approve_rental(self, request, pk=None):
    pass
```

**URL:** `/api/rentals/rentals/123/approve/`

**Use case:** Operations on specific object
- Approve rental #123
- Cancel rental #456
- Update status of rental #789

---

## 🧪 Testing URL Resolution

### **Check if URL exists:**

```bash
# Using Django shell
python3 manage.py shell

>>> from django.urls import reverse
>>> reverse('rental-dashboard-summary')
'/api/rentals/rentals/dashboard_summary/'
```

### **List all URLs:**

```python
# In Django shell
from django.urls import get_resolver
resolver = get_resolver()
for pattern in resolver.url_patterns:
    print(pattern)
```

### **Test with cURL:**

```bash
curl -X GET \
  http://localhost:8000/api/rentals/rentals/dashboard_summary/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📚 URL Naming Convention

Router automatically creates names for URLs:

```
Format: {basename}-{action}

Examples:
─────────────────────────────────────────────
rental-list              → GET /rentals/
rental-detail            → GET /rentals/{id}/
rental-create            → POST /rentals/
rental-update            → PUT /rentals/{id}/
rental-dashboard-summary → GET /rentals/dashboard_summary/
rental-active-rentals    → GET /rentals/active_rentals/
```

**Usage in code:**
```python
from django.urls import reverse

# Get URL by name
url = reverse('rental-dashboard-summary')
# Returns: '/api/rentals/rentals/dashboard_summary/'

# With parameters
url = reverse('rental-detail', kwargs={'pk': 123})
# Returns: '/api/rentals/rentals/123/'
```

---

## 🎨 Visual Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT REQUEST                            │
│  GET /api/rentals/rentals/dashboard_summary/                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  config/urls.py                              │
│  urlpatterns = [                                            │
│      path('api/rentals/', include('rentals.urls')),  ◄──────│
│  ]                                                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  rentals/urls.py                             │
│  router = DefaultRouter()                                   │
│  router.register(r'rentals', RentalViewSet)  ◄──────────────│
│  urlpatterns = [path('', include(router.urls))]            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              DRF Router (Auto-magic!)                        │
│  • Scans RentalViewSet for methods                          │
│  • Finds @action decorators                                 │
│  • Creates URL patterns dynamically                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                rentals/views.py                              │
│  class RentalViewSet(viewsets.ModelViewSet):                │
│      @action(detail=False, methods=['get'])                 │
│      def dashboard_summary(self, request):  ◄────────────────│
│          return Response({...})                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   JSON RESPONSE                              │
│  { "summary": {...}, "monthly_stats": {...} }              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Takeaways

1. **DefaultRouter** automatically creates standard REST URLs
2. **@action** decorator adds custom endpoints
3. **detail=False** creates list-level URLs (`/rentals/action/`)
4. **detail=True** creates object-level URLs (`/rentals/{id}/action/`)
5. Method name becomes URL path
6. All combined through `include()` in main urls.py

---

## 📝 Quick Reference

| Component | Location | Purpose |
|-----------|----------|---------|
| Main routes | `config/urls.py` | Include app URLs |
| App routes | `rentals/urls.py` | Register ViewSets with router |
| ViewSet | `rentals/views.py` | Define actions and logic |
| Router | DRF library | Auto-generate URL patterns |
| @action | In ViewSet methods | Create custom endpoints |

---

## 🚀 Adding New Endpoints

Want to add a new endpoint? Just add an @action:

```python
# rentals/views.py

class RentalViewSet(viewsets.ModelViewSet):
    
    @action(detail=False, methods=['get'])
    def my_new_endpoint(self, request):
        """
        Automatically creates:
        GET /api/rentals/rentals/my_new_endpoint/
        """
        return Response({'message': 'Hello!'})
```

**No URL configuration needed!** The router handles it automatically! ✨

That's the beauty of Django REST Framework routers!
