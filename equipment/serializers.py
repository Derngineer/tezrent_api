from rest_framework import serializers
from .models import Category, Equipment, EquipmentImage, EquipmentSpecification, Tag, Banner

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')

class CategorySerializer(serializers.ModelSerializer):
    """Full category serializer for React Native with images and metadata"""
    equipment_count = serializers.SerializerMethodField()
    icon_url = serializers.SerializerMethodField()
    promotional_image_url = serializers.SerializerMethodField()
    
    # Mobile-specific fields
    mobile_display_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'description', 'slug', 'is_featured', 'display_order', 
            'color_code', 'equipment_count', 'icon_url', 'promotional_image_url',
            'mobile_display_data'
        )
    
    def get_equipment_count(self, obj):
        """Return count of available equipment in this category"""
        return obj.equipment.filter(status='available').count()
    
    def get_icon_url(self, obj):
        """Get full URL for category icon"""
        if obj.icon:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        return None
    
    def get_promotional_image_url(self, obj):
        """Get full URL for promotional image"""
        if obj.promotional_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.promotional_image.url)
            return obj.promotional_image.url
        return None
    
    def get_mobile_display_data(self, obj):
        """Optimized data structure for React Native components"""
        return {
            'id': obj.id,
            'name': obj.name,
            'slug': obj.slug,
            'icon': self.get_icon_url(obj),
            'promotional_image': self.get_promotional_image_url(obj),
            'equipment_count': self.get_equipment_count(obj),
            'color': obj.color_code or '#6B7280',  # Default gray if no color
            'is_featured': obj.is_featured,
            'navigation_params': {
                'screen': 'CategoryEquipment',
                'params': {
                    'categoryId': obj.id,
                    'categoryName': obj.name,
                    'categorySlug': obj.slug
                }
            }
        }

class CategoryChoicesSerializer(serializers.ModelSerializer):
    """Simplified serializer for category choices in dropdowns"""
    icon_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'icon_url', 'color_code')
    
    def get_icon_url(self, obj):
        """Get icon URL for dropdown display"""
        if obj.icon:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        return None

class CategoryFeaturedSerializer(serializers.ModelSerializer):
    """Serializer for featured categories on homepage"""
    icon_url = serializers.SerializerMethodField()
    promotional_image_url = serializers.SerializerMethodField()
    equipment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'description', 'slug', 'icon_url', 'promotional_image_url',
            'equipment_count', 'color_code'
        )
    
    def get_icon_url(self, obj):
        if obj.icon:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        return None
    
    def get_promotional_image_url(self, obj):
        if obj.promotional_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.promotional_image.url)
            return obj.promotional_image.url
        return None
    
    def get_equipment_count(self, obj):
        return obj.equipment.filter(status='available').count()

class EquipmentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentImage
        fields = ('id', 'image', 'is_primary', 'display_order', 'caption')
        
    def validate_display_order(self, value):
        """Ensure display_order is between 1 and 7"""
        if not 1 <= value <= 7:
            raise serializers.ValidationError("Display order must be between 1 and 7")
        return value

class EquipmentSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentSpecification
        fields = ('id', 'name', 'value')

