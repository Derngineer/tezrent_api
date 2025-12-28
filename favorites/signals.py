"""
Signals for favorites app to handle notifications
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from equipment.models import Equipment
from favorites.models import Favorite
from notifications.models import Notification

@receiver(post_save, sender=Equipment)
def notify_favorites_on_status_change(sender, instance, created, **kwargs):
    """
    Notify users who favorited this equipment when:
    1. It becomes available (if they opted in)
    2. Price drops (if they opted in)
    3. A deal is activated (if they opted in)
    """
    if created:
        return

    # Check if status changed to available
    if instance.status == 'available' and instance.available_units > 0:
        # Find users who favorited this and want availability alerts
        favorites = Favorite.objects.filter(
            equipment=instance,
            notify_on_availability=True
        ).select_related('customer__user')
        
        for fav in favorites:
            Notification.objects.create(
                user=fav.customer.user,
                notification_type='equipment_available',
                title=f"{instance.name} is Available!",
                message=f"Good news! The {instance.name} you liked is now available for rent.",
                related_equipment=instance
            )

    # Check if deal became active
    if instance.is_deal_active:
        favorites = Favorite.objects.filter(
            equipment=instance,
            notify_on_deals=True
        ).select_related('customer__user')
        
        for fav in favorites:
            Notification.objects.create(
                user=fav.customer.user,
                notification_type='deal_alert',
                title=f"Special Deal on {instance.name}!",
                message=f"Get {instance.deal_discount_percentage}% off on {instance.name}. Now only {instance.discounted_daily_rate}/day!",
                related_equipment=instance
            )
