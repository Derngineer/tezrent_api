"""
Notification service for sending notifications via various channels
"""
from django.conf import settings
from .models import Notification, PushNotificationToken
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for creating and sending notifications
    """
    
    @staticmethod
    def create_notification(
        user,
        notification_type,
        title,
        message,
        related_rental=None,
        related_equipment=None,
        action_url='',
        navigation_params=None
    ):
        """
        Create a notification and optionally send via push/email
        """
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_rental=related_rental,
            related_equipment=related_equipment,
            action_url=action_url,
            navigation_params=navigation_params or {}
        )
        
        # Send push notification if user has preferences enabled
        if hasattr(user, 'notification_preferences'):
            prefs = user.notification_preferences
            
            # Determine if push should be sent based on type and preferences
            should_send_push = NotificationService._should_send_push(
                notification_type, prefs
            )
            
            if should_send_push:
                NotificationService.send_push_notification(user, notification)
            
            # Determine if email should be sent
            should_send_email = NotificationService._should_send_email(
                notification_type, prefs
            )
            
            if should_send_email:
                NotificationService.send_email_notification(user, notification)
        
        return notification
    
    @staticmethod
    def _should_send_push(notification_type, prefs):
        """Determine if push notification should be sent based on type and preferences"""
        type_mapping = {
            'rental_request': prefs.push_rental_updates,
            'rental_approved': prefs.push_rental_updates,
            'rental_rejected': prefs.push_rental_updates,
            'rental_confirmed': prefs.push_rental_updates,
            'rental_delivered': prefs.push_rental_updates,
            'rental_completed': prefs.push_rental_updates,
            'rental_cancelled': prefs.push_rental_updates,
            'payment_received': prefs.push_payment_updates,
            'payment_pending': prefs.push_payment_updates,
            'message_received': prefs.push_messages,
            'deal_alert': prefs.push_deals_alerts,
        }
        return type_mapping.get(notification_type, False)
    
    @staticmethod
    def _should_send_email(notification_type, prefs):
        """Determine if email notification should be sent"""
        type_mapping = {
            'rental_request': prefs.email_rental_updates,
            'rental_approved': prefs.email_rental_updates,
            'rental_rejected': prefs.email_rental_updates,
            'rental_confirmed': prefs.email_rental_updates,
            'payment_received': prefs.email_payment_updates,
            'payment_pending': prefs.email_payment_updates,
            'message_received': prefs.email_messages,
            'deal_alert': prefs.email_deals_alerts,
        }
        return type_mapping.get(notification_type, False)
    
    @staticmethod
    def send_push_notification(user, notification):
        """
        Send push notification to user's devices
        Uses Expo Push Notifications for React Native
        """
        tokens = PushNotificationToken.objects.filter(
            user=user,
            is_active=True
        )
        
        if not tokens.exists():
            logger.info(f"No active push tokens for user {user.email}")
            return
        
        # TODO: Implement actual push notification sending
        # This is a placeholder for Expo Push Notifications or FCM
        
        # Example Expo Push format:
        push_messages = []
        for token in tokens:
            push_messages.append({
                'to': token.token,
                'title': notification.title,
                'body': notification.message,
                'data': {
                    'notification_id': notification.id,
                    'notification_type': notification.notification_type,
                    'action_url': notification.action_url,
                    **notification.navigation_params
                },
                'sound': 'default',
                'priority': 'high',
            })
        
        # In production, you would send these to Expo or FCM:
        # response = requests.post('https://exp.host/--/api/v2/push/send', json=push_messages)
        
        logger.info(f"Would send {len(push_messages)} push notifications for {notification.title}")
        
        # Mark as sent
        from django.utils import timezone
        notification.push_sent = True
        notification.push_sent_at = timezone.now()
        notification.save(update_fields=['push_sent', 'push_sent_at'])
    
    @staticmethod
    def send_email_notification(user, notification):
        """
        Send email notification to user
        """
        if not user.email:
            logger.warning(f"User {user.id} has no email address")
            return
        
        try:
            # You can create email templates later
            subject = notification.title
            message = notification.message
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            
            # For now, send simple email
            # Later you can use HTML templates
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            
            # Mark as sent
            from django.utils import timezone
            notification.email_sent = True
            notification.email_sent_at = timezone.now()
            notification.save(update_fields=['email_sent', 'email_sent_at'])
            
            logger.info(f"Email sent to {user.email}: {subject}")
            
        except Exception as e:
            logger.error(f"Failed to send email to {user.email}: {str(e)}")


# Helper functions for common notifications

def notify_rental_request(rental):
    """Notify seller about new rental request"""
    seller_user = rental.seller.user
    
    return NotificationService.create_notification(
        user=seller_user,
        notification_type='rental_request',
        title=f'New Rental Request - {rental.equipment.name}',
        message=f'{rental.customer.user.get_full_name() or rental.customer.user.email} '
                f'requested to rent {rental.equipment.name} from '
                f'{rental.start_date} to {rental.end_date}.',
        related_rental=rental,
        related_equipment=rental.equipment,
        action_url=f'/rentals/{rental.id}',
        navigation_params={
            'screen': 'RentalDetail',
            'params': {'rentalId': rental.id}
        }
    )


def notify_rental_approved(rental):
    """Notify customer that rental was approved"""
    customer_user = rental.customer.user
    
    return NotificationService.create_notification(
        user=customer_user,
        notification_type='rental_approved',
        title='Rental Request Approved! 🎉',
        message=f'Your rental request for {rental.equipment.name} has been approved. '
                f'Please complete the payment to confirm your booking.',
        related_rental=rental,
        related_equipment=rental.equipment,
        action_url=f'/rentals/{rental.id}/payment',
        navigation_params={
            'screen': 'RentalPayment',
            'params': {'rentalId': rental.id}
        }
    )


def notify_rental_rejected(rental):
    """Notify customer that rental was rejected"""
    customer_user = rental.customer.user
    
    return NotificationService.create_notification(
        user=customer_user,
        notification_type='rental_rejected',
        title='Rental Request Not Approved',
        message=f'Unfortunately, your rental request for {rental.equipment.name} '
                f'could not be approved. {rental.cancellation_reason or ""}',
        related_rental=rental,
        related_equipment=rental.equipment,
        action_url=f'/rentals/{rental.id}',
        navigation_params={
            'screen': 'RentalDetail',
            'params': {'rentalId': rental.id}
        }
    )


def notify_payment_received(rental):
    """Notify seller that payment was received"""
    seller_user = rental.seller.user
    
    return NotificationService.create_notification(
        user=seller_user,
        notification_type='payment_received',
        title='Payment Received 💰',
        message=f'Payment of ${rental.total_amount} received for rental {rental.rental_reference}',
        related_rental=rental,
        action_url=f'/rentals/{rental.id}',
        navigation_params={
            'screen': 'RentalDetail',
            'params': {'rentalId': rental.id}
        }
    )
