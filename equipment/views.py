from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend  # Fixed import
from django.db.models import Q
from .models import Category, Equipment, EquipmentImage, EquipmentSpecification, Tag, Banner
from .serializers import (
    CategorySerializer, CategoryChoicesSerializer, CategoryFeaturedSerializer,
    EquipmentListSerializer, EquipmentDetailSerializer, EquipmentCreateSerializer,
    EquipmentUpdateSerializer, EquipmentImageSerializer, EquipmentSpecificationSerializer,
    BannerSerializer, TagSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoint for equipment categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['display_order', 'name', 'equipment_count']
    ordering = ['display_order', 'name']
    
    @action(detail=False, methods=['get'])
    def choices(self, request):
        """Get simplified category list for dropdown choices"""
        categories = Category.objects.all().order_by('display_order', 'name')
        serializer = CategoryChoicesSerializer(categories, many=True, context={'request': request})
        return Response({
            'categories': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured categories for React Native homepage"""
        featured_categories = Category.objects.filter(
            is_featured=True
        ).order_by('display_order')
        
        serializer = CategoryFeaturedSerializer(featured_categories, many=True, context={'request': request})
        return Response({
            'count': featured_categories.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def mobile_categories(self, request):
        """Get all categories optimized for React Native with icons and counts"""
        categories = Category.objects.all().order_by('display_order', 'name')
        
        # Add equipment count annotation for efficiency
        from django.db.models import Count
        categories = categories.annotate(
            available_equipment_count=Count('equipment', filter=Q(equipment__status='available'))
        )
        
        serializer = self.get_serializer(categories, many=True)
        return Response({
            'count': categories.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def equipment(self, request, pk=None):
        """Get equipment for a specific category (React Native category page)"""
        category = self.get_object()
        
        # Get equipment in this category
        equipment_queryset = Equipment.objects.filter(
            category=category,
            status='available'
        ).order_by('-featured', '-created_at')
        
        # Apply filters
        featured_only = request.query_params.get('featured') == 'true'
        if featured_only:
            equipment_queryset = equipment_queryset.filter(featured=True)
        
        deals_only = request.query_params.get('deals') == 'true'
        if deals_only:
            equipment_queryset = equipment_queryset.filter(is_todays_deal=True)
        
        # Pagination for mobile
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = equipment_queryset.count()
        results = equipment_queryset[start:end]
        
        # Use EquipmentListSerializer for consistency
        from .serializers import EquipmentListSerializer
        equipment_serializer = EquipmentListSerializer(results, many=True, context={'request': request})
        
        return Response({
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'icon_url': category.icon_url,
                'promotional_image_url': category.promotional_image_url,
                'color_code': category.color_code
            },
            'equipment': {
                'count': total_count,
                'has_next': end < total_count,
                'has_previous': page > 1,
                'current_page': page,
                'results': equipment_serializer.data
            }
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upload_icon(self, request, pk=None):
        """Upload icon for a category (small icon for navigation/cards)"""
        category = self.get_object()
        
        # Check if icon file is present
        icon_file = request.FILES.get('icon')
        if not icon_file:
            return Response(
                {'error': 'No icon file provided. Please send the file with key "icon"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete old icon if exists
        if category.icon:
            category.icon.delete(save=False)
        
        # Save new icon
        category.icon = icon_file
        category.save()
        
        # Return updated category
        serializer = self.get_serializer(category)
        return Response({
            'message': 'Icon uploaded successfully',
            'category': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upload_promotional_image(self, request, pk=None):
        """Upload promotional/banner image for a category (larger image for featured sections)"""
        category = self.get_object()
        
        # Check if image file is present
        image_file = request.FILES.get('promotional_image')
        if not image_file:
            return Response(
                {'error': 'No promotional image file provided. Please send the file with key "promotional_image"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete old promotional image if exists
        if category.promotional_image:
            category.promotional_image.delete(save=False)
        
        # Save new promotional image
        category.promotional_image = image_file
        category.save()
        
        # Return updated category
        serializer = self.get_serializer(category)
        return Response({
            'message': 'Promotional image uploaded successfully',
            'category': serializer.data
        }, status=status.HTTP_200_OK)
    

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
        elif self.action == 'create':
            return EquipmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EquipmentUpdateSerializer
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
        """Handle equipment creation with image uploads"""
        # Verify user has company profile
        if not hasattr(self.request.user, 'company_profile'):
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError(
                {"error": "Only companies can list equipment. Please complete your company profile first."}
            )
        
        # Parse JSON fields from FormData (tag_names, specifications_data)
        # When sent via FormData, JSON arrays come as strings and need to be parsed
        import json
        if 'tag_names' in self.request.data and isinstance(self.request.data.get('tag_names'), str):
            try:
                self.request.data._mutable = True  # Make QueryDict mutable
                self.request.data['tag_names'] = json.loads(self.request.data['tag_names'])
            except (json.JSONDecodeError, AttributeError):
                pass
        
        if 'specifications_data' in self.request.data and isinstance(self.request.data.get('specifications_data'), str):
            try:
                if not hasattr(self.request.data, '_mutable'):
                    self.request.data._mutable = True
                self.request.data['specifications_data'] = json.loads(self.request.data['specifications_data'])
            except (json.JSONDecodeError, AttributeError):
                pass
        
        # Save the equipment with seller_company automatically set
        equipment = serializer.save(seller_company=self.request.user.company_profile)
        
        # Handle image uploads from FormData
        # When using FormData, multiple files with same name come as a list
        uploaded_images = self.request.FILES.getlist('images')  # or 'uploaded_images'
        
        # Limit to 7 images
        if len(uploaded_images) > 7:
            # Delete the created equipment and raise error
            equipment.delete()
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError({"images": "Maximum 7 images allowed per equipment"})
        
        # Create EquipmentImage objects
        for i, image_file in enumerate(uploaded_images):
            EquipmentImage.objects.create(
                equipment=equipment,
                image=image_file,
                display_order=i + 1,
                is_primary=(i == 0),  # First image is primary
                caption=f"Image {i+1} for {equipment.name}"
            )
    
    def perform_update(self, serializer):
        """Handle equipment updates - seller can only update their own equipment"""
        # Verify seller owns the equipment
        equipment = self.get_object()
        if equipment.seller_company != self.request.user.company_profile:
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError(
                {"error": "You can only update your own equipment listings."}
            )
        
        # Parse JSON fields from FormData (tag_names, specifications_data)
        import json
        if 'tag_names' in self.request.data and isinstance(self.request.data.get('tag_names'), str):
            try:
                self.request.data._mutable = True
                self.request.data['tag_names'] = json.loads(self.request.data['tag_names'])
            except (json.JSONDecodeError, AttributeError):
                pass
        
        if 'specifications_data' in self.request.data and isinstance(self.request.data.get('specifications_data'), str):
            try:
                if not hasattr(self.request.data, '_mutable'):
                    self.request.data._mutable = True
                self.request.data['specifications_data'] = json.loads(self.request.data['specifications_data'])
            except (json.JSONDecodeError, AttributeError):
                pass
        
        # Handle image updates if provided
        uploaded_images = self.request.FILES.getlist('images')
        
        # Save the updated equipment
        instance = serializer.save()
        
        # If new images are uploaded, handle them
        if uploaded_images:
            # Optionally delete old images or keep them
            # For now, we'll add new images alongside existing ones
            existing_count = instance.images.count()
            total_count = existing_count + len(uploaded_images)
            
            if total_count > 7:
                from rest_framework import serializers as drf_serializers
                raise drf_serializers.ValidationError(
                    {"images": f"Maximum 7 images allowed. You have {existing_count} existing images."}
                )
            
            # Add new images
            for i, image_file in enumerate(uploaded_images):
                EquipmentImage.objects.create(
                    equipment=instance,
                    image=image_file,
                    display_order=existing_count + i + 1,
                    is_primary=False,  # Don't override existing primary
                    caption=f"Additional image for {instance.name}"
                )
    
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
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def check_availability(self, request, pk=None):
        """
        Real-time availability check for equipment booking
        Call this BEFORE customer fills out booking form
        
        Query params:
        - start_date: YYYY-MM-DD (required)
        - end_date: YYYY-MM-DD (required)
        - quantity: int (required, default=1)
        
        Returns:
        - available: boolean
        - available_units: int (how many units free)
        - total_units: int (total capacity)
        - booked_units: int (currently booked)
        - message: string (user-friendly message)
        - price_estimate: object (pricing breakdown)
        """
        equipment = self.get_object()
        
        # Get query parameters
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        quantity_str = request.query_params.get('quantity', '1')
        
        # Validate required parameters
        if not start_date_str or not end_date_str:
            return Response({
                'error': 'Both start_date and end_date are required',
                'example': '/api/equipment/equipment/1/check_availability/?start_date=2025-10-28&end_date=2025-10-30&quantity=2'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse dates
        from datetime import datetime
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            quantity = int(quantity_str)
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD. Quantity must be an integer.',
                'example': 'start_date=2025-10-28&end_date=2025-10-30&quantity=2'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate dates
        from django.utils import timezone
        if start_date < timezone.now().date():
            return Response({
                'error': 'Start date cannot be in the past',
                'available': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date <= start_date:
            return Response({
                'error': 'End date must be after start date',
                'available': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if quantity < 1:
            return Response({
                'error': 'Quantity must be at least 1',
                'available': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check equipment status
        if equipment.status != 'available':
            return Response({
                'available': False,
                'available_units': 0,
                'total_units': equipment.available_units,
                'booked_units': 0,
                'message': f'This equipment is currently {equipment.get_status_display().lower()}',
                'can_proceed': False
            })
        
        # Get booked quantity for date range
        from rentals.models import Rental
        from django.db.models import Sum
        
        booked_quantity = Rental.objects.filter(
            equipment=equipment,
            status__in=['confirmed', 'preparing', 'ready_for_pickup', 
                       'out_for_delivery', 'delivered', 'in_progress'],
            start_date__lte=end_date,
            end_date__gte=start_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Calculate availability
        total_units = equipment.available_units
        available_units = total_units - booked_quantity
        is_available = available_units >= quantity
        
        # Calculate pricing
        total_days = (end_date - start_date).days + 1
        daily_rate = float(equipment.daily_rate)
        subtotal = daily_rate * total_days * quantity
        delivery_fee = 50.00  # Default
        insurance_fee = daily_rate * 0.1 * total_days
        total_amount = subtotal + delivery_fee + insurance_fee
        
        # Build response message
        if is_available:
            if available_units == total_units:
                message = f"✅ Great news! All {total_units} units are available for your dates."
            else:
                message = f"✅ Available! {available_units} of {total_units} units free for your dates."
        else:
            if available_units > 0:
                message = f"⚠️ Only {available_units} unit(s) available. You requested {quantity}."
            else:
                message = f"❌ Sorry, all units are booked for these dates."
        
        return Response({
            'available': is_available,
            'can_proceed': is_available,
            'available_units': available_units,
            'total_units': total_units,
            'booked_units': booked_quantity,
            'requested_quantity': quantity,
            'message': message,
            'dates': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'total_days': total_days
            },
            'price_estimate': {
                'daily_rate': f'{daily_rate:.2f}',
                'quantity': quantity,
                'total_days': total_days,
                'subtotal': f'{subtotal:.2f}',
                'delivery_fee': f'{delivery_fee:.2f}',
                'insurance_fee': f'{insurance_fee:.2f}',
                'total_amount': f'{total_amount:.2f}',
                'currency': 'AED'
            },
            'next_step': 'Proceed to fill out booking details' if is_available else 'Try different dates or reduce quantity'
        })
    
    @action(detail=False, methods=['get'])
    def new_listings(self, request):
        """Get newly listed equipment (for React homepage)"""
        new_equipment = self.get_queryset().filter(
            is_new_listing=True,
            is_actually_new=True
        ).order_by('-created_at')[:12]  # Limit to 12 for grid display
        
        serializer = self.get_serializer(new_equipment, many=True)
        return Response({
            'count': new_equipment.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def featured_brands(self, request):
        """Get featured equipment (for React homepage)"""
        featured_equipment = self.get_queryset().filter(
            featured=True,
            status='available'
        ).order_by('-created_at')[:12]
        
        serializer = self.get_serializer(featured_equipment, many=True)
        return Response({
            'count': featured_equipment.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def todays_deals(self, request):
        """Get today's deals (for React homepage)"""
        from django.utils import timezone
        
        deals = self.get_queryset().filter(
            is_todays_deal=True,
            status='available'
        ).filter(
            Q(deal_expires_at__isnull=True) | 
            Q(deal_expires_at__gte=timezone.now())
        ).order_by('-deal_discount_percentage', '-created_at')[:12]
        
        serializer = self.get_serializer(deals, many=True)
        return Response({
            'count': deals.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def mobile_home_data(self, request):
        """Get all homepage data in one API call for React Native"""
        from django.utils import timezone
        
        # Get data efficiently
        new_listings = self.get_queryset().filter(
            is_new_listing=True,
            is_actually_new=True
        ).order_by('-created_at')[:8]
        
        featured = self.get_queryset().filter(
            featured=True,
            status='available'
        ).order_by('-created_at')[:8]
        
        deals = self.get_queryset().filter(
            is_todays_deal=True,
            status='available'
        ).filter(
            Q(deal_expires_at__isnull=True) | 
            Q(deal_expires_at__gte=timezone.now())
        ).order_by('-deal_discount_percentage')[:8]
        
        # Serialize data
        serializer = self.get_serializer
        
        return Response({
            'new_listings': serializer(new_listings, many=True).data,
            'featured_brands': serializer(featured, many=True).data,
            'todays_deals': serializer(deals, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def mobile_search(self, request):
        """Optimized search for React Native with filters"""
        queryset = self.get_queryset()
        
        # Search query
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(manufacturer__icontains=search) |
                Q(category__name__icontains=search)
            )
        
        # Quick filters for mobile
        if request.query_params.get('featured') == 'true':
            queryset = queryset.filter(featured=True)
        if request.query_params.get('deals') == 'true':
            queryset = queryset.filter(is_todays_deal=True)
        if request.query_params.get('new') == 'true':
            queryset = queryset.filter(is_actually_new=True)
        
        # Pagination for mobile
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = queryset.count()
        results = queryset[start:end]
        
        serializer = self.get_serializer(results, many=True)
        
        return Response({
            'count': total_count,
            'has_next': end < total_count,
            'has_previous': page > 1,
            'current_page': page,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def seller_dashboard(self, request):
        """Dashboard data for React Native seller app"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not hasattr(request.user, 'company_profile'):
            return Response({'error': 'Company profile required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get seller's equipment
        seller_equipment = self.get_queryset().filter(
            seller_company=request.user.company_profile
        )
        
        # Dashboard stats
        stats = {
            'total_listings': seller_equipment.count(),
            'active_listings': seller_equipment.filter(status='available').count(),
            'featured_listings': seller_equipment.filter(featured=True).count(),
            'deal_listings': seller_equipment.filter(is_todays_deal=True).count(),
            'rented_listings': seller_equipment.filter(status='rented').count(),
        }
        
        # Recent listings
        recent_listings = seller_equipment.order_by('-created_at')[:5]
        serializer = self.get_serializer(recent_listings, many=True)
        
        return Response({
            'stats': stats,
            'recent_listings': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def my_equipment(self, request):
        """Get seller's equipment for React Native seller app"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not hasattr(request.user, 'company_profile'):
            return Response({'error': 'Company profile required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter seller's equipment
        queryset = self.get_queryset().filter(
            seller_company=request.user.company_profile
        )
        
        # Apply status filter if provided
        equipment_status = request.query_params.get('status')
        if equipment_status:
            queryset = queryset.filter(status=equipment_status)
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = queryset.count()
        results = queryset.order_by('-created_at')[start:end]
        
        serializer = self.get_serializer(results, many=True)
        
        return Response({
            'count': total_count,
            'has_next': end < total_count,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def tags(self, request):
        """Get all available tags"""
        tags = Tag.objects.all()
        return Response({'tags': [tag.name for tag in tags]})
    
    @action(detail=True, methods=['post'])
    def manage_images(self, request, pk=None):
        """Add or remove images for equipment (seller only)"""
        equipment = self.get_object()
        
        # Verify seller owns the equipment
        if equipment.seller_company != request.user.company_profile:
            return Response(
                {'error': 'You can only manage images for your own equipment'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        action_type = request.data.get('action')  # 'add' or 'delete'
        
        if action_type == 'delete':
            image_id = request.data.get('image_id')
            try:
                image = EquipmentImage.objects.get(id=image_id, equipment=equipment)
                image.delete()
                return Response({'message': 'Image deleted successfully'})
            except EquipmentImage.DoesNotExist:
                return Response(
                    {'error': 'Image not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        elif action_type == 'add':
            uploaded_images = request.FILES.getlist('images')
            existing_count = equipment.images.count()
            total_count = existing_count + len(uploaded_images)
            
            if total_count > 7:
                return Response(
                    {'error': f'Maximum 7 images allowed. You have {existing_count} existing images.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add new images
            created_images = []
            for i, image_file in enumerate(uploaded_images):
                img = EquipmentImage.objects.create(
                    equipment=equipment,
                    image=image_file,
                    display_order=existing_count + i + 1,
                    is_primary=False,
                    caption=request.data.get('caption', '')
                )
                created_images.append(img)
            
            serializer = EquipmentImageSerializer(created_images, many=True, context={'request': request})
            return Response({
                'message': f'{len(created_images)} image(s) added successfully',
                'images': serializer.data
            })
        
        elif action_type == 'set_primary':
            image_id = request.data.get('image_id')
            try:
                # Remove primary status from all images
                equipment.images.update(is_primary=False)
                # Set new primary
                image = EquipmentImage.objects.get(id=image_id, equipment=equipment)
                image.is_primary = True
                image.save()
                return Response({'message': 'Primary image updated successfully'})
            except EquipmentImage.DoesNotExist:
                return Response(
                    {'error': 'Image not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        else:
            return Response(
                {'error': 'Invalid action. Use "add", "delete", or "set_primary"'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def get_permissions(self):
        """Custom permissions - only authenticated companies can create/update/delete"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'manage_images']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

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

class BannerViewSet(viewsets.ModelViewSet):
    """API endpoint for homepage banners (React/Next.js)"""
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['display_order', 'created_at']
    ordering = ['position', 'display_order']
    
    def get_queryset(self):
        """Filter banners by position and active status"""
        from django.utils import timezone
        from django.db.models import Q
        
        # For authenticated users (admins), show all banners
        # For public/unauthenticated, only show currently active banners
        if self.request.user and self.request.user.is_authenticated:
            # Authenticated users see all banners (for management)
            queryset = Banner.objects.all()
        else:
            # Public users only see active banners within date range
            now = timezone.now()
            queryset = Banner.objects.filter(is_active=True)
            queryset = queryset.filter(
                Q(start_date__isnull=True) | Q(start_date__lte=now)
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=now)
            )
        
        # Apply optional filters
        position = self.request.query_params.get('position', None)
        banner_type = self.request.query_params.get('banner_type', None)
        
        if position:
            queryset = queryset.filter(position=position)
        if banner_type:
            queryset = queryset.filter(banner_type=banner_type)
            
        return queryset

class TagViewSet(viewsets.ModelViewSet):
    """API endpoint for tags - allows listing and management by authenticated users"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']

    def get_permissions(self):
        # Authenticated users can manage tags, anyone can read
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]
    
    def destroy(self, request, *args, **kwargs):
        """Delete a tag - with safety check for usage"""
        tag = self.get_object()
        
        # Check if tag is being used by any equipment
        equipment_count = tag.equipment.count()
        
        if equipment_count > 0:
            return Response(
                {
                    'error': f'Cannot delete tag "{tag.name}". It is currently used by {equipment_count} equipment listing(s).',
                    'equipment_count': equipment_count,
                    'tag_name': tag.name
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Tag is not in use, safe to delete
        tag_name = tag.name
        tag.delete()
        
        return Response(
            {
                'message': f'Tag "{tag_name}" deleted successfully.',
                'deleted_tag': tag_name
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def track_view(self, request, pk=None):
        """Track banner view for analytics"""
        banner = self.get_object()
        banner.increment_view_count()
        return Response({'status': 'view tracked'})
    
    @action(detail=True, methods=['post']) 
    def track_click(self, request, pk=None):
        """Track banner click for analytics"""
        banner = self.get_object()
        banner.increment_click_count()
        return Response({'status': 'click tracked'})
    
    @action(detail=False, methods=['get'])
    def active_banners(self, request):
        """Get all currently active banners grouped by position"""
        banners = self.get_queryset()
        
        grouped_banners = {
            'top': [],
            'middle': [],
            'bottom': [],
            'sidebar': []
        }
        
        for banner in banners:
            serializer = self.get_serializer(banner)
            grouped_banners[banner.position].append(serializer.data)
        
        return Response(grouped_banners)
