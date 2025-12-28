"""
Ziina Payment Views

Handles payment initiation and verification for equipment rentals.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rentals.models import Rental, RentalPayment
from .services import ZiinaClient

import logging

logger = logging.getLogger(__name__)


class InitiatePaymentView(APIView):
    """
    Initiate a Ziina payment for a rental
    
    POST /api/payments/ziina/initiate/
    
    Request Body:
    {
        "rental_id": 123,
        "success_url": "tezrent://payment/success",  // Optional, has default
        "cancel_url": "tezrent://payment/failed"     // Optional, has default
    }
    
    Response (Success):
    {
        "success": true,
        "payment_id": "pi_xxxx",
        "redirect_url": "https://pay.ziina.com/xxxx",
        "rental_reference": "RNT-2024-001",
        "amount": 1500,
        "currency": "AED"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        rental_id = request.data.get('rental_id')
        
        if not rental_id:
            return Response(
                {"error": "rental_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the rental
        try:
            rental = Rental.objects.get(id=rental_id)
        except Rental.DoesNotExist:
            return Response(
                {"error": "Rental not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify the user owns this rental (customer)
        if rental.customer.user != request.user:
            return Response(
                {"error": "You can only pay for your own rentals"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check rental is in a payable state
        if rental.status not in ['approved', 'payment_pending']:
            return Response(
                {"error": f"Rental cannot be paid in '{rental.status}' status. Must be 'approved' or 'payment_pending'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if there's already a pending payment
        existing_payment = RentalPayment.objects.filter(
            rental=rental,
            payment_method='card',
            payment_status__in=['pending', 'processing']
        ).first()
        
        if existing_payment and existing_payment.gateway_reference:
            # Return the existing payment URL
            ziina_client = ZiinaClient()
            payment_status = ziina_client.get_payment_status(existing_payment.gateway_reference)
            
            if payment_status.get('success') and not payment_status.get('is_completed'):
                return Response({
                    "success": True,
                    "payment_id": existing_payment.gateway_reference,
                    "redirect_url": payment_status.get('raw_response', {}).get('redirect_url'),
                    "rental_reference": rental.rental_reference,
                    "amount": int(rental.total_amount * 100),  # Convert to fils
                    "currency": "AED",
                    "message": "Existing payment session found"
                })
        
        # Get redirect URLs from request or use defaults (for testing)
        success_url = request.data.get('success_url', 'https://tezrent.com/en')
        cancel_url = request.data.get('cancel_url', 'https://tezrent.com/uz')
        
        # Convert amount to smallest unit (fils for AED, cents for USD)
        # Assuming total_amount is in AED
        amount_in_fils = int(rental.total_amount * 100)
        
        # Create Ziina payment intent
        ziina_client = ZiinaClient()
        result = ziina_client.create_payment_intent(
            amount=amount_in_fils,
            rental_reference=rental.rental_reference,
            success_url=success_url,
            cancel_url=cancel_url,
            currency_code="AED",
            message=f"Rental payment for {rental.equipment.name} - {rental.rental_reference}"
        )
        
        if not result.get('success'):
            logger.error(f"Failed to create Ziina payment for rental {rental_id}: {result.get('error')}")
            return Response(
                {"error": result.get('error', 'Failed to create payment')},
                status=status.HTTP_502_BAD_GATEWAY
            )
        
        # Create or update RentalPayment record
        payment = RentalPayment.objects.create(
            rental=rental,
            payment_type='rental_fee',
            amount=rental.total_amount,
            payment_method='card',
            payment_status='pending',
            gateway_reference=result.get('payment_id'),
            gateway_response=result.get('raw_response', {}),
            notes=f"Ziina payment initiated at {timezone.now()}"
        )
        
        # Update rental status to payment_pending
        if rental.status == 'approved':
            rental.status = 'payment_pending'
            rental.save()
        
        logger.info(f"Ziina payment initiated for rental {rental.rental_reference}, payment_id: {result.get('payment_id')}")
        
        return Response({
            "success": True,
            "payment_id": result.get('payment_id'),
            "redirect_url": result.get('redirect_url'),
            "rental_reference": rental.rental_reference,
            "amount": amount_in_fils,
            "currency": "AED",
            "rental_payment_id": payment.id
        })


class VerifyPaymentView(APIView):
    """
    Verify a Ziina payment after user returns from payment page
    
    POST /api/payments/ziina/verify/
    
    Request Body:
    {
        "payment_id": "pi_xxxx",
        "rental_id": 123
    }
    
    Response (Success):
    {
        "success": true,
        "payment_status": "completed",
        "rental_status": "confirmed",
        "message": "Payment successful! Your rental is confirmed."
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        payment_id = request.data.get('payment_id')
        rental_id = request.data.get('rental_id')
        
        if not payment_id:
            return Response(
                {"error": "payment_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find the payment record
        try:
            if rental_id:
                payment = RentalPayment.objects.get(
                    gateway_reference=payment_id,
                    rental_id=rental_id
                )
            else:
                payment = RentalPayment.objects.get(gateway_reference=payment_id)
        except RentalPayment.DoesNotExist:
            return Response(
                {"error": "Payment record not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        rental = payment.rental
        
        # Verify user owns this rental
        if rental.customer.user != request.user:
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check payment status with Ziina
        ziina_client = ZiinaClient()
        result = ziina_client.get_payment_status(payment_id)
        
        if not result.get('success'):
            return Response(
                {"error": result.get('error', 'Could not verify payment')},
                status=status.HTTP_502_BAD_GATEWAY
            )
        
        ziina_status = result.get('status')
        
        # Update payment record
        payment.gateway_response = result.get('raw_response', {})
        
        if ziina_status == 'completed':
            payment.payment_status = 'completed'
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update rental status to confirmed
            rental.status = 'confirmed'
            rental.save()
            
            logger.info(f"Payment completed for rental {rental.rental_reference}")
            
            return Response({
                "success": True,
                "payment_status": "completed",
                "rental_status": "confirmed",
                "rental_reference": rental.rental_reference,
                "message": "Payment successful! Your rental is confirmed."
            })
        
        elif ziina_status == 'requires_payment_instrument':
            payment.payment_status = 'pending'
            payment.save()
            
            return Response({
                "success": False,
                "payment_status": "requires_payment",
                "rental_status": rental.status,
                "message": "Payment not completed. Please add a payment method."
            })
        
        elif ziina_status == 'requires_user_action':
            payment.payment_status = 'processing'
            payment.save()
            
            return Response({
                "success": False,
                "payment_status": "requires_action",
                "rental_status": rental.status,
                "message": "Additional action required to complete payment."
            })
        
        else:
            # Handle failed or other statuses
            payment.payment_status = 'failed'
            payment.save()
            
            return Response({
                "success": False,
                "payment_status": ziina_status,
                "rental_status": rental.status,
                "message": f"Payment status: {ziina_status}"
            })


class PaymentStatusView(APIView):
    """
    Get current payment status for a rental
    
    GET /api/payments/ziina/status/{rental_id}/
    
    Response:
    {
        "rental_id": 123,
        "rental_reference": "RNT-2024-001",
        "rental_status": "payment_pending",
        "total_amount": "150.00",
        "payments": [
            {
                "id": 1,
                "payment_type": "rental_fee",
                "amount": "150.00",
                "status": "pending",
                "gateway_reference": "pi_xxxx"
            }
        ],
        "is_fully_paid": false
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, rental_id):
        try:
            rental = Rental.objects.get(id=rental_id)
        except Rental.DoesNotExist:
            return Response(
                {"error": "Rental not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify user has access (customer or seller)
        user = request.user
        is_customer = hasattr(user, 'customer_profile') and rental.customer == user.customer_profile
        is_seller = hasattr(user, 'company_profile') and rental.seller == user.company_profile
        
        if not (is_customer or is_seller):
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all payments for this rental
        payments = RentalPayment.objects.filter(rental=rental).order_by('-created_at')
        
        payment_data = []
        for p in payments:
            payment_data.append({
                "id": p.id,
                "payment_type": p.payment_type,
                "payment_type_display": p.get_payment_type_display(),
                "amount": str(p.amount),
                "status": p.payment_status,
                "status_display": p.get_payment_status_display(),
                "method": p.payment_method,
                "gateway_reference": p.gateway_reference,
                "created_at": p.created_at.isoformat(),
                "completed_at": p.completed_at.isoformat() if p.completed_at else None
            })
        
        # Calculate if fully paid
        completed_payments = payments.filter(payment_status='completed')
        total_paid = sum(p.amount for p in completed_payments)
        is_fully_paid = total_paid >= rental.total_amount
        
        return Response({
            "rental_id": rental.id,
            "rental_reference": rental.rental_reference,
            "rental_status": rental.status,
            "rental_status_display": rental.get_status_display(),
            "total_amount": str(rental.total_amount),
            "total_paid": str(total_paid),
            "remaining_amount": str(max(0, rental.total_amount - total_paid)),
            "payments": payment_data,
            "is_fully_paid": is_fully_paid
        })
