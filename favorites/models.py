"""
Favorites models for TezRent
Allows users to save equipment they like
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Favorite(models.Model):
    """
    User's favorite/liked equipment
    """
    customer = models.ForeignKey(
        'accounts.CustomerProfile',
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    equipment = models.ForeignKey(
        'equipment.Equipment',
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    
    # Optional fields
    notes = models.TextField(
        blank=True,
        help_text="Personal notes about why they like this equipment"
    )
    
    # Rental preferences for this equipment
    preferred_rental_start = models.DateField(
        null=True,
        blank=True,
        help_text="When they'd like to rent this"
    )
    preferred_rental_duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Preferred rental duration in days"
    )
    
    # Notifications
    notify_on_availability = models.BooleanField(
        default=False,
        help_text="Notify when equipment becomes available"
    )
    notify_on_price_drop = models.BooleanField(
        default=False,
        help_text="Notify when price drops"
    )
    notify_on_deals = models.BooleanField(
        default=True,
        help_text="Notify when there's a special deal"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('customer', 'equipment')
        ordering = ['-created_at']
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        indexes = [
            models.Index(fields=['customer', '-created_at']),
            models.Index(fields=['equipment', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.customer.user.email} likes {self.equipment.name}"
    
    @property
    def is_available(self):
        """Check if the favorited equipment is currently available"""
        return self.equipment.status == 'available' and self.equipment.available_units > 0
    
    @property
    def current_price(self):
        """Get current daily rate (with deals if applicable)"""
        if self.equipment.is_deal_active:
            return self.equipment.discounted_daily_rate
        return self.equipment.daily_rate
    
    @property
    def price_when_favorited(self):
        """Track if price has changed since favoriting (for price drop alerts)"""
        # You could store original_price in the model if you want price tracking
        return self.equipment.daily_rate


class FavoriteCollection(models.Model):
    """
    Custom collections/wishlists for organizing favorites
    Similar to Pinterest boards or Instagram collections
    """
    customer = models.ForeignKey(
        'accounts.CustomerProfile',
        on_delete=models.CASCADE,
        related_name='favorite_collections'
    )
    name = models.CharField(
        max_length=100,
        help_text="Collection name (e.g., 'Summer Projects', 'Next Month', 'Dream Equipment')"
    )
    description = models.TextField(blank=True)
    
    # Collection settings
    is_public = models.BooleanField(
        default=False,
        help_text="Allow others to view this collection"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon name for mobile app (e.g., 'heart', 'star', 'bookmark')"
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Hex color code for collection (e.g., #FF6B35)"
    )
    
    # Items in collection
    equipment = models.ManyToManyField(
        'equipment.Equipment',
        related_name='in_collections',
        blank=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'
    
    def __str__(self):
        return f"{self.customer.user.email}'s {self.name} ({self.equipment.count()} items)"
    
    @property
    def item_count(self):
        """Number of items in collection"""
        return self.equipment.count()
    
    @property
    def total_estimated_cost(self):
        """Estimated total daily cost to rent all equipment in collection"""
        return sum(
            eq.discounted_daily_rate if eq.is_deal_active else eq.daily_rate
            for eq in self.equipment.all()
        )


class RecentlyViewed(models.Model):
    """
    Track recently viewed equipment for personalized recommendations
    """
    customer = models.ForeignKey(
        'accounts.CustomerProfile',
        on_delete=models.CASCADE,
        related_name='recently_viewed'
    )
    equipment = models.ForeignKey(
        'equipment.Equipment',
        on_delete=models.CASCADE,
        related_name='viewed_by'
    )
    
    # Tracking data
    view_count = models.PositiveIntegerField(default=1)
    first_viewed_at = models.DateTimeField(auto_now_add=True)
    last_viewed_at = models.DateTimeField(auto_now=True)
    
    # Context
    viewed_from = models.CharField(
        max_length=50,
        blank=True,
        help_text="Where they viewed from (search, category, featured, etc.)"
    )
    
    class Meta:
        unique_together = ('customer', 'equipment')
        ordering = ['-last_viewed_at']
        verbose_name = 'Recently Viewed'
        verbose_name_plural = 'Recently Viewed'
        indexes = [
            models.Index(fields=['customer', '-last_viewed_at']),
        ]
    
    def __str__(self):
        return f"{self.customer.user.email} viewed {self.equipment.name} ({self.view_count}x)"
    
    def increment_view(self):
        """Increment view count and update timestamp"""
        self.view_count += 1
        self.last_viewed_at = timezone.now()
        self.save(update_fields=['view_count', 'last_viewed_at'])
