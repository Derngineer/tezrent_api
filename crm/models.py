from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Lead(models.Model):
    """
    Potential customers who have shown interest but haven't registered yet
    """
    SOURCE_CHOICES = (
        ('website', 'Website Form'),
        ('phone', 'Phone Call'),
        ('email', 'Email Inquiry'),
        ('social_media', 'Social Media'),
        ('referral', 'Referral'),
        ('advertisement', 'Advertisement'),
        ('exhibition', 'Exhibition/Event'),
        ('walk_in', 'Walk In'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('new', 'New Lead'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal_sent', 'Proposal Sent'),
        ('negotiation', 'In Negotiation'),
        ('converted', 'Converted to Customer'),
        ('lost', 'Lost'),
        ('unqualified', 'Unqualified'),
    )
    
    INTEREST_LEVEL_CHOICES = (
        ('hot', 'Hot - Ready to Rent'),
        ('warm', 'Warm - Interested'),
        ('cold', 'Cold - Just Browsing'),
    )
    
    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    company_name = models.CharField(max_length=255, blank=True)
    
    # Lead Details
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    interest_level = models.CharField(max_length=10, choices=INTEREST_LEVEL_CHOICES, default='warm')
    
    # Interest Information
    interested_equipment = models.ManyToManyField(
        'equipment.Equipment',
        blank=True,
        related_name='interested_leads'
    )
    interested_category = models.ForeignKey(
        'equipment.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interested_leads'
    )
    estimated_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated rental budget per month"
    )
    rental_duration_needed = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., '1 week', '3 months'"
    )
    project_description = models.TextField(blank=True)
    
    # Location
    country = models.CharField(max_length=3, blank=True)
    city = models.CharField(max_length=3, blank=True)
    
    # Assignment and Follow-up
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads',
        limit_choices_to={'user_type': 'staff'}
    )
    next_follow_up = models.DateTimeField(null=True, blank=True)
    last_contacted = models.DateTimeField(null=True, blank=True)
    
    # Conversion
    converted_to_customer = models.ForeignKey(
        'accounts.CustomerProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='originated_from_lead'
    )
    converted_at = models.DateTimeField(null=True, blank=True)
    
    # Loss tracking
    lost_reason = models.TextField(blank=True)
    competitor_name = models.CharField(max_length=255, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'interest_level']),
            models.Index(fields=['assigned_to', 'next_follow_up']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_status_display()}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_overdue_follow_up(self):
        """Check if follow-up is overdue"""
        if self.next_follow_up:
            return timezone.now() > self.next_follow_up
        return False
    
    def convert_to_customer(self, customer_profile):
        """Mark lead as converted"""
        self.status = 'converted'
        self.converted_to_customer = customer_profile
        self.converted_at = timezone.now()
        self.save()


class CustomerInteraction(models.Model):
    """
    Track all interactions with customers and leads
    """
    INTERACTION_TYPE_CHOICES = (
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'In-Person Meeting'),
        ('video_call', 'Video Call'),
        ('chat', 'Live Chat'),
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('note', 'Internal Note'),
    )
    
    OUTCOME_CHOICES = (
        ('successful', 'Successful'),
        ('follow_up_needed', 'Follow-up Needed'),
        ('no_answer', 'No Answer'),
        ('voicemail', 'Left Voicemail'),
        ('not_interested', 'Not Interested'),
        ('information_sent', 'Information Sent'),
    )
    
    # Related to either a lead or a customer
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='interactions'
    )
    customer = models.ForeignKey(
        'accounts.CustomerProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='crm_interactions'
    )
    company = models.ForeignKey(
        'accounts.CompanyProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='crm_interactions'
    )
    
    # Interaction Details
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPE_CHOICES)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, null=True, blank=True)
    
    # Staff member who handled the interaction
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='customer_interactions',
        limit_choices_to={'user_type': 'staff'}
    )
    
    # Scheduling
    interaction_date = models.DateTimeField(default=timezone.now)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Follow-up
    requires_follow_up = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    follow_up_completed = models.BooleanField(default=False)
    
    # Attachments
    attachment = models.FileField(upload_to='crm/interactions/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-interaction_date']
        indexes = [
            models.Index(fields=['interaction_date']),
            models.Index(fields=['requires_follow_up', 'follow_up_date']),
        ]
    
    def __str__(self):
        contact = self.lead or self.customer or self.company
        return f"{self.get_interaction_type_display()} with {contact} on {self.interaction_date.date()}"


