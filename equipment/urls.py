from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, EquipmentViewSet, EquipmentImageViewSet, BannerViewSet, TagViewSet

app_name = 'equipment'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'equipment', EquipmentViewSet)
router.register(r'images', EquipmentImageViewSet)
router.register(r'banners', BannerViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]