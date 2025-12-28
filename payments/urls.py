"""
Payment URLs

Routes for Ziina payment gateway integration.
"""

from django.urls import path
from .views import InitiatePaymentView, VerifyPaymentView, PaymentStatusView

urlpatterns = [
    # Ziina payment endpoints
    path('ziina/initiate/', InitiatePaymentView.as_view(), name='ziina-initiate'),
    path('ziina/verify/', VerifyPaymentView.as_view(), name='ziina-verify'),
    path('ziina/status/<int:rental_id>/', PaymentStatusView.as_view(), name='ziina-status'),
]
