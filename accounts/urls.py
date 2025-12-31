from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    CustomerRegistrationView,
    CompanyRegistrationView,
    UserProfileView,
    get_location_choices,
    PasswordResetRequestView,
    PasswordResetVerifyView,
    PasswordResetConfirmView,
    ChangePasswordView,
    DeliveryAddressViewSet,
    OTPRequestView,
    OTPVerifyView,
    OTPSignupRequestView,
    OTPSignupVerifyView
)

app_name = 'accounts'

router = DefaultRouter()
router.register(r'addresses', DeliveryAddressViewSet, basename='delivery-address')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Registration endpoints
    path('register/customer/', CustomerRegistrationView.as_view(), name='register-customer'),
    path('register/company/', CompanyRegistrationView.as_view(), name='register-company'),
    path('seller/register/', CompanyRegistrationView.as_view(), name='register-seller'),  # Alias for company registration
    
    # Profile endpoint
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # JWT authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # OTP authentication endpoints (passwordless login alternative)
    path('otp/request/', OTPRequestView.as_view(), name='otp-request'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp-verify'),
    
    # OTP signup endpoints (passwordless registration)
    path('otp/signup-request/', OTPSignupRequestView.as_view(), name='otp-signup-request'),
    path('otp/signup-verify/', OTPSignupVerifyView.as_view(), name='otp-signup-verify'),

    # Password management endpoints
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/verify/', PasswordResetVerifyView.as_view(), name='password-reset-verify'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm-alt'),  # Alternative URL
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    # Location choices endpoint
    path('location-choices/', get_location_choices, name='location-choices'),
]