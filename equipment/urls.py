from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, EquipmentViewSet, EquipmentImageViewSet

app_name = 'equipment'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'equipment', EquipmentViewSet)
router.register(r'images', EquipmentImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]