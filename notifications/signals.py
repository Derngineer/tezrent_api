"""
Django signals for notifications app
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import NotificationPreference


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_notification_preferences(sender, instance, created, **kwargs):
    """
    Automatically create notification preferences for new users
    """
    if created:
        NotificationPreference.objects.get_or_create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_notification_preferences(sender, instance, **kwargs):
    """
    Ensure notification preferences are saved when user is saved
    """
    if hasattr(instance, 'notification_preferences'):
        instance.notification_preferences.save()
