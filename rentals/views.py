from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Rental, RentalStatusUpdate, RentalImage, RentalReview,
    RentalPayment, RentalDocument
)
from .serializers import (
    RentalListSerializer, RentalDetailSerializer, RentalCreateSerializer,
    RentalUpdateStatusSerializer, RentalStatusUpdateSerializer,
    RentalImageSerializer, RentalImageUploadSerializer, RentalReviewSerializer,
    RentalPaymentSerializer, RentalDocumentSerializer
)


class RentalViewSet(viewsets.ModelViewSet):
    """
    API endpoint for rentals - supports both customer and seller apps
    """
    queryset = Rental.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'equipment', 'start_date', 'end_date']
    search_fields = ['rental_reference', 'equipment__name']
    ordering_fields = ['created_at', 'start_date', 'total_amount']
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
                status__in=['confirmed', 'preparing', 'ready_for_pickup', 
                           'out_for_delivery', 'delivered', 'in_progress']
            ).count(),
            'pending_rentals': rentals.filter(status='pending').count(),
            'completed_rentals': rentals.filter(status='completed').count(),
            'total_spent': sum(r.total_amount for r in rentals.filter(status='completed')),
        }
        
        # Active rentals
        active_rentals = rentals.filter(
            status__in=['delivered', 'in_progress', 'out_for_delivery']
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
                status__in=['confirmed', 'preparing', 'ready_for_pickup',
                           'out_for_delivery', 'delivered', 'in_progress']
            ).count(),
            'completed_rentals': rentals.filter(status='completed').count(),
            'total_revenue': sum(r.total_amount for r in rentals.filter(status='completed')),
            'pending_returns': rentals.filter(
                status__in=['return_requested', 'returning']
            ).count(),
        }
        
        # Pending approvals
        pending_rentals = rentals.filter(status='pending').order_by('-created_at')[:5]
        
        # Active rentals
        active_rentals = rentals.filter(
            status__in=['confirmed', 'preparing', 'out_for_delivery', 'delivered']
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
