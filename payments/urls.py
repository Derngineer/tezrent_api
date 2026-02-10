"""
Payment URLs

Routes for Ziina payment gateway integration.
"""

from django.urls import path
from .views import (
    InitiatePaymentView, 
    VerifyPaymentView, 
    PaymentStatusView,
    ZiinaWebhookView,
    PaymentReceiptView,
    ResendReceiptEmailView,
)

urlpatterns = [
    # Ziina payment endpoints
    path('ziina/initiate/', InitiatePaymentView.as_view(), name='ziina-initiate'),
    path('ziina/verify/', VerifyPaymentView.as_view(), name='ziina-verify'),
    path('ziina/status/<int:rental_id>/', PaymentStatusView.as_view(), name='ziina-status'),
    path('ziina/webhook/', ZiinaWebhookView.as_view(), name='ziina-webhook'),
    
    # Receipt endpoints
    path('receipt/<str:payment_id>/', PaymentReceiptView.as_view(), name='payment-receipt'),
    path('receipt/<str:payment_id>/resend/', ResendReceiptEmailView.as_view(), name='resend-receipt'),
]
