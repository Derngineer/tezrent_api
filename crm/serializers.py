from rest_framework import serializers
from .models import (
    Lead, CustomerInteraction, SalesOpportunity,
    SupportTicket, TicketComment, CustomerNote, CustomerSegment
)
from accounts.models import User, CustomerProfile, CompanyProfile
from equipment.models import Equipment
from rentals.models import Rental


class LeadSerializer(serializers.ModelSerializer):
    """Full lead serializer for staff"""
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True, allow_null=True)
    customer_email = serializers.CharField(source='customer.user.email', read_only=True, allow_null=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'last_contacted_at', 'converted_at']


class LeadCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating leads"""
    
    class Meta:
        model = Lead
        fields = [
            'title', 'contact_name', 'contact_email', 'contact_phone',
            'company_name', 'source', 'status', 'company', 'customer',
            'assigned_to', 'notes', 'estimated_value', 'expected_close_date',
            'metadata'
        ]


class SalesOpportunitySerializer(serializers.ModelSerializer):
    """Full opportunity serializer"""
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True, allow_null=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True, allow_null=True)
    weighted_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    lead_title = serializers.CharField(source='lead.title', read_only=True, allow_null=True)
    
    class Meta:
        model = SalesOpportunity
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'weighted_value']


class SalesOpportunityCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating opportunities"""
    
    class Meta:
        model = SalesOpportunity
        fields = [
            'title', 'description', 'lead', 'contact_name',
            'contact_email', 'contact_phone', 'company', 'customer',
            'equipment', 'assigned_to', 'stage', 'probability',
            'estimated_amount', 'expected_close_date', 'notes'
        ]


class CustomerInteractionSerializer(serializers.ModelSerializer):
    """Interaction/activity log serializer"""
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    related_to_lead_title = serializers.CharField(source='related_to_lead.title', read_only=True, allow_null=True)
    related_to_opportunity_title = serializers.CharField(source='related_to_opportunity.title', read_only=True, allow_null=True)
    
    class Meta:
        model = CustomerInteraction
        fields = '__all__'
        read_only_fields = ['created_at']


class TicketCommentSerializer(serializers.ModelSerializer):
    """Ticket comment serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = TicketComment
        fields = '__all__'
        read_only_fields = ['created_at']


class SupportTicketSerializer(serializers.ModelSerializer):
    """Full support ticket serializer"""
    customer_email = serializers.CharField(source='customer.user.email', read_only=True)
    customer_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.company_name', read_only=True, allow_null=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)
    rental_reference = serializers.CharField(source='related_rental.rental_reference', read_only=True, allow_null=True)
    equipment_name = serializers.CharField(source='related_equipment.name', read_only=True, allow_null=True)
    comments = TicketCommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportTicket
        fields = '__all__'
        read_only_fields = [
            'ticket_number', 'created_at', 'updated_at',
            'resolved_at', 'closed_at'
        ]
    
    def get_customer_name(self, obj):
        user = obj.customer.user
        return f"{user.first_name} {user.last_name}".strip() or user.email
    
    def get_comment_count(self, obj):
        return obj.comments.count()


class SupportTicketCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating tickets"""
    
    class Meta:
        model = SupportTicket
        fields = [
            'title', 'description', 'category', 'priority',
            'customer', 'company', 'related_rental',
            'related_equipment', 'internal_notes'
        ]


class SupportTicketCustomerSerializer(serializers.ModelSerializer):
    """Customer-facing ticket serializer (hides internal notes)"""
    company_name = serializers.CharField(source='company.company_name', read_only=True, allow_null=True)
    rental_reference = serializers.CharField(source='related_rental.rental_reference', read_only=True, allow_null=True)
    equipment_name = serializers.CharField(source='related_equipment.name', read_only=True, allow_null=True)
    public_comments = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_number', 'title', 'description', 'category',
            'priority', 'status', 'company_name', 'rental_reference',
            'equipment_name', 'resolution', 'created_at', 'updated_at',
            'resolved_at', 'public_comments'
        ]
        read_only_fields = [
            'ticket_number', 'created_at', 'updated_at',
            'resolved_at'
        ]
    
    def get_public_comments(self, obj):
        # Only return non-internal comments for customers
        public_comments = obj.comments.filter(is_internal=False)
        return TicketCommentSerializer(public_comments, many=True).data


class CustomerNoteSerializer(serializers.ModelSerializer):
    """Customer note serializer"""
    customer_email = serializers.CharField(source='customer.user.email', read_only=True)
    customer_name = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True, allow_null=True)
    
    class Meta:
        model = CustomerNote
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_customer_name(self, obj):
        user = obj.customer.user
        return f"{user.first_name} {user.last_name}".strip() or user.email


class CustomerSegmentSerializer(serializers.ModelSerializer):
    """Customer segment serializer"""
    customer_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CustomerSegment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# Mobile-optimized serializers for React Native

class LeadMobileSerializer(serializers.ModelSerializer):
    """Lightweight lead serializer for mobile"""
    
    class Meta:
        model = Lead
        fields = [
            'id', 'title', 'contact_name', 'contact_email',
            'contact_phone', 'source', 'status', 'estimated_value',
            'expected_close_date', 'created_at'
        ]


class TicketMobileSerializer(serializers.ModelSerializer):
    """Lightweight ticket serializer for mobile"""
    unread_comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_number', 'title', 'category',
            'priority', 'status', 'created_at', 'updated_at',
            'unread_comment_count'
        ]
    
    def get_unread_comment_count(self, obj):
        # This would require a read_receipts model or similar
        # For now, return 0
        return 0