class EquipmentListSerializer(serializers.ModelSerializer):
    """Serializer for listing equipment - Optimized for React Native mobile apps"""
    category_name = serializers.ReadOnlyField(source='category.name')
    primary_image = serializers.SerializerMethodField()
    image_gallery = serializers.SerializerMethodField()  # For mobile image carousels
    city_name = serializers.ReadOnlyField()
    country_name = serializers.ReadOnlyField()
    tags = serializers.SerializerMethodField()
    company_name = serializers.ReadOnlyField(source='seller_company.company_name')
    company_phone = serializers.ReadOnlyField(source='seller_company.company_phone')
    
    # Promotional fields for mobile promotions
    discounted_daily_rate = serializers.ReadOnlyField()
    savings_amount = serializers.ReadOnlyField()
    is_deal_active = serializers.ReadOnlyField()
    is_actually_new = serializers.ReadOnlyField()
    days_since_listed = serializers.ReadOnlyField()
    
    # Mobile-specific fields
    mobile_display_title = serializers.SerializerMethodField()
    mobile_price_text = serializers.SerializerMethodField()
    quick_contact_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Equipment
        fields = (
            'id', 'name', 'mobile_display_title', 'category', 'category_name', 
            'daily_rate', 'discounted_daily_rate', 'mobile_price_text',
            'status', 'available_units', 'city', 'city_name', 'country', 'country_name', 
            'primary_image', 'image_gallery', 'featured', 'is_new_listing', 'is_todays_deal',
            'tags', 'company_name', 'company_phone', 'promotion_badge', 'savings_amount', 
            'is_deal_active', 'is_actually_new', 'days_since_listed', 'deal_discount_percentage',
            'quick_contact_data', 'manufacturer', 'year'
        )
    
    def get_primary_image(self, obj):
        """Return the URL of the primary image for main product card display"""
        primary_image = obj.images.filter(is_primary=True).first()
        if not primary_image:
            primary_image = obj.images.first()
        
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None
    
    def get_image_gallery(self, obj):
        """Return all images in order for mobile carousel"""
        request = self.context.get('request')
        images = obj.images.all()[:7]  # Max 7 images
        
        gallery = []
        for img in images:
            url = img.image.url
            if request:
                url = request.build_absolute_uri(url)
            
            gallery.append({
                'id': img.id,
                'url': url,
                'is_primary': img.is_primary,
                'display_order': img.display_order,
                'caption': img.caption
            })
        
        return gallery
        
    def get_tags(self, obj):
        """Return a list of tag names"""
        return [tag.name for tag in obj.tags.all()]
        
    def get_mobile_display_title(self, obj):
        """Truncated title for mobile cards"""
        return obj.name[:30] + '...' if len(obj.name) > 30 else obj.name
    
    def get_mobile_price_text(self, obj):
        """Formatted price text for mobile display"""
        if obj.is_deal_active and obj.deal_discount_percentage > 0:
            return f"${obj.discounted_daily_rate}/day (Save ${obj.savings_amount})"
        return f"${obj.daily_rate}/day"
    
    def get_quick_contact_data(self, obj):
        """Contact info for quick actions in mobile app"""
        return {
            'phone': obj.seller_company.company_phone,
            'company_name': obj.seller_company.company_name,
            'whatsapp_link': f"https://wa.me/{obj.seller_company.company_phone.replace('+', '').replace(' ', '')}",
            'call_link': f"tel:{obj.seller_company.company_phone}"
        }
    
    def get_tags(self, obj):
        """Return a list of tag names"""
        return [tag.name for tag in obj.tags.all()]
        
    def get_mobile_display_title(self, obj):
        """Truncated title for mobile cards"""
        return obj.name[:30] + '...' if len(obj.name) > 30 else obj.name
    
    def get_mobile_price_text(self, obj):
        """Formatted price text for mobile display"""
        if obj.is_deal_active and obj.deal_discount_percentage > 0:
            return f"${obj.discounted_daily_rate}/day (Save ${obj.savings_amount})"
        return f"${obj.daily_rate}/day"
    
    def get_quick_contact_data(self, obj):
        """Contact info for quick actions in mobile app"""
        return {
            'phone': obj.seller_company.company_phone,
            'company_name': obj.seller_company.company_name,
            'whatsapp_link': f"https://wa.me/{obj.seller_company.company_phone.replace('+', '').replace(' ', '')}",
            'call_link': f"tel:{obj.seller_company.company_phone}"
        }

class EquipmentDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed equipment view"""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    images = EquipmentImageSerializer(many=True, read_only=True)
    specifications = EquipmentSpecificationSerializer(many=True, read_only=True)
    city_name = serializers.ReadOnlyField()
    country_name = serializers.ReadOnlyField()
    tags = TagSerializer(many=True, read_only=True)
    
    # Company information
    company_name = serializers.ReadOnlyField(source='seller_company.company_name')
    company_contact = serializers.ReadOnlyField(source='seller_company.user.get_full_name')
    company_phone = serializers.ReadOnlyField(source='seller_company.company_phone')
    company_city = serializers.ReadOnlyField(source='seller_company.city_name')
    
    class Meta:
        model = Equipment
        fields = (
            'id', 'name', 'description', 'category', 'category_id', 'manufacturer', 
            'model_number', 'year', 'weight', 'dimensions', 'fuel_type', 
            'daily_rate', 'weekly_rate', 'monthly_rate', 'country', 'country_name',
            'city', 'city_name', 'status', 'total_units', 'available_units',
            'featured', 'created_at', 'updated_at', 'images', 'specifications', 'tags',
            'seller_company', 'company_name', 'company_contact', 'company_phone', 'company_city'
        )
        read_only_fields = ('seller_company',)

class EquipmentCreateSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for creating equipment with images and tags"""
    # Category handling - allow creating new category or selecting existing
    category_name = serializers.CharField(write_only=True, required=False)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    
    # Tags handling
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )
    
    # Image upload handling - Note: images are handled in the view
    # FormData sends multiple files with same key, handled in perform_create
    
    # Specifications handling
    specifications_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    
    # Read-only fields for response
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = EquipmentImageSerializer(many=True, read_only=True)
    specifications = EquipmentSpecificationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Equipment
        fields = (
            'id', 'name', 'description', 'manufacturer', 'model_number', 'year',
            'weight', 'dimensions', 'fuel_type', 'daily_rate', 'weekly_rate',
            'monthly_rate', 'country', 'city', 'status', 'total_units',
            'available_units', 'featured', 'category_name', 'category_id',
            'category', 'tag_names', 'tags', 'uploaded_images', 'images',
            'specifications_data', 'specifications', 'created_at', 'updated_at'
        )
        read_only_fields = ('seller',)
    
    def validate(self, data):
        """Ensure either category_id or category_name is provided"""
        if not data.get('category') and not data.get('category_name'):
            raise serializers.ValidationError(
                "Either category_id or category_name must be provided"
            )
        return data
    
    def create(self, validated_data):
        # Handle category creation/selection
        category_name = validated_data.pop('category_name', None)
        tag_names = validated_data.pop('tag_names', [])
        specifications_data = validated_data.pop('specifications_data', [])
        
        # Images are handled in the view's perform_create method
        # because FormData handling is easier there
        
        # Set seller_company to current user's company profile
        user = self.context['request'].user
        if not hasattr(user, 'company_profile'):
            raise serializers.ValidationError(
                "Only companies can list equipment. Please complete your company profile first."
            )
        validated_data['seller_company'] = user.company_profile
        
        # Handle category
        if category_name and not validated_data.get('category'):
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={'description': f'Category for {category_name}'}
            )
            validated_data['category'] = category
        
        # Create equipment
        equipment = super().create(validated_data)
        
        # Handle tags
        if tag_names:
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
                equipment.tags.add(tag)
        
        # Images will be handled in the view's perform_create method
        
        # Handle specifications
        for spec_data in specifications_data:
            if 'name' in spec_data and 'value' in spec_data:
                EquipmentSpecification.objects.create(
                    equipment=equipment,
                    name=spec_data['name'],
                    value=spec_data['value']
                )
        
        return equipment


class EquipmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating equipment (seller can only update their own)"""
    category_name = serializers.CharField(write_only=True, required=False)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        required=False
    )
    tag_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    
    # Specifications handling
    specifications_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    
    # Read-only fields for response
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = EquipmentImageSerializer(many=True, read_only=True)
    specifications = EquipmentSpecificationSerializer(many=True, read_only=True)
    seller_company_name = serializers.ReadOnlyField(source='seller_company.company_name')
    
    class Meta:
        model = Equipment
        fields = (
            'id', 'name', 'description', 'manufacturer', 'model_number', 'year',
            'weight', 'dimensions', 'fuel_type', 'daily_rate', 'weekly_rate',
            'monthly_rate', 'country', 'city', 'status', 'total_units',
            'available_units', 'featured', 'is_new_listing', 'is_todays_deal',
            'deal_discount_percentage', 'original_daily_rate', 'deal_expires_at',
            'promotion_badge', 'promotion_description',
            'category_name', 'category_id', 'category', 'tag_names', 'tags',
            'specifications_data', 'specifications', 'images',
            'seller_company_name', 'created_at', 'updated_at'
        )
        read_only_fields = ('seller_company', 'created_at', 'updated_at')
    
    def validate(self, data):
        """Ensure seller can only update their own equipment"""
        user = self.context['request'].user
        equipment = self.instance
        
        if equipment and equipment.seller_company != user.company_profile:
            raise serializers.ValidationError(
                "You can only update your own equipment listings."
            )
        
        return data
    
    def update(self, instance, validated_data):
        # Handle category creation/selection
        category_name = validated_data.pop('category_name', None)
        tag_names = validated_data.pop('tag_names', None)
        specifications_data = validated_data.pop('specifications_data', None)
        
        # Handle category
        if category_name and not validated_data.get('category'):
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={'description': f'Category for {category_name}'}
            )
            validated_data['category'] = category
        
        # Update equipment
        equipment = super().update(instance, validated_data)
        
        # Handle tags
        if tag_names is not None:
            equipment.tags.clear()
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
                equipment.tags.add(tag)
        
        # Handle specifications
        if specifications_data is not None:
            # Clear existing and add new ones
            equipment.specifications.all().delete()
            for spec_data in specifications_data:
                if 'name' in spec_data and 'value' in spec_data:
                    EquipmentSpecification.objects.create(
                        equipment=equipment,
                        name=spec_data['name'],
                        value=spec_data['value']
                    )
        
        return equipment


class BannerSerializer(serializers.ModelSerializer):
    """Serializer for homepage banners in React Native"""
    desktop_image_url = serializers.SerializerMethodField()
    mobile_image_url = serializers.SerializerMethodField()
    target_category_name = serializers.ReadOnlyField(source='target_category.name')
    target_equipment_name = serializers.ReadOnlyField(source='target_equipment.name')
    is_currently_active = serializers.ReadOnlyField()
    
    # Mobile-specific fields
    mobile_cta_data = serializers.SerializerMethodField()
    display_image_url = serializers.SerializerMethodField()  # Automatically chooses mobile/desktop
    
    class Meta:
        model = Banner
        fields = (
            'id', 'title', 'subtitle', 'description', 'banner_type', 'position',
            'desktop_image_url', 'mobile_image_url', 'display_image_url', 
            'cta_text', 'cta_link', 'mobile_cta_data',
            'target_category', 'target_category_name', 'target_equipment', 'target_equipment_name',
            'is_currently_active', 'display_order'
        )
    
    def get_desktop_image_url(self, obj):
        """Get full URL for desktop banner image"""
        if obj.desktop_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.desktop_image.url)
            return obj.desktop_image.url
        return None
    
    def get_mobile_image_url(self, obj):
        """Get full URL for mobile banner image"""
        if obj.mobile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.mobile_image.url)
            return obj.mobile_image.url
        # Fallback to desktop image if no mobile image
        return self.get_desktop_image_url(obj)
    
    def get_display_image_url(self, obj):
        """Return mobile image for React Native, fallback to desktop"""
        return self.get_mobile_image_url(obj)
    
    def get_mobile_cta_data(self, obj):
        """CTA data optimized for React Native navigation"""
        return {
            'text': obj.cta_text,
            'link': obj.cta_link,
            'action_type': self._determine_action_type(obj.cta_link),
            'navigation_params': self._parse_navigation_params(obj.cta_link)
        }
    
    def _determine_action_type(self, link):
        """Determine the type of action for React Native navigation"""
        if not link:
            return 'none'
        if link.startswith('/categories/'):
            return 'category'
        elif link.startswith('/equipment/'):
            return 'equipment_detail'
        elif link.startswith('/deals'):
            return 'deals_page'
        elif link.startswith('http'):
            return 'external_url'
        else:
            return 'internal_navigation'
    
    def _parse_navigation_params(self, link):
        """Parse navigation parameters for React Native"""
        if not link:
            return {}
        
        if link.startswith('/categories/'):
            category_slug = link.replace('/categories/', '').strip('/')
            return {'category': category_slug}
        elif link.startswith('/equipment/'):
            equipment_id = link.replace('/equipment/', '').strip('/')
            return {'equipment_id': equipment_id}
        
        return {'url': link}