from rest_framework import serializers
from django.utils import timezone
from .models import (
    Rental, RentalStatusUpdate, RentalImage, RentalReview, 
    RentalPayment, RentalDocument
)
from equipment.serializers import EquipmentListSerializer
from accounts.models import CustomerProfile, CompanyProfile


class RentalStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for rental status updates"""
    updated_by_name = serializers.ReadOnlyField(source='updated_by.get_full_name')
    
    class Meta:
        model = RentalStatusUpdate
        fields = ('id', 'old_status', 'new_status', 'updated_by_name', 'notes', 
                  'is_visible_to_customer', 'created_at')
        read_only_fields = ('updated_by',)


class RentalImageSerializer(serializers.ModelSerializer):
    """Serializer for rental images"""
    image_url = serializers.SerializerMethodField()
    uploaded_by_name = serializers.ReadOnlyField(source='uploaded_by.get_full_name')
    
    class Meta:
        model = RentalImage
        fields = ('id', 'image_url', 'image_type', 'description', 
                  'uploaded_by_name', 'created_at')
        read_only_fields = ('uploaded_by',)
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class RentalReviewSerializer(serializers.ModelSerializer):
    """Serializer for rental reviews"""
    customer_name = serializers.ReadOnlyField(source='customer.user.get_full_name')
    
    class Meta:
        model = RentalReview
        fields = ('id', 'rental', 'customer', 'customer_name', 'equipment_rating', 
                  'service_rating', 'delivery_rating', 'overall_rating', 'review_text', 
                  'would_recommend', 'created_at')
        read_only_fields = ('customer', 'overall_rating')


class RentalPaymentSerializer(serializers.ModelSerializer):
    """Serializer for rental payments"""
    payment_type_display = serializers.ReadOnlyField(source='get_payment_type_display')
    payment_status_display = serializers.ReadOnlyField(source='get_payment_status_display')
    payment_method_display = serializers.ReadOnlyField(source='get_payment_method_display')
    
    class Meta:
        model = RentalPayment
        fields = ('id', 'rental', 'payment_type', 'payment_type_display', 
                  'amount', 'payment_method', 'payment_method_display', 
                  'payment_status', 'payment_status_display', 'transaction_id', 
                  'created_at', 'completed_at')


class RentalDocumentSerializer(serializers.ModelSerializer):
    """Serializer for rental documents"""
    file_url = serializers.SerializerMethodField()
    uploaded_by_name = serializers.ReadOnlyField(source='uploaded_by.get_full_name')
    document_type_display = serializers.ReadOnlyField(source='get_document_type_display')
    
    class Meta:
        model = RentalDocument
        fields = ('id', 'document_type', 'document_type_display', 'title', 
                  'file_url', 'uploaded_by_name', 'is_signed', 'signed_at', 'created_at')
        read_only_fields = ('uploaded_by',)
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class RentalListSerializer(serializers.ModelSerializer):
    """Simplified rental serializer for list views in React Native"""
    equipment_name = serializers.ReadOnlyField(source='equipment.name')
    equipment_image = serializers.SerializerMethodField()
    customer_name = serializers.ReadOnlyField(source='customer.user.get_full_name')
    seller_name = serializers.ReadOnlyField(source='seller.company_name')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    
    # Mobile-optimized fields
    is_overdue = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    rental_duration_text = serializers.ReadOnlyField()
    mobile_display_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Rental
        fields = (
            'id', 'rental_reference', 'equipment_name', 'equipment_image',
            'customer_name', 'seller_name', 'start_date', 'end_date',
            'total_amount', 'status', 'status_display', 'created_at',
            'is_overdue', 'days_remaining', 'rental_duration_text',
            'mobile_display_data'
        )
    
    def get_equipment_image(self, obj):
        """Get primary equipment image"""
        primary_image = obj.equipment.images.filter(is_primary=True).first()
        if not primary_image:
            primary_image = obj.equipment.images.first()
        
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None
    
    def get_mobile_display_data(self, obj):
        """Optimized data for React Native cards"""
        return {
            'id': obj.id,
            'reference': obj.rental_reference,
            'equipment': obj.equipment.name,
            'image': self.get_equipment_image(obj),
            'status': obj.status,
            'status_text': obj.get_status_display(),
            'start_date': obj.start_date.strftime('%Y-%m-%d'),
            'end_date': obj.end_date.strftime('%Y-%m-%d'),
            'duration': obj.rental_duration_text,
            'total_amount': str(obj.total_amount),
            'is_overdue': obj.is_overdue,
            'days_remaining': obj.days_remaining,
            'status_color': self._get_status_color(obj.status)
        }
    
    def _get_status_color(self, status):
        """Return color code for status badges in React Native"""
        color_map = {
            'pending': '#FFA500',        # Orange
            'approved': '#4CAF50',       # Green
            'confirmed': '#2196F3',      # Blue
            'delivered': '#9C27B0',      # Purple
            'in_progress': '#00BCD4',    # Cyan
            'completed': '#4CAF50',      # Green
            'cancelled': '#F44336',      # Red
            'overdue': '#FF0000',        # Red
            'dispute': '#FF9800',        # Orange
        }
        return color_map.get(status, '#757575')  # Default gray


class RentalDetailSerializer(serializers.ModelSerializer):
    """Detailed rental serializer for single rental view"""
    equipment = EquipmentListSerializer(read_only=True)
    customer_details = serializers.SerializerMethodField()
    seller_details = serializers.SerializerMethodField()
    status_updates = RentalStatusUpdateSerializer(many=True, read_only=True)
    images = RentalImageSerializer(many=True, read_only=True)
    payments = RentalPaymentSerializer(many=True, read_only=True)
    documents = RentalDocumentSerializer(many=True, read_only=True)
    review = RentalReviewSerializer(read_only=True)
    
    # Computed fields
    is_overdue = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    rental_duration_text = serializers.ReadOnlyField()
    status_display = serializers.ReadOnlyField(source='get_status_display')
    
    # Mobile actions
    available_actions = serializers.SerializerMethodField()
    
    class Meta:
        model = Rental
        fields = (
            'id', 'rental_reference', 'equipment', 'customer_details', 'seller_details',
            'start_date', 'end_date', 'actual_start_date', 'actual_end_date',
            'quantity', 'daily_rate', 'total_days', 'subtotal', 'delivery_fee',
            'insurance_fee', 'security_deposit', 'late_fees', 'damage_fees', 
            'total_amount', 'status', 'status_display', 'delivery_address',
            'delivery_city', 'delivery_country', 'delivery_instructions',
            'pickup_required', 'customer_phone', 'customer_email', 'customer_notes',
            'seller_notes', 'created_at', 'updated_at', 'is_overdue', 'days_remaining',
            'rental_duration_text', 'status_updates', 'images', 'payments', 
            'documents', 'review', 'available_actions'
        )
    
    def get_customer_details(self, obj):
        """Customer profile information"""
        return {
            'id': obj.customer.id,
            'name': obj.customer.user.get_full_name(),
            'email': obj.customer.user.email,
            'phone': obj.customer_phone,
            'address': obj.delivery_address,
            'city': obj.delivery_city
        }
    
    def get_seller_details(self, obj):
        """Seller company information"""
        return {
            'id': obj.seller.id,
            'company_name': obj.seller.company_name,
            'phone': obj.seller.company_phone,
            'address': obj.seller.company_address,
            'contact_person': obj.seller.user.get_full_name()
        }
    
    def get_available_actions(self, obj):
        """Get actions available for current rental status"""
        user = self.context['request'].user
        actions = []
        
        # Customer actions
        if hasattr(user, 'customer_profile') and obj.customer == user.customer_profile:
            if obj.status == 'approved':
                actions.append({'action': 'pay', 'label': 'Make Payment'})
            elif obj.status == 'pending':
                actions.append({'action': 'cancel', 'label': 'Cancel Request'})
            elif obj.status in ['delivered', 'in_progress']:
                actions.append({'action': 'request_return', 'label': 'Request Return'})
            elif obj.status == 'completed' and not hasattr(obj, 'review'):
                actions.append({'action': 'review', 'label': 'Write Review'})
        
        # Seller actions
        elif hasattr(user, 'company_profile') and obj.seller == user.company_profile:
            if obj.status == 'pending':
                actions.extend([
                    {'action': 'approve', 'label': 'Approve Rental'},
                    {'action': 'reject', 'label': 'Reject Rental'}
                ])
            elif obj.status == 'confirmed':
                actions.append({'action': 'mark_preparing', 'label': 'Start Preparing'})
            elif obj.status == 'preparing':
                actions.append({'action': 'mark_ready', 'label': 'Mark Ready for Pickup'})
            elif obj.status == 'ready_for_pickup':
                actions.append({'action': 'mark_delivering', 'label': 'Start Delivery'})
            elif obj.status == 'out_for_delivery':
                actions.append({'action': 'mark_delivered', 'label': 'Confirm Delivery'})
            elif obj.status == 'return_requested':
                actions.append({'action': 'start_return', 'label': 'Start Return Process'})
            elif obj.status == 'returning':
                actions.append({'action': 'complete_rental', 'label': 'Complete Rental'})
        
        return actions


class RentalCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating rental requests (customer side)"""
    
    class Meta:
        model = Rental
        fields = (
            'equipment', 'start_date', 'end_date', 'quantity', 
            'delivery_address', 'delivery_city', 'delivery_country',
            'delivery_instructions', 'pickup_required', 'customer_phone',
            'customer_email', 'customer_notes'
        )
    
    def validate(self, data):
        """Validate rental request"""
        # Check dates
        if data['start_date'] < timezone.now().date():
            raise serializers.ValidationError("Start date cannot be in the past")
        
        if data['end_date'] <= data['start_date']:
            raise serializers.ValidationError("End date must be after start date")
        
        # Check equipment availability
        equipment = data['equipment']
        if equipment.status != 'available':
            raise serializers.ValidationError("Equipment is not available for rental")
        
        if data['quantity'] > equipment.available_units:
            raise serializers.ValidationError(
                f"Only {equipment.available_units} units available"
            )
        
        # Check if equipment is available for selected dates
        if not equipment.is_available_on_dates(data['start_date'], data['end_date']):
            raise serializers.ValidationError(
                "Equipment is not available for the selected dates"
            )
        
        return data
    
    def create(self, validated_data):
        """Create rental request"""
        user = self.context['request'].user
        
        # Ensure user has customer profile
        if not hasattr(user, 'customer_profile'):
            raise serializers.ValidationError("Only customers can create rental requests")
        
        # Set customer and calculate pricing
        validated_data['customer'] = user.customer_profile
        validated_data['daily_rate'] = validated_data['equipment'].daily_rate
        
        # Auto-calculate fees (can be customized)
        validated_data['delivery_fee'] = 50.00  # Default delivery fee
        validated_data['insurance_fee'] = validated_data['daily_rate'] * 0.1  # 10% insurance
        validated_data['security_deposit'] = validated_data['daily_rate'] * 2  # 2 days deposit
        
        rental = Rental.objects.create(**validated_data)
        
        # Create initial status update
        RentalStatusUpdate.objects.create(
            rental=rental,
            new_status='pending',
            updated_by=user,
            notes='Rental request created by customer',
            is_visible_to_customer=True
        )
        
        return rental


class RentalUpdateStatusSerializer(serializers.Serializer):
    """Serializer for updating rental status"""
    new_status = serializers.ChoiceField(choices=Rental.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
    is_visible_to_customer = serializers.BooleanField(default=True)
    
    def validate(self, data):
        """Validate status transition"""
        rental = self.context['rental']
        new_status = data['new_status']
        
        # Define valid status transitions
        valid_transitions = {
            'pending': ['approved', 'cancelled'],
            'approved': ['confirmed', 'cancelled'],
            'confirmed': ['preparing', 'cancelled'],
            'preparing': ['ready_for_pickup'],
            'ready_for_pickup': ['out_for_delivery', 'delivered'],
            'out_for_delivery': ['delivered'],
            'delivered': ['in_progress', 'return_requested'],
            'in_progress': ['return_requested', 'overdue'],
            'return_requested': ['returning'],
            'returning': ['completed'],
        }
        
        current_status = rental.status
        if new_status not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot transition from {current_status} to {new_status}"
            )
        
        return data


class RentalImageUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading rental images"""
    
    class Meta:
        model = RentalImage
        fields = ('rental', 'image', 'image_type', 'description')
        
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)
