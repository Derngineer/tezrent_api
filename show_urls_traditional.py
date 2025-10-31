"""
Show all URLs like traditional Django urls.py
This makes it easy to see what URLs exist in your API
"""

import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import get_resolver
from rest_framework.routers import DefaultRouter
from rentals.views import RentalViewSet

print("=" * 100)
print("YOUR API URLS - Traditional Django Style View")
print("=" * 100)
print()

# Show what the router generates
router = DefaultRouter()
router.register(r'rentals', RentalViewSet, basename='rental')

print("🔹 From: rentals/urls.py → router.register(r'rentals', RentalViewSet, basename='rental')")
print()
print("This creates these URLs:")
print()

urls_list = []

for pattern in router.urls:
    url_pattern = str(pattern.pattern)
    url_name = pattern.name if hasattr(pattern, 'name') else 'N/A'
    
    # Clean up the pattern for display
    url_pattern = url_pattern.replace('^', '').replace('$', '').replace('\\', '')
    
    # Add prefix from config/urls.py
    full_url = f"/api/rentals/{url_pattern}"
    
    urls_list.append({
        'url': full_url,
        'name': url_name,
        'pattern': url_pattern
    })

# Sort by URL for better readability
urls_list.sort(key=lambda x: x['url'])

# Print in traditional Django style
print("urlpatterns = [")
for item in urls_list:
    # Determine the method type from the URL
    if '{pk}' in item['url'] or '{id}' in item['url']:
        url_type = "    # Detail URL (requires ID)"
    else:
        url_type = "    # List URL (no ID needed)"
    
    print(f"{url_type}")
    print(f"    path('{item['url']}', name='{item['name']}'),")
    print()

print("]")
print()
print("=" * 100)
print("URL NAME → FULL URL MAPPING")
print("=" * 100)
print()

for item in urls_list:
    print(f"{item['name']:<40} → {item['url']}")

print()
print("=" * 100)
print("HOW TO USE IN CODE")
print("=" * 100)
print()
print("# Get URL by name:")
print("from django.urls import reverse")
print()
print("# Example 1: List all rentals")
print("url = reverse('rental-list')")
print("# Returns: '/api/rentals/rentals/'")
print()
print("# Example 2: Dashboard summary")
print("url = reverse('rental-dashboard-summary')")
print("# Returns: '/api/rentals/rentals/dashboard_summary/'")
print()
print("# Example 3: Specific rental detail")
print("url = reverse('rental-detail', kwargs={'pk': 123})")
print("# Returns: '/api/rentals/rentals/123/'")
print()