class SalesOpportunity(models.Model):
    """
    Track potential rental deals and sales pipeline
    """
    STAGE_CHOICES = (
        ('prospecting', 'Prospecting'),
        ('qualification', 'Qualification'),
        ('needs_analysis', 'Needs Analysis'),
        ('proposal', 'Proposal/Quote Sent'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    )
    
    PROBABILITY_CHOICES = (
        (10, '10% - Prospecting'),
        (25, '25% - Qualification'),
        (50, '50% - Needs Analysis'),
        (75, '75% - Proposal Sent'),
        (90, '90% - Negotiation'),
        (100, '100% - Closed Won'),
        (0, '0% - Closed Lost'),
    )
    
    # Opportunity Details
    name = models.CharField(max_length=255, help_text="Descriptive name for this opportunity")
    description = models.TextField(blank=True)
    
    # Related Entities
    lead = models.ForeignKey(
        Lead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunities'
    )
    customer = models.ForeignKey(
        'accounts.CustomerProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='opportunities'
    )
    company = models.ForeignKey(
        'accounts.CompanyProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='opportunities'
    )
    
    # Equipment and Rental Details
    equipment_items = models.ManyToManyField(
        'equipment.Equipment',
        related_name='sales_opportunities'
    )
    estimated_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Estimated total rental value"
    )
    rental_start_date = models.DateField(null=True, blank=True)
    rental_end_date = models.DateField(null=True, blank=True)
    rental_duration_months = models.PositiveIntegerField(null=True, blank=True)
    
    # Sales Stage
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='prospecting')
    probability = models.PositiveIntegerField(
        choices=PROBABILITY_CHOICES,
        default=25,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales_opportunities',
        limit_choices_to={'user_type': 'staff'}
    )
    
    # Important Dates
    expected_close_date = models.DateField(null=True, blank=True)
    actual_close_date = models.DateField(null=True, blank=True)
    
    # Outcome
    won_rental = models.ForeignKey(
        'rentals.Rental',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='originated_opportunity'
    )
    lost_reason = models.TextField(blank=True)
    competitor_name = models.CharField(max_length=255, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Sales Opportunities"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stage', 'probability']),
            models.Index(fields=['expected_close_date']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_stage_display()}"
    
    @property
    def weighted_value(self):
        """Calculate weighted value based on probability"""
        return self.estimated_value * (self.probability / 100)
    
    @property
    def is_overdue(self):
        """Check if expected close date has passed"""
        if self.expected_close_date and self.stage not in ['closed_won', 'closed_lost']:
            return timezone.now().date() > self.expected_close_date
        return False
    
    def mark_won(self, rental):
        """Mark opportunity as won"""
        self.stage = 'closed_won'
        self.probability = 100
        self.won_rental = rental
        self.actual_close_date = timezone.now().date()
        self.save()
    
    def mark_lost(self, reason, competitor=None):
        """Mark opportunity as lost"""
        self.stage = 'closed_lost'
        self.probability = 0
        self.lost_reason = reason
        self.competitor_name = competitor or ''
        self.actual_close_date = timezone.now().date()
        self.save()


class SupportTicket(models.Model):
    """
    Customer support and issue tracking
    """
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_customer', 'Waiting on Customer'),
        ('waiting_internal', 'Waiting on Internal Team'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('reopened', 'Reopened'),
    )
    
    CATEGORY_CHOICES = (
        ('equipment_issue', 'Equipment Issue'),
        ('billing', 'Billing Question'),
        ('delivery', 'Delivery/Pickup Issue'),
        ('rental_inquiry', 'Rental Inquiry'),
        ('technical_support', 'Technical Support'),
        ('complaint', 'Complaint'),
        ('feedback', 'Feedback'),
        ('return_issue', 'Return Issue'),
        ('damage_claim', 'Damage Claim'),
        ('other', 'Other'),
    )
    
    # Ticket Information
    ticket_number = models.CharField(max_length=20, unique=True, blank=True)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Customer Information
    customer = models.ForeignKey(
        'accounts.CustomerProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='support_tickets'
    )
    company = models.ForeignKey(
        'accounts.CompanyProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='support_tickets'
    )
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Related Objects
    related_rental = models.ForeignKey(
        'rentals.Rental',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='support_tickets'
    )
    related_equipment = models.ForeignKey(
        'equipment.Equipment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='support_tickets'
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        limit_choices_to={'user_type': 'staff'}
    )
    
    # Resolution
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_tickets',
        limit_choices_to={'user_type': 'staff'}
    )
    
    # Customer Satisfaction
    customer_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Customer satisfaction rating (1-5)"
    )
    customer_feedback = models.TextField(blank=True)
    
    # SLA Tracking
    response_due = models.DateTimeField(null=True, blank=True)
    resolution_due = models.DateTimeField(null=True, blank=True)
    first_response_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.subject}"
    
    def save(self, *args, **kwargs):
        """Auto-generate ticket number"""
        if not self.ticket_number:
            import random
            self.ticket_number = f"TKT-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if ticket is past resolution due date"""
        if self.resolution_due and self.status not in ['resolved', 'closed']:
            return timezone.now() > self.resolution_due
        return False
    
    @property
    def response_time(self):
        """Calculate time to first response"""
        if self.first_response_at:
            return self.first_response_at - self.created_at
        return None
    
    @property
    def resolution_time(self):
        """Calculate time to resolution"""
        if self.resolved_at:
            return self.resolved_at - self.created_at
        return None
    
    def mark_resolved(self, resolution_text, resolved_by):
        """Mark ticket as resolved"""
        self.status = 'resolved'
        self.resolution = resolution_text
        self.resolved_at = timezone.now()
        self.resolved_by = resolved_by
        self.save()


