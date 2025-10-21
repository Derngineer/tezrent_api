"""
Notification models for TezRent
Handles in-app notifications, push notifications, and email notifications
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    """
    In-app notifications for users
    """
    NOTIFICATION_TYPES = (
        ('rental_request', 'Rental Request Received'),
        ('rental_approved', 'Rental Approved'),
        ('rental_rejected', 'Rental Rejected'),
        ('rental_confirmed', 'Rental Confirmed'),
        ('rental_delivered', 'Equipment Delivered'),
        ('rental_completed', 'Rental Completed'),
        ('rental_cancelled', 'Rental Cancelled'),
        ('payment_received', 'Payment Received'),
        ('payment_pending', 'Payment Pending'),
        ('review_received', 'Review Received'),
        ('message_received', 'New Message'),
        ('equipment_available', 'Equipment Now Available'),
        ('deal_alert', 'Special Deal Alert'),
        ('system_update', 'System Update'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Optional references
    related_rental = models.ForeignKey(
        'rentals.Rental',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_equipment = models.ForeignKey(
        'equipment.Equipment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    # Navigation data for React Native
    action_url = models.CharField(max_length=500, blank=True)
    navigation_params = models.JSONField(default=dict, blank=True)
    
    # Status tracking
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Push notification tracking
    push_sent = models.BooleanField(default=False)
    push_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Email notification tracking
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def time_since_created(self):
        """Human-readable time since creation"""
        delta = timezone.now() - self.created_at
        
        if delta.days > 30:
            return f"{delta.days // 30} month(s) ago"
        elif delta.days > 0:
            return f"{delta.days} day(s) ago"
        elif delta.seconds >= 3600:
            return f"{delta.seconds // 3600} hour(s) ago"
        elif delta.seconds >= 60:
            return f"{delta.seconds // 60} minute(s) ago"
        else:
            return "Just now"


class PushNotificationToken(models.Model):
    """
    Store FCM/Expo push notification tokens for React Native apps
    """
    DEVICE_TYPES = (
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_tokens'
    )
    token = models.CharField(max_length=500, unique=True)
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES)
    device_id = models.CharField(max_length=255, blank=True)
    device_name = models.CharField(max_length=255, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'device_id')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.device_type} - {self.device_name}"


class NotificationPreference(models.Model):
    """
    User preferences for notifications
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Push notification preferences
    push_rental_updates = models.BooleanField(default=True)
    push_messages = models.BooleanField(default=True)
    push_payment_updates = models.BooleanField(default=True)
    push_deals_alerts = models.BooleanField(default=True)
    push_marketing = models.BooleanField(default=False)
    
    # Email notification preferences
    email_rental_updates = models.BooleanField(default=True)
    email_messages = models.BooleanField(default=False)
    email_payment_updates = models.BooleanField(default=True)
    email_deals_alerts = models.BooleanField(default=False)
    email_marketing = models.BooleanField(default=False)
    
    # SMS notification preferences (for future)
    sms_rental_updates = models.BooleanField(default=False)
    sms_payment_updates = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification preferences for {self.user.email}"

