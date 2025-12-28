from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from .models import (
    Rental, RentalStatusUpdate, RentalImage, RentalReview, 
    RentalPayment, RentalDocument, RentalSale
)
from equipment.serializers import EquipmentListSerializer
from accounts.models import CustomerProfile, CompanyProfile, DeliveryAddress


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
    receipt_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = RentalPayment
        fields = ('id', 'rental', 'payment_type', 'payment_type_display', 
                  'amount', 'payment_method', 'payment_method_display', 
                  'payment_status', 'payment_status_display', 'transaction_id', 
                  'receipt_file', 'receipt_file_url', 'receipt_number', 'notes',
                  'created_at', 'completed_at')
    
    def get_receipt_file_url(self, obj):
        """Get full URL for receipt file"""
        if obj.receipt_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.receipt_file.url)
            return obj.receipt_file.url
        return None


class RentalDocumentSerializer(serializers.ModelSerializer):
    """Serializer for rental documents"""
    file_url = serializers.SerializerMethodField()
    uploaded_by_name = serializers.ReadOnlyField(source='uploaded_by.get_full_name')
    document_type_display = serializers.ReadOnlyField(source='get_document_type_display')
    is_locked = serializers.SerializerMethodField()
    
    class Meta:
        model = RentalDocument
        fields = ('id', 'document_type', 'document_type_display', 'title', 
                  'file_url', 'uploaded_by_name', 'visible_to_customer', 'requires_payment',
                  'is_locked', 'is_signed', 'signed_at', 'signature_data', 'created_at')
        read_only_fields = ('uploaded_by',)
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_is_locked(self, obj):
        """Check if document is locked (requires payment and payment not completed)"""
        if not obj.requires_payment:
            return False
        
        # Check if rental has completed payment
        rental = obj.rental
        completed_payment = rental.payments.filter(
            payment_status='completed'
        ).exists()
        
        return not completed_payment


