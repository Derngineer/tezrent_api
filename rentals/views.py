from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Rental, RentalStatusUpdate, RentalImage, RentalReview,
    RentalPayment, RentalDocument, RentalSale
)
from .serializers import (
    RentalListSerializer, RentalDetailSerializer, RentalCreateSerializer,
    RentalUpdateStatusSerializer, RentalStatusUpdateSerializer,
    RentalImageSerializer, RentalImageUploadSerializer, RentalReviewSerializer,
    RentalPaymentSerializer, RentalDocumentSerializer
)
from .filters import RentalFilter


class RentalViewSet(viewsets.ModelViewSet):
    """
    API endpoint for rentals - supports both customer and seller apps
    """
    queryset = Rental.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RentalFilter
    search_fields = ['rental_reference', 'equipment__name']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'total_amount']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RentalListSerializer
        elif self.action == 'create':
            return RentalCreateSerializer
        return RentalDetailSerializer
    
    def get_queryset(self):
        """Filter rentals based on user type"""
        user = self.request.user
        queryset = Rental.objects.all()
        
        # Customer: see their own rentals
        if hasattr(user, 'customer_profile'):
            queryset = queryset.filter(customer=user.customer_profile)
        # Seller: see rentals for their equipment
        elif hasattr(user, 'company_profile'):
            queryset = queryset.filter(seller=user.company_profile)
        else:
            # Staff can see all
            pass
        
        return queryset.select_related(
            'equipment', 'customer', 'seller', 'customer__user', 'seller__user'
        ).prefetch_related(
            'status_updates', 'images', 'payments', 'documents'
        )
    
    def perform_create(self, serializer):
        """Create rental request"""
        rental = serializer.save()
        
        # TODO: Send notification to seller
        # send_rental_request_notification(rental)
        
        return rental
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update rental status (seller or system)"""
        rental = self.get_object()
        serializer = RentalUpdateStatusSerializer(
            data=request.data,
            context={'rental': rental, 'request': request}
        )
        
        if serializer.is_valid():
            old_status = rental.status
            new_status = serializer.validated_data['new_status']
            notes = serializer.validated_data.get('notes', '')
            
            # Update rental status
            rental.status = new_status
            
            # Handle status-specific actions
            if new_status == 'approved':
                rental.approved_at = timezone.now()
            elif new_status == 'delivered':
                rental.actual_start_date = timezone.now()
            elif new_status == 'completed':
                rental.actual_end_date = timezone.now()
            elif new_status == 'cancelled':
                rental.cancelled_at = timezone.now()
            
            rental.save()
            
            # Create status update record
            RentalStatusUpdate.objects.create(
                rental=rental,
                old_status=old_status,
                new_status=new_status,
                updated_by=request.user,
                notes=notes,
                is_visible_to_customer=serializer.validated_data['is_visible_to_customer']
            )
            
            # TODO: Send notification
            # send_status_update_notification(rental, old_status, new_status)
            
            return Response({
                'message': f'Rental status updated to {new_status}',
                'rental': RentalDetailSerializer(rental, context={'request': request}).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve rental request (seller only)"""
        rental = self.get_object()
        
        if not hasattr(request.user, 'company_profile'):
            return Response(
                {'error': 'Only sellers can approve rentals'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if rental.seller != request.user.company_profile:
            return Response(
                {'error': 'You can only approve your own rental requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if rental.status != 'pending':
            return Response(
                {'error': 'Only pending rentals can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rental.status = 'approved'
        rental.approved_at = timezone.now()
        rental.save()
        
        RentalStatusUpdate.objects.create(
            rental=rental,
            old_status='pending',
            new_status='approved',
            updated_by=request.user,
            notes='Rental request approved by seller',
            is_visible_to_customer=True
        )
        
        return Response({
            'message': 'Rental approved successfully',
            'rental': RentalDetailSerializer(rental, context={'request': request}).data
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject rental request (seller only)"""
        rental = self.get_object()
        reason = request.data.get('reason', 'No reason provided')
        
        if not hasattr(request.user, 'company_profile'):
            return Response(
                {'error': 'Only sellers can reject rentals'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if rental.status != 'pending':
            return Response(
                {'error': 'Only pending rentals can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rental.status = 'cancelled'
        rental.cancelled_at = timezone.now()
        rental.cancellation_reason = reason
        rental.save()
        
        RentalStatusUpdate.objects.create(
            rental=rental,
            old_status='pending',
            new_status='cancelled',
            updated_by=request.user,
            notes=f'Rejected by seller: {reason}',
            is_visible_to_customer=True
        )
        
        return Response({'message': 'Rental rejected'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel rental (customer only, before delivery)"""
        rental = self.get_object()
        reason = request.data.get('reason', 'Cancelled by customer')
        
        if not hasattr(request.user, 'customer_profile'):
            return Response(
                {'error': 'Only customers can cancel their rentals'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if rental.status not in ['pending', 'approved']:
            return Response(
                {'error': 'Can only cancel pending or approved rentals'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rental.status = 'cancelled'
        rental.cancelled_at = timezone.now()
        rental.cancellation_reason = reason
        rental.save()
        
        RentalStatusUpdate.objects.create(
            rental=rental,
            old_status=rental.status,
            new_status='cancelled',
            updated_by=request.user,
            notes=reason,
            is_visible_to_customer=True
        )
        
        return Response({'message': 'Rental cancelled successfully'})
    
    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Upload rental image (delivery, damage, etc.)"""
        rental = self.get_object()
        
        serializer = RentalImageUploadSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save(rental=rental)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def upload_payment_receipt(self, request, pk=None):
        """Upload payment receipt for cash on delivery (seller only)"""
        rental = self.get_object()
        
        # Only seller can upload receipt
        if not hasattr(request.user, 'company_profile'):
            return Response(
                {'error': 'Only sellers can upload payment receipts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if rental.seller != request.user.company_profile:
            return Response(
                {'error': 'You can only upload receipts for your own rentals'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get payment (or create one if needed)
        payment_id = request.data.get('payment_id')
        if payment_id:
            try:
                payment = RentalPayment.objects.get(id=payment_id, rental=rental)
            except RentalPayment.DoesNotExist:
                return Response(
                    {'error': 'Payment not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Create payment if not exists
            payment = RentalPayment.objects.filter(
                rental=rental,
                payment_method='cash_on_delivery'
            ).first()
            
            if not payment:
                payment = RentalPayment.objects.create(
                    rental=rental,
                    payment_type='full',
                    amount=rental.total_amount,
                    payment_method='cash_on_delivery',
                    payment_status='completed',
                    completed_at=timezone.now()
                )
        
        # Update payment with receipt
        receipt_file = request.FILES.get('receipt_file')
        receipt_number = request.data.get('receipt_number', '')
        notes = request.data.get('notes', '')
        
        if receipt_file:
            payment.receipt_file = receipt_file
        payment.receipt_number = receipt_number
        payment.notes = notes
        payment.payment_status = 'completed'
        payment.completed_at = timezone.now()
        payment.save()
        
        # Update rental status if needed
        if rental.status == 'approved':
            rental.status = 'confirmed'
            rental.save()
            
            RentalStatusUpdate.objects.create(
                rental=rental,
                old_status='approved',
                new_status='confirmed',
                updated_by=request.user,
                notes='Payment confirmed with receipt',
                is_visible_to_customer=True
            )
        
        serializer = RentalPaymentSerializer(payment, context={'request': request})
        return Response({
            'message': 'Payment receipt uploaded successfully',
            'payment': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get rental documents (filtered by visibility and payment status)"""
        rental = self.get_object()
        user = request.user
        
        # Get all documents for this rental
        documents = RentalDocument.objects.filter(rental=rental)
        
        # Filter based on user type
        if hasattr(user, 'customer_profile') and rental.customer == user.customer_profile:
            # Customer: only see documents visible to them
            documents = documents.filter(visible_to_customer=True)
        elif hasattr(user, 'company_profile') and rental.seller == user.company_profile:
            # Seller: can see all documents
            pass
        else:
            # Others: no access
            return Response(
                {'error': 'You do not have access to these documents'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = RentalDocumentSerializer(
            documents,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'count': documents.count(),
            'documents': serializer.data
        })
    
    @action(
        detail=True, 
        methods=['post'], 
        parser_classes=[MultiPartParser, FormParser],
        permission_classes=[permissions.IsAuthenticated]
    )
    def upload_document(self, request, pk=None):
        """Upload rental document (seller or customer)"""
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required. Please provide a valid token.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        rental = self.get_object()
        
        # Verify user has access to this rental
        user = request.user
        has_access = False
        
        if hasattr(user, 'customer_profile'):
            has_access = rental.customer == user.customer_profile
        elif hasattr(user, 'company_profile'):
            has_access = rental.seller == user.company_profile
        else:
            return Response(
                {'error': 'You must have either a customer or company profile to upload documents.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not has_access:
            return Response(
                {'error': 'Access denied. You do not have permission to upload documents for this rental.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get document data
        document_type = request.data.get('document_type')
        title = request.data.get('title')
        file = request.FILES.get('file')
        visible_to_customer = request.data.get('visible_to_customer', 'true')
        
        # Convert string to boolean
        if isinstance(visible_to_customer, str):
            visible_to_customer = visible_to_customer.lower() in ['true', '1', 'yes']
        
        # Validation
        if not document_type:
            return Response(
                {'error': 'document_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not title:
            return Response(
                {'error': 'title is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not file:
            return Response(
                {'error': 'file is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (max 10MB)
        if file.size > 10 * 1024 * 1024:
            return Response(
                {'error': 'File size must be less than 10MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create document
            document = RentalDocument.objects.create(
                rental=rental,
                document_type=document_type,
                title=title,
                file=file,
                uploaded_by=user,
                visible_to_customer=visible_to_customer,
                requires_payment=False
            )
            
            serializer = RentalDocumentSerializer(document, context={'request': request})
            return Response({
                'message': 'Document uploaded successfully',
                'document': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': f'Failed to upload document: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def submit_review(self, request, pk=None):
        """Submit review for completed rental (customer only)"""
        rental = self.get_object()
        
        if not hasattr(request.user, 'customer_profile'):
            return Response(
                {'error': 'Only customers can submit reviews'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if rental.status != 'completed':
            return Response(
                {'error': 'Can only review completed rentals'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if hasattr(rental, 'review'):
            return Response(
                {'error': 'Review already submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = RentalReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                rental=rental,
                customer=request.user.customer_profile
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # ========== REACT NATIVE MOBILE ENDPOINTS ==========
    
    @action(detail=False, methods=['get'])
    def customer_dashboard(self, request):
        """Customer dashboard data for React Native"""
        if not hasattr(request.user, 'customer_profile'):
            return Response(
                {'error': 'Customer profile required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        customer = request.user.customer_profile
        rentals = Rental.objects.filter(customer=customer)
        
        # Dashboard stats
        stats = {
            'total_rentals': rentals.count(),
            'active_rentals': rentals.filter(
                status__in=['approved', 'payment_pending', 'confirmed', 'preparing', 
                           'ready_for_pickup', 'out_for_delivery', 'delivered', 'in_progress']
            ).count(),
            'pending_rentals': rentals.filter(status='pending').count(),
            'completed_rentals': rentals.filter(status='completed').count(),
            'total_spent': sum(r.total_amount for r in rentals.filter(status='completed')),
        }
        
        # Active rentals (most recent)
        active_rentals = rentals.filter(
            status__in=['approved', 'payment_pending', 'confirmed', 'preparing',
                       'ready_for_pickup', 'out_for_delivery', 'delivered', 'in_progress']
        ).order_by('-start_date')[:5]
        
        serializer = RentalListSerializer(
            active_rentals,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'stats': stats,
            'active_rentals': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def seller_dashboard(self, request):
        """Seller dashboard data for React Native"""
        if not hasattr(request.user, 'company_profile'):
            return Response(
                {'error': 'Company profile required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        seller = request.user.company_profile
        rentals = Rental.objects.filter(seller=seller)
        
        # Dashboard stats
        stats = {
            'total_orders': rentals.count(),
            'pending_approvals': rentals.filter(status='pending').count(),
            'active_rentals': rentals.filter(
                status__in=['approved', 'payment_pending', 'confirmed', 'preparing', 
                           'ready_for_pickup', 'out_for_delivery', 'delivered', 'in_progress']
            ).count(),
            'completed_rentals': rentals.filter(status='completed').count(),
            'total_revenue': sum(r.total_amount for r in rentals.filter(status='completed')),
            'pending_returns': rentals.filter(
                status__in=['return_requested', 'returning']
            ).count(),
        }
        
        # Pending approvals
        pending_rentals = rentals.filter(status='pending').order_by('-created_at')[:5]
        
        # Active rentals (awaiting payment or in progress)
        active_rentals = rentals.filter(
            status__in=['approved', 'payment_pending', 'confirmed', 'preparing', 
                       'ready_for_pickup', 'out_for_delivery', 'delivered', 'in_progress']
        ).order_by('-start_date')[:5]
        
        return Response({
            'stats': stats,
            'pending_approvals': RentalListSerializer(
                pending_rentals,
                many=True,
                context={'request': request}
            ).data,
            'active_rentals': RentalListSerializer(
                active_rentals,
                many=True,
                context={'request': request}
            ).data
        })
    
    @action(detail=False, methods=['get'])
    def my_rentals(self, request):
        """Get user's rentals with filtering (mobile optimized)"""
        queryset = self.get_queryset()
        
        # Filters for mobile
        rental_status = request.query_params.get('status')
        if rental_status:
            queryset = queryset.filter(status=rental_status)
        
        # Date filters
        upcoming = request.query_params.get('upcoming') == 'true'
        if upcoming:
            queryset = queryset.filter(
                start_date__gte=timezone.now().date(),
                status__in=['pending', 'approved', 'confirmed', 'preparing']
            )
        
        past = request.query_params.get('past') == 'true'
        if past:
            queryset = queryset.filter(status='completed')
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = queryset.count()
        results = queryset[start:end]
        
        serializer = RentalListSerializer(results, many=True, context={'request': request})
        
        return Response({
            'count': total_count,
            'has_next': end < total_count,
            'has_previous': page > 1,
            'current_page': page,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def active_rentals(self, request):
        """Get all active rentals for current user"""
        queryset = self.get_queryset()
        
        # Filter for active statuses (includes approved rentals waiting for payment)
        active_rentals = queryset.filter(
            status__in=['approved', 'payment_pending', 'confirmed', 'preparing', 
                       'ready_for_pickup', 'out_for_delivery', 'delivered', 'in_progress']
        ).order_by('-start_date')
        
        serializer = RentalListSerializer(
            active_rentals,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'count': active_rentals.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """Get all pending approval rentals (for sellers)"""
        if not hasattr(request.user, 'company_profile'):
            return Response(
                {'error': 'Company profile required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        seller = request.user.company_profile
        pending_rentals = Rental.objects.filter(
            seller=seller,
            status='pending'
        ).order_by('-created_at')
        
        serializer = RentalListSerializer(
            pending_rentals,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'count': pending_rentals.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def rental_history(self, request):
        """Get rental history with analytics (customer)"""
        if not hasattr(request.user, 'customer_profile'):
            return Response(
                {'error': 'Customer profile required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rentals = Rental.objects.filter(
            customer=request.user.customer_profile,
            status='completed'
        ).order_by('-completed_at', '-end_date')
        
        serializer = RentalListSerializer(rentals, many=True, context={'request': request})
        
        return Response({
            'count': rentals.count(),
            'rentals': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def sales(self, request):
        """
        Get sales records (completed rentals with financial data).
        For revenue tracking and transaction history.
        
        Query params:
        - seller: Filter by seller ID
        - payout_status: pending, processing, completed, failed, on_hold
        - start_date: Filter from date (YYYY-MM-DD)
        - end_date: Filter to date (YYYY-MM-DD)
        """
        from .models import RentalSale
        from .serializers import RentalSaleSerializer
        
        # Base queryset
        queryset = RentalSale.objects.select_related(
            'rental', 'seller', 'customer', 'equipment'
        ).all()
        
        # Filter by seller (for seller dashboard)
        if hasattr(request.user, 'company_profile'):
            seller_id = request.query_params.get('seller')
            if seller_id:
                queryset = queryset.filter(seller_id=seller_id)
            else:
                # Default: show only their sales
                queryset = queryset.filter(seller=request.user.company_profile)
        
        # Filter by payout status
        payout_status = request.query_params.get('payout_status')
        if payout_status:
            queryset = queryset.filter(payout_status=payout_status)
        
        # Date range filters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(sale_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(sale_date__lte=end_date)
        
        # Order by most recent
        queryset = queryset.order_by('-sale_date')
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RentalSaleSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = RentalSaleSerializer(queryset, many=True, context={'request': request})
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def revenue_summary(self, request):
        """
        Get revenue summary for financials dashboard.
        Returns total revenue, commission, payouts, and trends.
        """
        from .models import RentalSale
        from datetime import timedelta
        
        # Base queryset
        queryset = RentalSale.objects.all()
        
        # Filter by seller
        if hasattr(request.user, 'company_profile'):
            queryset = queryset.filter(seller=request.user.company_profile)
        
        # Get date ranges
        today = timezone.now()
        this_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        this_year_start = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Overall metrics - use separate aggregations
        total_sales = queryset.count()
        
        revenue_stats = queryset.aggregate(
            total_revenue=Sum('total_revenue'),
            total_commission=Sum('platform_commission_amount'),
            total_payout=Sum('seller_payout')
        )
        
        # Calculate averages separately
        avg_stats = queryset.aggregate(
            avg_sale=Avg('total_revenue'),
            avg_rental_days=Avg('rental_days')
        )
        
        # Combine overall stats
        overall_stats = {
            'total_sales': total_sales,
            'total_revenue': revenue_stats['total_revenue'] or 0,
            'total_commission': revenue_stats['total_commission'] or 0,
            'total_payout': revenue_stats['total_payout'] or 0,
            'avg_sale': avg_stats['avg_sale'] or 0,
            'avg_rental_days': avg_stats['avg_rental_days'] or 0
        }
        
        # This month
        this_month_qs = queryset.filter(sale_date__gte=this_month_start)
        this_month = {
            'sales': this_month_qs.count(),
            'revenue': this_month_qs.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0,
            'payout': this_month_qs.aggregate(Sum('seller_payout'))['seller_payout__sum'] or 0
        }
        
        # Last month
        last_month_qs = queryset.filter(
            sale_date__gte=last_month_start,
            sale_date__lt=this_month_start
        )
        last_month = {
            'sales': last_month_qs.count(),
            'revenue': last_month_qs.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0,
            'payout': last_month_qs.aggregate(Sum('seller_payout'))['seller_payout__sum'] or 0
        }
        
        # This year
        this_year_qs = queryset.filter(sale_date__gte=this_year_start)
        this_year = {
            'sales': this_year_qs.count(),
            'revenue': this_year_qs.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0,
            'payout': this_year_qs.aggregate(Sum('seller_payout'))['seller_payout__sum'] or 0
        }
        
        # Pending payouts
        pending_qs = queryset.filter(payout_status='pending')
        pending_payouts = {
            'count': pending_qs.count(),
            'amount': pending_qs.aggregate(Sum('seller_payout'))['seller_payout__sum'] or 0
        }
        
        # Calculate growth percentages
        revenue_growth = 0
        if last_month['revenue'] and last_month['revenue'] > 0:
            revenue_growth = (
                (this_month['revenue'] - last_month['revenue'])
            ) / last_month['revenue'] * 100
        
        sales_growth = 0
        if last_month['sales'] and last_month['sales'] > 0:
            sales_growth = (
                (this_month['sales'] - last_month['sales'])
            ) / last_month['sales'] * 100
        
        return Response({
            'overview': {
                'total_sales': overall_stats['total_sales'],
                'total_revenue': float(overall_stats['total_revenue']),
                'total_commission': float(overall_stats['total_commission']),
                'total_payout': float(overall_stats['total_payout']),
                'average_sale_value': float(overall_stats['avg_sale']),
                'average_rental_days': float(overall_stats['avg_rental_days']),
            },
            'this_month': {
                'sales': this_month['sales'],
                'revenue': float(this_month['revenue']),
                'payout': float(this_month['payout']),
            },
            'last_month': {
                'sales': last_month['sales'],
                'revenue': float(last_month['revenue']),
                'payout': float(last_month['payout']),
            },
            'this_year': {
                'sales': this_year['sales'],
                'revenue': float(this_year['revenue']),
                'payout': float(this_year['payout']),
            },
            'growth': {
                'revenue_percentage': round(revenue_growth, 2),
                'sales_percentage': round(sales_growth, 2),
            },
            'pending_payouts': {
                'count': pending_payouts['count'],
                'amount': float(pending_payouts['amount']),
            }
        })
    
    @action(detail=False, methods=['get'])
    def transactions(self, request):
        """
        Get transaction history for financials page.
        Shows all completed sales with payment details.
        """
        from .models import RentalSale
        from .serializers import RentalSaleSerializer
        
        # Get sales for this seller
        queryset = RentalSale.objects.select_related(
            'rental', 'seller', 'customer', 'equipment'
        )
        
        if hasattr(request.user, 'company_profile'):
            queryset = queryset.filter(seller=request.user.company_profile)
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(sale_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(sale_date__lte=end_date)
        
        # Filter by payout status
        payout_status = request.query_params.get('payout_status')
        if payout_status:
            queryset = queryset.filter(payout_status=payout_status)
        
        # Order by most recent
        queryset = queryset.order_by('-sale_date')
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RentalSaleSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = RentalSaleSerializer(queryset, many=True, context={'request': request})
        
        # Calculate totals for this page/filter
        totals = queryset.aggregate(
            total_revenue=Sum('total_revenue'),
            total_commission=Sum('platform_commission_amount'),
            total_payout=Sum('seller_payout')
        )
        
        return Response({
            'count': queryset.count(),
            'totals': {
                'revenue': float(totals['total_revenue'] or 0),
                'commission': float(totals['total_commission'] or 0),
                'payout': float(totals['total_payout'] or 0),
            },
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """
        Platform-wide dashboard summary with key metrics (OPTIMIZED)
        Returns: total equipment, active rentals, pending approvals, monthly revenue
        
        GET /api/rentals/rentals/dashboard_summary/
        """
        from equipment.models import Equipment, Category
        from datetime import datetime
        from django.db.models import Count, Sum, Avg, Q, F
        
        # Get current month boundaries
        now = timezone.now()
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (first_day_of_month - timezone.timedelta(days=1)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        
        # OPTIMIZED: Single aggregated query for ALL rental stats
        rental_stats = Rental.objects.aggregate(
            # Total counts
            total_rentals=Count('id'),
            completed_rentals=Count('id', filter=Q(status='completed')),
            pending_approvals=Count('id', filter=Q(status='pending')),
            
            # Active rentals (multiple statuses in one query)
            active_rentals=Count(
                'id',
                filter=Q(status__in=[
                    'confirmed', 'preparing', 'ready_for_pickup',
                    'out_for_delivery', 'delivered', 'in_progress'
                ])
            ),
        )
        
        # OPTIMIZED: Single query for sales stats (current + last month)
        sales_stats = RentalSale.objects.aggregate(
            # This month
            monthly_revenue=Sum(
                'total_revenue',
                filter=Q(sale_date__gte=first_day_of_month)
            ),
            monthly_commission=Sum(
                'platform_commission_amount',
                filter=Q(sale_date__gte=first_day_of_month)
            ),
            monthly_sales=Count(
                'id',
                filter=Q(sale_date__gte=first_day_of_month)
            ),
            
            # Last month
            last_month_revenue=Sum(
                'total_revenue',
                filter=Q(
                    sale_date__gte=last_month_start,
                    sale_date__lt=first_day_of_month
                )
            ),
            last_month_sales=Count(
                'id',
                filter=Q(
                    sale_date__gte=last_month_start,
                    sale_date__lt=first_day_of_month
                )
            ),
            
            # Pending payouts
            pending_payout_count=Count('id', filter=Q(payout_status='pending')),
            pending_payout_total=Sum('seller_payout', filter=Q(payout_status='pending')),
        )
        
        # Extract values with defaults
        monthly_revenue = float(sales_stats['monthly_revenue'] or 0)
        monthly_commission = float(sales_stats['monthly_commission'] or 0)
        monthly_sales_count = sales_stats['monthly_sales'] or 0
        last_month_revenue = float(sales_stats['last_month_revenue'] or 0)
        last_month_sales_count = sales_stats['last_month_sales'] or 0
        
        # Calculate growth percentages
        revenue_growth = (
            ((monthly_revenue - last_month_revenue) / last_month_revenue * 100)
            if last_month_revenue > 0 else 0
        )
        sales_growth = (
            ((monthly_sales_count - last_month_sales_count) / last_month_sales_count * 100)
            if last_month_sales_count > 0 else 0
        )
        
        # Equipment count and category breakdown (2 queries)
        total_equipment = Equipment.objects.exclude(status='inactive').count()
        
        equipment_by_category = Equipment.objects.exclude(
            status='inactive'
        ).values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Top performing equipment (optimized with values())
        top_equipment = Rental.objects.filter(
            status='completed'
        ).values(
            'equipment__name',
            'equipment__id'
        ).annotate(
            rental_count=Count('id'),
            total_revenue=Sum('total_amount')
        ).order_by('-rental_count')[:5]
        
        # Recent activity (optimized with select_related and values)
        recent_rentals = Rental.objects.select_related(
            'equipment',
            'customer__user',
            'seller'
        ).order_by('-created_at')[:5].values(
            'id',
            'rental_reference',
            'equipment__name',
            'customer__user__username',
            'status',
            'total_amount',
            'created_at'
        )
        
        # Calculate completion rate
        total_rentals = rental_stats['total_rentals'] or 0
        completed_rentals = rental_stats['completed_rentals'] or 0
        completion_rate = (
            round((completed_rentals / total_rentals * 100), 2)
            if total_rentals > 0 else 0
        )
        
        return Response({
            'summary': {
                'total_equipment': total_equipment,
                'active_rentals': rental_stats['active_rentals'] or 0,
                'pending_approvals': rental_stats['pending_approvals'] or 0,
                'monthly_revenue': monthly_revenue,
            },
            'monthly_stats': {
                'revenue': monthly_revenue,
                'commission': monthly_commission,
                'sales_count': monthly_sales_count,
                'revenue_growth_percentage': round(revenue_growth, 2),
                'sales_growth_percentage': round(sales_growth, 2),
            },
            'comparison': {
                'this_month': {
                    'revenue': monthly_revenue,
                    'sales': monthly_sales_count,
                },
                'last_month': {
                    'revenue': last_month_revenue,
                    'sales': last_month_sales_count,
                }
            },
            'platform_stats': {
                'total_rentals': total_rentals,
                'completed_rentals': completed_rentals,
                'completion_rate': completion_rate,
            },
            'equipment_by_category': list(equipment_by_category),
            'top_equipment': list(top_equipment),
            'recent_activity': list(recent_rentals),
            'pending_payouts': {
                'count': sales_stats['pending_payout_count'] or 0,
                'total_amount': float(sales_stats['pending_payout_total'] or 0),
            }
        })


class RentalReviewViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for rental reviews
    """
    queryset = RentalReview.objects.all()
    serializer_class = RentalReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def equipment_reviews(self, request):
        """Get reviews for specific equipment"""
        equipment_id = request.query_params.get('equipment_id')
        if not equipment_id:
            return Response(
                {'error': 'equipment_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reviews = self.queryset.filter(rental__equipment_id=equipment_id)
        serializer = self.get_serializer(reviews, many=True)
        
        # Calculate average ratings
        if reviews.exists():
            avg_ratings = {
                'overall': sum(r.overall_rating for r in reviews) / reviews.count(),
                'equipment': sum(r.equipment_rating for r in reviews) / reviews.count(),
                'service': sum(r.service_rating for r in reviews) / reviews.count(),
                'delivery': sum(r.delivery_rating for r in reviews) / reviews.count(),
            }
        else:
            avg_ratings = {'overall': 0, 'equipment': 0, 'service': 0, 'delivery': 0}
        
        return Response({
            'count': reviews.count(),
            'average_ratings': avg_ratings,
            'reviews': serializer.data
        })
