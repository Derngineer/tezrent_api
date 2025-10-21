"""
Serializers for favorites app
"""
from rest_framework import serializers
from .models import Favorite, FavoriteCollection, RecentlyViewed
from equipment.serializers import EquipmentListSerializer
from equipment.models import Equipment


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for user's favorites"""
    equipment = EquipmentListSerializer(read_only=True)
    equipment_id = serializers.PrimaryKeyRelatedField(
        queryset=Equipment.objects.all(),
        source='equipment',
        write_only=True
    )
    
    # Read-only computed fields
    is_available = serializers.ReadOnlyField()
    current_price = serializers.ReadOnlyField()
    
    # Customer info
    customer_email = serializers.ReadOnlyField(source='customer.user.email')
    
    # Mobile-optimized data
    mobile_display_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Favorite
        fields = (
            'id', 'customer', 'customer_email', 'equipment', 'equipment_id',
            'notes', 'preferred_rental_start', 'preferred_rental_duration',
            'notify_on_availability', 'notify_on_price_drop', 'notify_on_deals',
            'is_available', 'current_price', 'created_at', 'updated_at',
            'mobile_display_data'
        )
        read_only_fields = ('customer', 'created_at', 'updated_at')
    
    def get_mobile_display_data(self, obj):
        """Optimized data for React Native favorites screen"""
        return {
            'favorite_id': obj.id,
            'equipment_id': obj.equipment.id,
            'equipment_name': obj.equipment.name,
            'equipment_image': obj.equipment.images.filter(is_primary=True).first().image.url if obj.equipment.images.filter(is_primary=True).exists() else None,
            'daily_rate': str(obj.current_price),
            'is_available': obj.is_available,
            'is_deal': obj.equipment.is_deal_active,
            'discount_percentage': obj.equipment.deal_discount_percentage if obj.equipment.is_deal_active else 0,
            'company_name': obj.equipment.seller_company.company_name,
            'location': f"{obj.equipment.city_name}, {obj.equipment.country_name}",
            'has_notes': bool(obj.notes),
            'notify_settings': {
                'availability': obj.notify_on_availability,
                'price_drop': obj.notify_on_price_drop,
                'deals': obj.notify_on_deals
            },
            'navigation_params': {
                'screen': 'EquipmentDetail',
                'params': {'equipmentId': obj.equipment.id}
            }
        }


class FavoriteCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating favorites"""
    
    class Meta:
        model = Favorite
        fields = (
            'equipment', 'notes', 'notify_on_availability',
            'notify_on_price_drop', 'notify_on_deals'
        )
    
    def create(self, validated_data):
        # Customer will be set in the view from request.user
        return super().create(validated_data)


class FavoriteCollectionSerializer(serializers.ModelSerializer):
    """Serializer for favorite collections/wishlists"""
    equipment = EquipmentListSerializer(many=True, read_only=True)
    equipment_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Equipment.objects.all(),
        source='equipment',
        write_only=True,
        required=False
    )
    
    # Computed fields
    item_count = serializers.ReadOnlyField()
    total_estimated_cost = serializers.ReadOnlyField()
    
    # Mobile display
    mobile_display_data = serializers.SerializerMethodField()
    
    class Meta:
        model = FavoriteCollection
        fields = (
            'id', 'customer', 'name', 'description', 'is_public',
            'icon', 'color', 'equipment', 'equipment_ids',
            'item_count', 'total_estimated_cost',
            'created_at', 'updated_at', 'mobile_display_data'
        )
        read_only_fields = ('customer', 'created_at', 'updated_at')
    
    def get_mobile_display_data(self, obj):
        """Optimized data for React Native collections"""
        return {
            'collection_id': obj.id,
            'name': obj.name,
            'icon': obj.icon or 'bookmark',
            'color': obj.color or '#6B7280',
            'item_count': obj.item_count,
            'estimated_daily_cost': str(obj.total_estimated_cost),
            'is_public': obj.is_public,
            'preview_images': [
                eq.images.filter(is_primary=True).first().image.url
                for eq in obj.equipment.all()[:3]
                if eq.images.filter(is_primary=True).exists()
            ],
            'navigation_params': {
                'screen': 'CollectionDetail',
                'params': {'collectionId': obj.id}
            }
        }


class RecentlyViewedSerializer(serializers.ModelSerializer):
    """Serializer for recently viewed equipment"""
    equipment = EquipmentListSerializer(read_only=True)
    
    class Meta:
        model = RecentlyViewed
        fields = (
            'id', 'equipment', 'view_count', 
            'first_viewed_at', 'last_viewed_at', 'viewed_from'
        )
        read_only_fields = ('view_count', 'first_viewed_at', 'last_viewed_at')
