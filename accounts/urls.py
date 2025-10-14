from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    CustomerRegistrationView,
    CompanyRegistrationView,
    UserProfileView,
    get_location_choices,
)

app_name = 'accounts'

urlpatterns = [
    # Registration endpoints
    path('register/customer/', CustomerRegistrationView.as_view(), name='register-customer'),
    path('register/company/', CompanyRegistrationView.as_view(), name='register-company'),
    
    # Profile endpoint
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # JWT authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Location choices endpoint
    path('location-choices/', get_location_choices, name='location-choices'),
]