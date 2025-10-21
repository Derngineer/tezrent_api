from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FavoriteViewSet, FavoriteCollectionViewSet, RecentlyViewedViewSet

app_name = 'favorites'

router = DefaultRouter()
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'collections', FavoriteCollectionViewSet, basename='collection')
router.register(r'recently-viewed', RecentlyViewedViewSet, basename='recently-viewed')

urlpatterns = [
    path('', include(router.urls)),
]
