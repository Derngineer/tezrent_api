from django.contrib import admin
from .models import (
    Rental, RentalStatusUpdate, RentalImage, 
    RentalReview, RentalPayment, RentalDocument
)


class RentalStatusUpdateInline(admin.TabularInline):
    model = RentalStatusUpdate
    extra = 0
    readonly_fields = ['created_at', 'updated_by']
    can_delete = False


class RentalImageInline(admin.TabularInline):
    model = RentalImage
    extra = 1
    fields = ['image', 'image_type', 'description', 'uploaded_by']


class RentalPaymentInline(admin.TabularInline):
    model = RentalPayment
    extra = 0
    readonly_fields = ['created_at', 'transaction_id']
    can_delete = False


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = [
        'rental_reference', 'equipment', 'customer', 
        'seller', 'status', 'start_date', 'end_date', 
        'total_amount', 'created_at'
    ]
    list_filter = [
        'status', 'created_at', 'start_date', 
        'end_date', 'pickup_required'
    ]
    search_fields = [
        'rental_reference', 'equipment__name', 
        'customer__user__email', 'seller__company_name'
    ]
    readonly_fields = [
        'rental_reference', 'created_at', 'updated_at',
        'approved_at', 'cancelled_at', 'total_days', 
        'subtotal', 'total_amount'
    ]
    
    fieldsets = (
        ('Rental Information', {
            'fields': (
                'rental_reference', 'equipment', 'customer', 
                'seller', 'status'
            )
        }),
        ('Rental Dates', {
            'fields': (
                'start_date', 'end_date', 'actual_start_date', 
                'actual_end_date', 'total_days', 'quantity'
            )
        }),
        ('Delivery Information', {
            'fields': (
                'pickup_required', 'delivery_address', 'delivery_city',
                'delivery_country', 'delivery_instructions'
            )
        }),
        ('Contact Information', {
            'fields': ('customer_phone', 'customer_email')
        }),
        ('Financial Details', {
            'fields': (
                'daily_rate', 'subtotal', 'security_deposit',
                'delivery_fee', 'insurance_fee', 'late_fees',
                'damage_fees', 'total_amount'
            )
        }),
        ('Additional Information', {
            'fields': ('customer_notes', 'seller_notes')
        }),
        ('Status Timestamps', {
            'fields': (
                'created_at', 'updated_at', 'approved_at',
                'cancelled_at', 'cancellation_reason'
            ),
            'classes': ('collapse',)
        })
    )
    
    inlines = [RentalStatusUpdateInline, RentalImageInline, RentalPaymentInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'equipment', 'customer__user', 'seller'
        )


@admin.register(RentalStatusUpdate)
class RentalStatusUpdateAdmin(admin.ModelAdmin):
    list_display = [
        'rental', 'old_status', 'new_status', 'updated_by', 'created_at'
    ]
    list_filter = ['new_status', 'created_at', 'is_visible_to_customer']
    search_fields = ['rental__rental_reference', 'notes']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'rental', 'updated_by'
        )


@admin.register(RentalImage)
class RentalImageAdmin(admin.ModelAdmin):
    list_display = [
        'rental', 'image_type', 'uploaded_by', 'created_at'
    ]
    list_filter = ['image_type', 'created_at']
    search_fields = ['rental__rental_reference', 'description']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'rental', 'uploaded_by'
        )


@admin.register(RentalReview)
class RentalReviewAdmin(admin.ModelAdmin):
    list_display = [
        'rental', 'customer', 'overall_rating', 
        'would_recommend', 'created_at'
    ]
    list_filter = [
        'overall_rating', 'would_recommend', 'created_at'
    ]
    search_fields = [
        'rental__rental_reference', 'customer__user__email', 'review_text'
    ]
    readonly_fields = ['created_at', 'overall_rating']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('rental', 'customer')
        }),
        ('Ratings', {
            'fields': (
                'equipment_rating', 'service_rating', 
                'delivery_rating', 'overall_rating'
            )
        }),
        ('Review Content', {
            'fields': ('review_text', 'would_recommend')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'rental', 'customer__user'
        )


@admin.register(RentalPayment)
class RentalPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'rental', 'payment_type', 
        'amount', 'payment_status', 'created_at'
    ]
    list_filter = ['payment_type', 'payment_status', 'payment_method', 'created_at']
    search_fields = [
        'transaction_id', 'rental__rental_reference', 
        'gateway_reference'
    ]
    readonly_fields = ['created_at', 'completed_at', 'transaction_id']
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'rental', 'transaction_id', 'payment_type',
                'amount', 'payment_status'
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_method', 'gateway_reference',
                'gateway_response'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('rental')


@admin.register(RentalDocument)
class RentalDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'rental', 'document_type', 'title', 'uploaded_by', 
        'is_signed', 'created_at'
    ]
    list_filter = ['document_type', 'is_signed', 'created_at']
    search_fields = ['rental__rental_reference', 'title']
    readonly_fields = ['created_at', 'signed_at']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('rental', 'document_type', 'title', 'file')
        }),
        ('Signature', {
            'fields': ('is_signed', 'signed_at')
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'rental', 'uploaded_by'
        )
