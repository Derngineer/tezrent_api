from rest_framework import serializers
from .models import Category, Equipment, EquipmentImage, EquipmentSpecification, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class EquipmentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentImage
        fields = ('id', 'image', 'is_primary', 'caption')

class EquipmentSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentSpecification
        fields = ('id', 'name', 'value')

class EquipmentListSerializer(serializers.ModelSerializer):
    """Serializer for listing equipment (summary view)"""
    category_name = serializers.ReadOnlyField(source='category.name')
    primary_image = serializers.SerializerMethodField()
    city_name = serializers.ReadOnlyField()
    country_name = serializers.ReadOnlyField()
    tags = serializers.SerializerMethodField()
    
    class Meta:
        model = Equipment
        fields = (
            'id', 'name', 'category', 'category_name', 'daily_rate', 
            'status', 'available_units', 'city', 'city_name',
            'country', 'country_name', 'primary_image', 'featured', 'tags'
        )
    
    def get_primary_image(self, obj):
        """Return the URL of the primary image or the first image if no primary is set"""
        primary_image = obj.images.filter(is_primary=True).first()
        if not primary_image:
            primary_image = obj.images.first()
        
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None
        
    def get_tags(self, obj):
        """Return a list of tag names"""
        return [tag.name for tag in obj.tags.all()]

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
    
    class Meta:
        model = Equipment
        fields = (
            'id', 'name', 'description', 'category', 'category_id', 'manufacturer', 
            'model_number', 'year', 'weight', 'dimensions', 'fuel_type', 
            'daily_rate', 'weekly_rate', 'monthly_rate', 'country', 'country_name',
            'city', 'city_name', 'status', 'total_units', 'available_units',
            'featured', 'created_at', 'updated_at', 'images', 'specifications', 'tags'
        )