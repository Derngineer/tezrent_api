from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Rental(models.Model):
    """
    Main rental model connecting customers with equipment from sellers
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),           # Customer submitted, waiting for seller
        ('approved', 'Approved'),                  # Seller approved, waiting for payment
        ('payment_pending', 'Payment Pending'),    # Payment in progress
        ('confirmed', 'Confirmed'),                # Paid and confirmed
        ('preparing', 'Preparing Equipment'),      # Seller preparing equipment
        ('ready_for_pickup', 'Ready for Pickup'), # Equipment ready
        ('out_for_delivery', 'Out for Delivery'), # Being delivered
        ('delivered', 'Equipment Delivered'),      # Customer has equipment
        ('in_progress', 'Rental in Progress'),     # Active rental period
        ('return_requested', 'Return Requested'), # Customer wants to return
        ('returning', 'Equipment Returning'),      # Being picked up/returned
        ('completed', 'Completed'),                # Successfully completed
        ('cancelled', 'Cancelled'),                # Cancelled before delivery
        ('overdue', 'Overdue'),                   # Past return date
        ('dispute', 'Under Dispute'),             # Issues being resolved
    )
    
    # Core rental information
    customer = models.ForeignKey(
        'accounts.CustomerProfile',
        on_delete=models.CASCADE,
        related_name='rentals'
    )
    equipment = models.ForeignKey(
        'equipment.Equipment',
        on_delete=models.CASCADE,
        related_name='rentals'
    )
    seller = models.ForeignKey(
        'accounts.CompanyProfile',
        on_delete=models.CASCADE,
        related_name='rental_orders'
    )
    
    # Rental period
    start_date = models.DateField()
    end_date = models.DateField()
    actual_start_date = models.DateTimeField(null=True, blank=True)
    actual_end_date = models.DateTimeField(null=True, blank=True)
    
    # Quantities and pricing
    quantity = models.PositiveIntegerField(default=1)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_days = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional costs
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    insurance_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    damage_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rental_reference = models.CharField(max_length=20, unique=True, blank=True)
    
    # Delivery information
    delivery_address = models.TextField(blank=True)
    delivery_city = models.CharField(max_length=50, blank=True) # Changed max_length to accommodate full city names
    delivery_country = models.CharField(max_length=3, blank=True)
    delivery_instructions = models.TextField(blank=True)
    pickup_required = models.BooleanField(default=True)
    
    # Detailed delivery location (snapshot at time of booking)
    delivery_apartment_room = models.CharField(max_length=50, blank=True)
    delivery_building = models.CharField(max_length=100, blank=True)
    delivery_street = models.CharField(max_length=255, blank=True)
    delivery_contact_number = models.CharField(max_length=20, blank=True)
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Contact information
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField()
    
    # Notes and communication
    customer_notes = models.TextField(blank=True, help_text="Customer's special requests or notes")
    seller_notes = models.TextField(blank=True, help_text="Seller's internal notes")
    cancellation_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Rental {self.rental_reference} - {self.equipment.name}"
    
    def save(self, *args, **kwargs):
        """Auto-generate rental reference and calculate totals"""
        if not self.rental_reference:
            import uuid
            self.rental_reference = f"RNT{str(uuid.uuid4())[:8].upper()}"
        
        # Auto-set seller from equipment
        if not self.seller_id:
            self.seller = self.equipment.seller_company
        
        # Calculate totals
        self.total_days = (self.end_date - self.start_date).days + 1
        self.subtotal = self.daily_rate * self.total_days * self.quantity
        self.total_amount = self.subtotal + self.delivery_fee + self.insurance_fee + self.late_fees + self.damage_fees
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if rental is overdue"""
        if self.status in ['delivered', 'in_progress']:
            return timezone.now().date() > self.end_date
        return False
    
    @property
    def days_remaining(self):
        """Days remaining in rental period"""
        if self.status in ['delivered', 'in_progress']:
            remaining = (self.end_date - timezone.now().date()).days
            return max(0, remaining)
        return 0
    
    @property
    def rental_duration_text(self):
        """Human readable rental duration"""
        if self.total_days == 1:
            return "1 day"
        elif self.total_days <= 7:
            return f"{self.total_days} days"
        elif self.total_days <= 30:
            weeks = self.total_days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''}"
        else:
            months = self.total_days // 30
            return f"{months} month{'s' if months > 1 else ''}"


