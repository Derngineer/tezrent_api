from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend  # Fixed import
from django.db.models import Q
from .models import Category, Equipment, EquipmentImage, EquipmentSpecification, Tag
from .serializers import (
    CategorySerializer, EquipmentListSerializer, 
    EquipmentDetailSerializer, EquipmentImageSerializer, 
    EquipmentSpecificationSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoint for equipment categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class EquipmentViewSet(viewsets.ModelViewSet):
    """API endpoint for equipment listings"""
    queryset = Equipment.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'country', 'city', 'featured']
    search_fields = ['name', 'description', 'manufacturer']
    ordering_fields = ['name', 'daily_rate', 'created_at', 'year']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EquipmentListSerializer
        return EquipmentDetailSerializer
    
    def get_queryset(self):
        """Allow filtering by available dates and tags"""
        queryset = Equipment.objects.all()
        
        # Get query parameters
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        tags = self.request.query_params.get('tags', None)
        
        # Filter by tags if provided
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queryset = queryset.filter(tags__name__in=tag_list).distinct()
        
        # Filter by date availability
        if start_date and end_date:
            from rentals.models import Rental
            
            # Find equipment that's unavailable during the date range
            unavailable = Rental.objects.filter(
                status__in=['confirmed', 'out_for_delivery', 'delivered'],
                start_date__lte=end_date,
                end_date__gte=start_date
            ).values_list('equipment', flat=True)
            
            # Filter out equipment with no available units
            queryset = queryset.exclude(Q(id__in=unavailable) & Q(available_units__lte=1))
        
        return queryset
    
    def perform_create(self, serializer):
        """Handle tags when creating equipment"""
        instance = serializer.save()
        tags = self.request.data.get('tags', [])
        if tags:
            for tag_name in tags:
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag_obj)
    
    def perform_update(self, serializer):
        """Handle tags when updating equipment"""
        instance = serializer.save()
        tags = self.request.data.get('tags', [])
        if tags:
            # Clear existing tags and add new ones
            instance.tags.clear()
            for tag_name in tags:
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag_obj)
    
    @action(detail=True, methods=['get'])
    def check_availability(self, request, pk=None):
        """Check if equipment is available for specific dates"""
        equipment = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Both start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        is_available = equipment.is_available_on_dates(start_date, end_date)
        
        return Response({
            'equipment_id': equipment.id,
            'equipment_name': equipment.name,
            'available': is_available,
            'available_units': equipment.available_units
        })
    
    @action(detail=True, methods=['get'])
    def specifications(self, request, pk=None):
        """Get specifications for a specific equipment"""
        equipment = self.get_object()
        specs = equipment.specifications.all()
        serializer = EquipmentSpecificationSerializer(specs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def tags(self, request):
        """Get all available tags"""
        tags = Tag.objects.all()
        return Response({'tags': [tag.name for tag in tags]})

class EquipmentImageViewSet(viewsets.ModelViewSet):
    """API endpoint for equipment images"""
    queryset = EquipmentImage.objects.all()
    serializer_class = EquipmentImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        equipment_id = self.request.query_params.get('equipment_id')
        if equipment_id:
            return EquipmentImage.objects.filter(equipment_id=equipment_id)
        return EquipmentImage.objects.all()
