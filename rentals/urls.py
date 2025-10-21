from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RentalViewSet, RentalReviewViewSet

app_name = 'rentals'

router = DefaultRouter()
router.register(r'rentals', RentalViewSet, basename='rental')
router.register(r'reviews', RentalReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]