class RentalStatusUpdate(models.Model):
    """
    Track status changes and communication for rentals
    """
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='status_updates')
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    is_visible_to_customer = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.rental.rental_reference}: {self.old_status} → {self.new_status}"


class RentalImage(models.Model):
    """
    Images for rental documentation (delivery, damage, etc.)
    """
    IMAGE_TYPE_CHOICES = (
        ('delivery_confirmation', 'Delivery Confirmation'),
        ('equipment_condition_before', 'Equipment Condition Before'),
        ('equipment_condition_after', 'Equipment Condition After'),
        ('damage_report', 'Damage Report'),
        ('pickup_confirmation', 'Pickup Confirmation'),
        ('other', 'Other'),
    )
    
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rental_images/')
    image_type = models.CharField(max_length=30, choices=IMAGE_TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.rental.rental_reference} - {self.get_image_type_display()}"


class RentalReview(models.Model):
    """
    Customer reviews for completed rentals
    """
    rental = models.OneToOneField(Rental, on_delete=models.CASCADE, related_name='review')
    customer = models.ForeignKey('accounts.CustomerProfile', on_delete=models.CASCADE)
    equipment_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating for equipment condition (1-5 stars)"
    )
    service_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating for seller service (1-5 stars)"
    )
    delivery_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating for delivery/pickup service (1-5 stars)"
    )
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, editable=False)
    review_text = models.TextField(blank=True)
    would_recommend = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        """Calculate overall rating as average"""
        self.overall_rating = Decimal(
            (self.equipment_rating + self.service_rating + self.delivery_rating) / 3
        ).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Review for {self.rental.rental_reference} - {self.overall_rating}★"


class RentalPayment(models.Model):
    """
    Payment tracking for rentals
    """
    PAYMENT_TYPE_CHOICES = (
        ('rental_fee', 'Rental Fee'),
        ('security_deposit', 'Security Deposit'),
        ('delivery_fee', 'Delivery Fee'),
        ('late_fee', 'Late Fee'),
        ('damage_fee', 'Damage Fee'),
        ('insurance_fee', 'Insurance Fee'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('cash', 'Cash'),
        ('cash_on_delivery', 'Cash on Delivery'),
        ('other', 'Other'),
    )
    
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Payment receipt (uploaded by seller for cash/manual payments)
    receipt_file = models.FileField(
        upload_to='payment_receipts/',
        blank=True,
        null=True,
        help_text="Payment receipt (uploaded by seller for cash on delivery or manual verification)"
    )
    receipt_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Receipt/invoice number"
    )
    
    # Payment gateway information
    transaction_id = models.CharField(max_length=100, blank=True)
    gateway_reference = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Payment notes
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the payment (e.g., 'Cash collected on delivery by John')"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.rental.rental_reference} - {self.get_payment_type_display()}: ${self.amount}"