class RentalListSerializer(serializers.ModelSerializer):
    """Simplified rental serializer for list views in React Native"""
    equipment = EquipmentListSerializer(read_only=True)  # Full equipment object with all images
    equipment_name = serializers.ReadOnlyField(source='equipment.name')
    equipment_id = serializers.ReadOnlyField(source='equipment.id')
    equipment_image = serializers.SerializerMethodField()
    equipment_images = serializers.SerializerMethodField()  # All images for gallery
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
            'id', 'rental_reference', 'equipment', 'equipment_id', 'equipment_name', 
            'equipment_image', 'equipment_images', 'customer_name', 'seller_name', 
            'start_date', 'end_date', 'total_amount', 'status', 'status_display', 
            'created_at', 'is_overdue', 'days_remaining', 'rental_duration_text',
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
    
    def get_equipment_images(self, obj):
        """Get all equipment images for gallery"""
        request = self.context.get('request')
        images = obj.equipment.images.all()[:7]  # Max 7 images
        
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
    
    def get_mobile_display_data(self, obj):
        """Optimized data for React Native cards"""
        return {
            'id': obj.id,
            'reference': obj.rental_reference,
            'equipment': obj.equipment.name,
            'equipment_id': obj.equipment.id,
            'image': self.get_equipment_image(obj),
            'images': self.get_equipment_images(obj),  # Full image gallery
            'status': obj.status,
            'status_text': obj.get_status_display(),
            'start_date': obj.start_date.strftime('%Y-%m-%d'),
            'end_date': obj.end_date.strftime('%Y-%m-%d'),
            'duration': obj.rental_duration_text,
            'total_amount': str(obj.total_amount),
            'is_overdue': obj.is_overdue,
            'days_remaining': obj.days_remaining,
            'status_color': self._get_status_color(obj.status),
            'seller': obj.seller.company_name,
            'customer': obj.customer.user.get_full_name()
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
    
    # Currency and formatted prices
    currency = serializers.SerializerMethodField()
    currency_symbol = serializers.SerializerMethodField()
    formatted_prices = serializers.SerializerMethodField()
    
    # Mobile actions
    available_actions = serializers.SerializerMethodField()
    
    class Meta:
        model = Rental
        fields = (
            'id', 'rental_reference', 'equipment', 'customer_details', 'seller_details',
            'start_date', 'end_date', 'actual_start_date', 'actual_end_date',
            'quantity', 'daily_rate', 'total_days', 'subtotal', 'delivery_fee',
            'insurance_fee', 'security_deposit', 'late_fees', 'damage_fees', 
            'total_amount', 'currency', 'currency_symbol', 'formatted_prices',
            'status', 'status_display', 'delivery_address',
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
    
    def get_currency(self, obj):
        """Get currency code based on country"""
        country_currency = {
            'UAE': 'AED',
            'UZB': 'UZS',
        }
        return country_currency.get(obj.delivery_country, 'USD')
    
    def get_currency_symbol(self, obj):
        """Get currency symbol"""
        country_symbol = {
            'UAE': 'AED',
            'UZB': 'UZS',
        }
        return country_symbol.get(obj.delivery_country, '$')
    
    def get_formatted_prices(self, obj):
        """Get all prices formatted with currency"""
        currency = self.get_currency(obj)
        symbol = self.get_currency_symbol(obj)
        
        return {
            'daily_rate': f"{symbol} {obj.daily_rate:,.2f}",
            'subtotal': f"{symbol} {obj.subtotal:,.2f}",
            'delivery_fee': f"{symbol} {obj.delivery_fee:,.2f}",
            'insurance_fee': f"{symbol} {obj.insurance_fee:,.2f}",
            'security_deposit': f"{symbol} {obj.security_deposit:,.2f}",
            'late_fees': f"{symbol} {obj.late_fees:,.2f}",
            'damage_fees': f"{symbol} {obj.damage_fees:,.2f}",
            'total_amount': f"{symbol} {obj.total_amount:,.2f}",
            'currency_code': currency
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
    """Serializer for creating rental requests"""
    delivery_address_id = serializers.IntegerField(write_only=True, required=False)
    id = serializers.IntegerField(read_only=True)
    rental_reference = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Rental
        fields = (
            'id', 'rental_reference', 'status', 'total_amount',  # Read-only response fields
            'equipment', 'start_date', 'end_date', 'quantity', 
            'delivery_address', 'delivery_city', 'delivery_country',
            'delivery_instructions', 'pickup_required', 'customer_phone',
            'customer_email', 'customer_notes', 'delivery_address_id'
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
        
        requested_quantity = data.get('quantity', 1)
        
        # Check total available units
        if requested_quantity > equipment.available_units:
            raise serializers.ValidationError(
                f"Only {equipment.available_units} units available in total"
            )
        
        # Check if enough units available for selected dates (considering existing bookings)
        if not equipment.is_available_on_dates(
            data['start_date'], 
            data['end_date'],
            requested_quantity
        ):
            raise serializers.ValidationError(
                "Not enough units available for the selected dates. Some units are already booked."
            )
        
        return data
    
    def create(self, validated_data):
        """Create rental request"""
        user = self.context['request'].user
        
        # Handle delivery address selection
        delivery_address_id = validated_data.pop('delivery_address_id', None)
        if delivery_address_id:
            try:
                address = DeliveryAddress.objects.get(id=delivery_address_id, user=user)
                # Populate delivery fields from selected address
                validated_data['delivery_address'] = f"{address.street_landmark}, {address.building}, {address.apartment_room}"
                validated_data['delivery_city'] = address.city
                validated_data['delivery_street'] = address.street_landmark
                validated_data['delivery_building'] = address.building
                validated_data['delivery_apartment_room'] = address.apartment_room
                validated_data['delivery_contact_number'] = address.contact_number
                validated_data['delivery_latitude'] = address.latitude
                validated_data['delivery_longitude'] = address.longitude
                
                # If phone number not provided in request, use address contact
                if not validated_data.get('customer_phone'):
                    validated_data['customer_phone'] = address.contact_number
                    
            except DeliveryAddress.DoesNotExist:
                raise serializers.ValidationError({"delivery_address_id": "Invalid delivery address selected."})

        # Ensure user has customer profile
        if not hasattr(user, 'customer_profile'):
            raise serializers.ValidationError("Only customers can create rental requests")
        
        # Set customer and seller
        equipment = validated_data['equipment']
        validated_data['customer'] = user.customer_profile
        validated_data['seller'] = equipment.seller_company
        validated_data['daily_rate'] = equipment.daily_rate
        
        # Auto-calculate total_days (ALWAYS calculated, never manual)
        start_date = validated_data['start_date']
        end_date = validated_data['end_date']
        validated_data['total_days'] = (end_date - start_date).days + 1  # +1 to include both days
        
        # Calculate pricing
        quantity = validated_data['quantity']
        total_days = validated_data['total_days']
        daily_rate = validated_data['daily_rate']
        subtotal = daily_rate * total_days * quantity
        
        # Auto-calculate fees (can be customized)
        delivery_fee = Decimal('50.00') if validated_data.get('pickup_required', True) else Decimal('0.00')
        insurance_fee = daily_rate * Decimal('0.1') * total_days  # 10% of daily rate per day
        security_deposit = daily_rate * 2  # 2 days deposit
        
        validated_data['subtotal'] = subtotal
        validated_data['delivery_fee'] = delivery_fee
        validated_data['insurance_fee'] = insurance_fee
        validated_data['security_deposit'] = security_deposit
        validated_data['total_amount'] = subtotal + delivery_fee + insurance_fee
        
        # Auto-approve if quantity is less than 5
        if quantity < 5:
            validated_data['status'] = 'approved'
            validated_data['approved_at'] = timezone.now()
        
        rental = Rental.objects.create(**validated_data)
        
        # Create initial status update
        if quantity < 5:
            status_note = 'Rental request auto-approved (quantity < 5)'
        else:
            status_note = 'Rental request created by customer and pending seller approval'
        
        RentalStatusUpdate.objects.create(
            rental=rental,
            new_status=rental.status,
            updated_by=user,
            notes=status_note,
            is_visible_to_customer=True
        )
        
        # Auto-generate rental agreement document
        self._create_rental_agreement(rental, user)
        
        # Attach operating manual if equipment has one (locked until payment)
        self._attach_operating_manual(rental, equipment, user)
        
        return rental
    
    def _create_rental_agreement(self, rental, user):
        """Auto-generate rental agreement document"""
        import os
        from django.core.files.base import ContentFile
        
        # Generate rental agreement content
        agreement_text = f"""
EQUIPMENT RENTAL AGREEMENT

Rental Reference: {rental.rental_reference}
Date: {timezone.now().strftime('%B %d, %Y')}

PARTIES:
Seller: {rental.seller.company_name}
Customer: {rental.customer.user.get_full_name()}

EQUIPMENT:
Item: {rental.equipment.name}
Quantity: {rental.quantity} unit(s)

RENTAL PERIOD:
Start Date: {rental.start_date.strftime('%B %d, %Y')}
End Date: {rental.end_date.strftime('%B %d, %Y')}
Duration: {rental.total_days} day(s)

PAYMENT:
Daily Rate: ${rental.daily_rate}
Subtotal: ${rental.subtotal}
Delivery Fee: ${rental.delivery_fee}
Insurance Fee: ${rental.insurance_fee}
Security Deposit: ${rental.security_deposit}
Total Amount: ${rental.total_amount}

DELIVERY:
Address: {rental.delivery_address}
City: {rental.delivery_city}, {rental.delivery_country}
Instructions: {rental.delivery_instructions or 'None'}

TERMS & CONDITIONS:
1. The customer agrees to pay the total amount before equipment delivery.
2. The customer is responsible for the equipment during the rental period.
3. Any damage or loss will be charged to the customer.
4. Equipment must be returned in the same condition as received.
5. Late returns will incur additional daily charges.

This agreement is binding upon acceptance of the rental request.

Generated automatically by TezRent System
        """
        
        # Create document file
        file_content = ContentFile(agreement_text.encode('utf-8'))
        filename = f"rental_agreement_{rental.rental_reference}.txt"
        
        # Create RentalDocument
        document = RentalDocument.objects.create(
            rental=rental,
            document_type='rental_agreement',
            title=f'Rental Agreement - {rental.rental_reference}',
            uploaded_by=user,
            visible_to_customer=True,
            requires_payment=False  # Rental agreement visible immediately
        )
        document.file.save(filename, file_content)
        document.save()
    
    def _attach_operating_manual(self, rental, equipment, user):
        """Attach equipment operating manual if exists (locked until payment)"""
        if equipment.operating_manual:
            # Create document reference to equipment's operating manual
            RentalDocument.objects.create(
                rental=rental,
                document_type='operating_manual',
                title=f'Operating Manual - {equipment.name}',
                file=equipment.operating_manual,  # Reference to equipment's manual
                uploaded_by=user,
                visible_to_customer=True,
                requires_payment=True  # Locked until payment completed
            )


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


class RentalSaleSerializer(serializers.ModelSerializer):
    """
    Serializer for RentalSale model - financial records.
    Used for sales analytics, revenue tracking, and payout management.
    """
    rental_reference = serializers.CharField(source='rental.rental_reference', read_only=True)
    seller_name = serializers.CharField(source='seller.company_name', read_only=True)
    customer_name = serializers.CharField(source='customer.user.get_full_name', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    equipment_category = serializers.CharField(source='equipment.category.name', read_only=True)
    
    # Formatted amounts
    formatted_revenue = serializers.SerializerMethodField()
    formatted_commission = serializers.SerializerMethodField()
    formatted_payout = serializers.SerializerMethodField()
    
    # Status display
    payout_status_display = serializers.CharField(source='get_payout_status_display', read_only=True)
    
    class Meta:
        model = RentalSale
        fields = (
            'id',
            'rental',
            'rental_reference',
            
            # Parties
            'seller',
            'seller_name',
            'customer',
            'customer_name',
            'equipment',
            'equipment_name',
            'equipment_category',
            
            # Financial details
            'total_revenue',
            'subtotal',
            'delivery_fee',
            'insurance_fee',
            'late_fees',
            'damage_fees',
            
            # Commission
            'platform_commission_percentage',
            'platform_commission_amount',
            'seller_payout',
            
            # Formatted amounts
            'formatted_revenue',
            'formatted_commission',
            'formatted_payout',
            
            # Rental details
            'rental_days',
            'rental_start_date',
            'rental_end_date',
            'equipment_quantity',
            
            # Payout tracking
            'payout_status',
            'payout_status_display',
            'payout_date',
            'payout_reference',
            'payout_notes',
            
            # Timestamps
            'sale_date',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'sale_date', 'created_at', 'updated_at',
            'platform_commission_amount', 'seller_payout'
        )
    
    def get_formatted_revenue(self, obj):
        """Format total revenue with currency"""
        currency = self.get_currency_symbol(obj.rental)
        return f"{currency}{obj.total_revenue:,.2f}"
    
    def get_formatted_commission(self, obj):
        """Format commission with currency"""
        currency = self.get_currency_symbol(obj.rental)
        return f"{currency}{obj.platform_commission_amount:,.2f}"
    
    def get_formatted_payout(self, obj):
        """Format seller payout with currency"""
        currency = self.get_currency_symbol(obj.rental)
        return f"{currency}{obj.seller_payout:,.2f}"
    
    def get_currency_symbol(self, rental):
        """Get currency symbol based on delivery country"""
        country_currencies = {
            'UAE': 'AED ',
            'UZB': 'UZS ',
        }
        return country_currencies.get(rental.delivery_country, '$')


class SalesAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for sales analytics dashboard.
    Returns aggregated financial data for reporting.
    """
    # Overview metrics
    total_sales = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_commission = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_seller_payout = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Averages
    average_sale_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_rental_days = serializers.FloatField()
    
    # Period comparisons
    this_month_sales = serializers.IntegerField()
    this_month_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    last_month_sales = serializers.IntegerField()
    last_month_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Growth
    revenue_growth_percentage = serializers.FloatField()
    sales_growth_percentage = serializers.FloatField()
    
    # Top performers
    top_equipment = serializers.ListField(child=serializers.DictField())
    top_sellers = serializers.ListField(child=serializers.DictField())
    
    # Payout status
    pending_payouts_count = serializers.IntegerField()
    pending_payouts_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