class TicketComment(models.Model):
    """
    Comments and updates on support tickets
    """
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ticket_comments'
    )
    comment = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal note not visible to customer"
    )
    attachment = models.FileField(
        upload_to='crm/tickets/',
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.ticket.ticket_number} by {self.author}"


class CustomerNote(models.Model):
    """
    Internal notes about customers or companies
    """
    NOTE_TYPE_CHOICES = (
        ('general', 'General Note'),
        ('preference', 'Customer Preference'),
        ('warning', 'Warning/Alert'),
        ('credit', 'Credit Information'),
        ('payment', 'Payment History'),
        ('behavior', 'Customer Behavior'),
    )
    
    # Related to either customer or company
    customer = models.ForeignKey(
        'accounts.CustomerProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='crm_notes'
    )
    company = models.ForeignKey(
        'accounts.CompanyProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='crm_notes'
    )
    
    note_type = models.CharField(max_length=20, choices=NOTE_TYPE_CHOICES, default='general')
    subject = models.CharField(max_length=255)
    content = models.TextField()
    is_important = models.BooleanField(default=False, help_text="Pin this note")
    
    # Author
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_notes',
        limit_choices_to={'user_type': 'staff'}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_important', '-created_at']
    
    def __str__(self):
        entity = self.customer or self.company
        return f"{self.get_note_type_display()} for {entity}"


class CustomerSegment(models.Model):
    """
    Customer segmentation for targeted marketing and analysis
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Segment Criteria (examples)
    min_rental_count = models.PositiveIntegerField(null=True, blank=True)
    min_total_spent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preferred_categories = models.ManyToManyField(
        'equipment.Category',
        blank=True,
        related_name='customer_segments'
    )
    
    # Customers in this segment
    customers = models.ManyToManyField(
        'accounts.CustomerProfile',
        blank=True,
        related_name='segments'
    )
    companies = models.ManyToManyField(
        'accounts.CompanyProfile',
        blank=True,
        related_name='segments'
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def total_customers(self):
        return self.customers.count() + self.companies.count()
