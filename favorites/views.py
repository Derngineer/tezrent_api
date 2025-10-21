"""
Views for favorites app
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Favorite, FavoriteCollection, RecentlyViewed
from .serializers import (
    FavoriteSerializer, FavoriteCreateSerializer,
    FavoriteCollectionSerializer, RecentlyViewedSerializer
)
from equipment.models import Equipment


class FavoriteViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user favorites/liked equipment
    
    Endpoints:
    - GET    /api/favorites/              - List user's favorites
    - POST   /api/favorites/              - Add to favorites
    - GET    /api/favorites/{id}/         - Get favorite detail
    - PUT    /api/favorites/{id}/         - Update favorite settings
    - DELETE /api/favorites/{id}/         - Remove from favorites
    - POST   /api/favorites/toggle/       - Toggle favorite status
    - GET    /api/favorites/check/{equipment_id}/ - Check if favorited
    """
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's favorites"""
        if not hasattr(self.request.user, 'customer_profile'):
            return Favorite.objects.none()
        return Favorite.objects.filter(
            customer=self.request.user.customer_profile
        ).select_related('equipment', 'equipment__seller_company', 'customer__user')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FavoriteCreateSerializer
        return FavoriteSerializer
    
    def perform_create(self, serializer):
        """Automatically set customer from authenticated user"""
        if not hasattr(self.request.user, 'customer_profile'):
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError(
                {"error": "Only customers can save favorites. Please complete your customer profile."}
            )
        serializer.save(customer=self.request.user.customer_profile)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """
        Toggle favorite status for equipment
        POST /api/favorites/toggle/
        Body: {"equipment_id": 123}
        
        Returns: {"favorited": true/false, "favorite_id": 123 or null}
        """
        equipment_id = request.data.get('equipment_id')
        
        if not equipment_id:
            return Response(
                {'error': 'equipment_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not hasattr(request.user, 'customer_profile'):
            return Response(
                {'error': 'Only customers can save favorites'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        equipment = get_object_or_404(Equipment, id=equipment_id)
        customer = request.user.customer_profile
        
        # Check if already favorited
        favorite = Favorite.objects.filter(
            customer=customer,
            equipment=equipment
        ).first()
        
        if favorite:
            # Remove from favorites
            favorite.delete()
            return Response({
                'favorited': False,
                'favorite_id': None,
                'message': 'Removed from favorites'
            })
        else:
            # Add to favorites
            favorite = Favorite.objects.create(
                customer=customer,
                equipment=equipment
            )
            return Response({
                'favorited': True,
                'favorite_id': favorite.id,
                'message': 'Added to favorites'
            }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def check(self, request):
        """
        Check if equipment is favorited
        GET /api/favorites/check/?equipment_id=123
        
        Returns: {"is_favorited": true/false, "favorite_id": 123 or null}
        """
        equipment_id = request.query_params.get('equipment_id')
        
        if not equipment_id:
            return Response(
                {'error': 'equipment_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not hasattr(request.user, 'customer_profile'):
            return Response({'is_favorited': False, 'favorite_id': None})
        
        favorite = Favorite.objects.filter(
            customer=request.user.customer_profile,
            equipment_id=equipment_id
        ).first()
        
        return Response({
            'is_favorited': favorite is not None,
            'favorite_id': favorite.id if favorite else None
        })
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get only favorites that are currently available
        GET /api/favorites/available/
        """
        favorites = self.get_queryset().filter(
            equipment__status='available',
            equipment__available_units__gt=0
        )
        
        serializer = self.get_serializer(favorites, many=True)
        return Response({
            'count': favorites.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def on_deal(self, request):
        """
        Get favorites that currently have deals
        GET /api/favorites/on_deal/
        """
        from django.utils import timezone
        from django.db.models import Q
        
        favorites = self.get_queryset().filter(
            equipment__is_todays_deal=True
        ).filter(
            Q(equipment__deal_expires_at__isnull=True) |
            Q(equipment__deal_expires_at__gte=timezone.now())
        )
        
        serializer = self.get_serializer(favorites, many=True)
        return Response({
            'count': favorites.count(),
            'results': serializer.data
        })


class FavoriteCollectionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for favorite collections/wishlists
    
    Allows users to organize their favorites into custom collections
    """
    serializer_class = FavoriteCollectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's collections"""
        if not hasattr(self.request.user, 'customer_profile'):
            return FavoriteCollection.objects.none()
        return FavoriteCollection.objects.filter(
            customer=self.request.user.customer_profile
        ).prefetch_related('equipment')
    
    def perform_create(self, serializer):
        """Automatically set customer from authenticated user"""
        if not hasattr(self.request.user, 'customer_profile'):
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError(
                {"error": "Only customers can create collections."}
            )
        serializer.save(customer=self.request.user.customer_profile)
    
    @action(detail=True, methods=['post'])
    def add_equipment(self, request, pk=None):
        """
        Add equipment to collection
        POST /api/collections/{id}/add_equipment/
        Body: {"equipment_id": 123}
        """
        collection = self.get_object()
        equipment_id = request.data.get('equipment_id')
        
        if not equipment_id:
            return Response(
                {'error': 'equipment_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        equipment = get_object_or_404(Equipment, id=equipment_id)
        collection.equipment.add(equipment)
        
        serializer = self.get_serializer(collection)
        return Response({
            'message': f'Added {equipment.name} to {collection.name}',
            'collection': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def remove_equipment(self, request, pk=None):
        """
        Remove equipment from collection
        POST /api/collections/{id}/remove_equipment/
        Body: {"equipment_id": 123}
        """
        collection = self.get_object()
        equipment_id = request.data.get('equipment_id')
        
        if not equipment_id:
            return Response(
                {'error': 'equipment_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        equipment = get_object_or_404(Equipment, id=equipment_id)
        collection.equipment.remove(equipment)
        
        serializer = self.get_serializer(collection)
        return Response({
            'message': f'Removed {equipment.name} from {collection.name}',
            'collection': serializer.data
        })


class RecentlyViewedViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for recently viewed equipment
    
    Read-only - tracking is done automatically
    """
    serializer_class = RecentlyViewedSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's recently viewed"""
        if not hasattr(self.request.user, 'customer_profile'):
            return RecentlyViewed.objects.none()
        return RecentlyViewed.objects.filter(
            customer=self.request.user.customer_profile
        ).select_related('equipment', 'equipment__seller_company')[:20]
    
    @action(detail=False, methods=['post'])
    def track(self, request):
        """
        Track equipment view
        POST /api/recently-viewed/track/
        Body: {"equipment_id": 123, "viewed_from": "search"}
        """
        if not hasattr(request.user, 'customer_profile'):
            return Response(
                {'message': 'Tracking skipped - not a customer'},
                status=status.HTTP_200_OK
            )
        
        equipment_id = request.data.get('equipment_id')
        viewed_from = request.data.get('viewed_from', '')
        
        if not equipment_id:
            return Response(
                {'error': 'equipment_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        equipment = get_object_or_404(Equipment, id=equipment_id)
        customer = request.user.customer_profile
        
        # Get or create recently viewed entry
        recently_viewed, created = RecentlyViewed.objects.get_or_create(
            customer=customer,
            equipment=equipment,
            defaults={'viewed_from': viewed_from}
        )
        
        if not created:
            # Update existing entry
            recently_viewed.increment_view()
        
        return Response({
            'message': 'View tracked',
            'view_count': recently_viewed.view_count
        })
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """
        Clear all recently viewed
        DELETE /api/recently-viewed/clear/
        """
        if hasattr(request.user, 'customer_profile'):
            count = RecentlyViewed.objects.filter(
                customer=request.user.customer_profile
            ).delete()[0]
            
            return Response({
                'message': f'Cleared {count} recently viewed items'
            })
        
        return Response({'message': 'No items to clear'})
