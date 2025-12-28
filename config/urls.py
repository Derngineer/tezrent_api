"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .health import health_check

# Customize Django Admin Site
admin.site.site_header = "TezRent Administration"
admin.site.site_title = "TezRent Admin Portal"
admin.site.index_title = "Welcome to TezRent Equipment Rental Management"

urlpatterns = [
    path('health/', health_check, name='health_check'),  # Quick database test
    path('admin/', admin.site.urls),
    # Include accounts URLs under the api/accounts/ path
    path('api/accounts/', include('accounts.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/equipment/', include('equipment.urls')),
    path('api/rentals/', include('rentals.urls')),
    path('api/favorites/', include('favorites.urls')),
    path('api/crm/', include('crm.urls')),
    path('api/payments/', include('payments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