class RentalDocument(models.Model):
    """
    Legal documents and contracts for rentals
    
    Document Types:
    - rental_agreement: Contract signed by both parties (seller uploads template, system auto-generates)
    - operating_manual: Equipment operating manual (auto-attached from Equipment.operating_manual after payment)
    - insurance_document: Insurance certificate if applicable
    - delivery_receipt: Proof of delivery with signature
    - return_receipt: Proof of return with condition notes
    - damage_report: Documentation of any damages
    - invoice: Official invoice for payment
    - payment_receipt: Receipt for cash/manual payments
    - other: Any other relevant documents
    """
    DOCUMENT_TYPE_CHOICES = (
        ('rental_agreement', 'Rental Agreement'),
        ('operating_manual', 'Operating Manual'),
        ('insurance_document', 'Insurance Document'),
        ('delivery_receipt', 'Delivery Receipt'),
        ('return_receipt', 'Return Receipt'),
        ('damage_report', 'Damage Report'),
        ('invoice', 'Invoice'),
        ('payment_receipt', 'Payment Receipt'),
        ('other', 'Other'),
    )
    
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='rental_documents/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Visibility control
    visible_to_customer = models.BooleanField(
        default=True,
        help_text="Whether customer can see this document (e.g., internal notes should be False)"
    )
    requires_payment = models.BooleanField(
        default=False,
        help_text="Document only visible after payment (e.g., operating manual)"
    )
    
    # Signing
    is_signed = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True, blank=True)
    signature_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Digital signature information"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.rental.rental_reference} - {self.title}"


class RentalSale(models.Model):
    """
    Sales record created when a rental is completed.
    This tracks revenue, commissions, and financial analytics.
    
    Created automatically when rental status becomes 'completed'.
    """
    rental = models.OneToOneField(
        Rental, 
        on_delete=models.CASCADE, 
        related_name='sale',
        help_text="The rental that generated this sale"
    )
    
    # Financial details (copied from rental at completion)
    total_revenue = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Total amount paid by customer"
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    insurance_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    damage_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Platform commission (configurable)
    platform_commission_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=10.00,
        help_text="Platform commission percentage at time of sale"
    )
    platform_commission_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Calculated commission amount"
    )
    seller_payout = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Amount to be paid to seller after commission"
    )
    
    # References
    seller = models.ForeignKey(
        'accounts.CompanyProfile',
        on_delete=models.CASCADE,
        related_name='sales'
    )
    customer = models.ForeignKey(
        'accounts.CustomerProfile',
        on_delete=models.CASCADE,
        related_name='purchases'
    )
    equipment = models.ForeignKey(
        'equipment.Equipment',
        on_delete=models.CASCADE,
        related_name='sales'
    )
    
    # Rental details for analytics
    rental_days = models.PositiveIntegerField()
    rental_start_date = models.DateField()
    rental_end_date = models.DateField()
    equipment_quantity = models.PositiveIntegerField(default=1)
    
    # Payout tracking
    PAYOUT_STATUS_CHOICES = (
        ('pending', 'Pending Payout'),
        ('processing', 'Processing'),
        ('completed', 'Paid Out'),
        ('failed', 'Failed'),
        ('on_hold', 'On Hold'),
    )
    payout_status = models.CharField(
        max_length=20, 
        choices=PAYOUT_STATUS_CHOICES, 
        default='pending'
    )
    payout_date = models.DateTimeField(null=True, blank=True)
    payout_reference = models.CharField(max_length=100, blank=True)
    payout_notes = models.TextField(blank=True)
    
    # Timestamps
    sale_date = models.DateTimeField(auto_now_add=True, help_text="When rental was completed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-sale_date']
        indexes = [
            models.Index(fields=['seller', '-sale_date']),
            models.Index(fields=['customer', '-sale_date']),
            models.Index(fields=['payout_status']),
        ]
    
    def __str__(self):
        return f"Sale {self.rental.rental_reference} - {self.seller.company_name}"
    
    def save(self, *args, **kwargs):
        """Calculate commission and payout amounts"""
        from decimal import Decimal
        if not self.pk:  # Only on creation
            # Convert percentage to Decimal for calculation
            commission_rate = Decimal(str(self.platform_commission_percentage)) / Decimal('100')
            self.platform_commission_amount = self.total_revenue * commission_rate
            self.seller_payout = self.total_revenue - self.platform_commission_amount
        super().save(*args, **kwargs)
    
    @property
    def commission_rate(self):
        """Return commission percentage as decimal"""
        return float(self.platform_commission_percentage)
    
    @property
    def is_paid_out(self):
        """Check if seller has been paid"""
        return self.payout_status == 'completed'
