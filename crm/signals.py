from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Lead, SalesOpportunity, SupportTicket, TicketComment
from rentals.models import Rental
from favorites.models import Favorite
from notifications.services import NotificationService


# Note: ContactFormSubmission removed - not applicable for REST API
# If you add a contact form endpoint later, you can create leads directly in the view


@receiver(post_save, sender=Rental)
def create_opportunity_from_large_rental(sender, instance, created, **kwargs):
    """
    Automatically create a sales opportunity for large rental orders.
    Threshold: rentals over 10,000 AED or rentals longer than 30 days.
    """
    if created:
        # Check if this is a high-value rental
        is_high_value = instance.total_amount >= 10000
        is_long_term = (instance.end_date - instance.start_date).days >= 30
        
        if is_high_value or is_long_term:
            # Check if opportunity already exists for this rental
            if not hasattr(instance, 'opportunity'):
                try:
                    SalesOpportunity.objects.create(
                        title=f"Rental Opportunity: {instance.equipment.name}",
                        description=f"High-value rental order: {instance.rental_reference}",
                        contact_name=instance.customer.user.get_full_name() or instance.customer.user.email,
                        contact_email=instance.customer_email,
                        contact_phone=instance.customer_phone,
                        company=instance.seller,
                        customer=instance.customer,
                        equipment=instance.equipment,
                        stage='closed_won',
                        probability=100,
                        estimated_amount=instance.total_amount,
                        actual_amount=instance.total_amount,
                        actual_close_date=timezone.now().date(),
                        notes=f"Auto-created from rental {instance.rental_reference}. Total: {instance.total_amount}, Duration: {instance.total_days} days"
                    )
                except Exception as e:
                    print(f"Error creating opportunity from rental: {e}")


@receiver(post_save, sender=Rental)
def create_ticket_from_rental_dispute(sender, instance, **kwargs):
    """
    Automatically create a support ticket when a rental status changes to 'dispute'.
    """
    if instance.status == 'dispute':
        # Check if ticket already exists for this rental
        existing_ticket = SupportTicket.objects.filter(
            related_rental=instance,
            status__in=['open', 'in_progress']
        ).first()
        
        if not existing_ticket:
            try:
                ticket = SupportTicket.objects.create(
                    title=f"Rental Dispute: {instance.rental_reference}",
                    description=f"Rental {instance.rental_reference} has entered dispute status. Please investigate.",
                    category='complaint',
                    priority='high',
                    customer=instance.customer,
                    company=instance.seller,
                    related_rental=instance,
                    related_equipment=instance.equipment,
                    internal_notes="Auto-created from rental dispute status",
                    created_by=None  # System-created
                )
                
                # Notify staff about the dispute ticket
                NotificationService.create_notification(
                    user=None,  # Will be sent to all staff
                    notification_type='rental_dispute',
                    title='New Dispute Ticket Created',
                    message=f'Rental {instance.rental_reference} is under dispute. Ticket {ticket.ticket_number} created.',
                    related_rental=instance
                )
            except Exception as e:
                print(f"Error creating ticket from rental dispute: {e}")


@receiver(post_save, sender=Favorite)
def create_lead_from_repeated_favorites(sender, instance, created, **kwargs):
    """
    Create a lead when a customer favorites multiple items (high intent signal).
    Threshold: 5 or more favorites in the last 7 days.
    """
    if created:
        # Count recent favorites by this customer
        from datetime import timedelta
        from django.utils import timezone
        
        week_ago = timezone.now() - timedelta(days=7)
        favorite_count = Favorite.objects.filter(
            customer=instance.customer,
            favorited_at__gte=week_ago
        ).count()
        
        if favorite_count >= 5:
            # Check if lead already exists for this customer recently
            recent_lead = Lead.objects.filter(
                customer=instance.customer,
                source='automation',
                created_at__gte=week_ago
            ).first()
            
            if not recent_lead:
                try:
                    Lead.objects.create(
                        title=f"High-Intent Customer: {instance.customer.user.email}",
                        contact_name=instance.customer.user.get_full_name() or instance.customer.user.email,
                        contact_email=instance.customer.user.email,
                        contact_phone=instance.customer.user.phone_number or '',
                        customer=instance.customer,
                        source='automation',
                        status='qualified',
                        notes=f"Customer has favorited {favorite_count} items in the past week. High purchase intent. Auto-created lead.",
                        metadata={
                            'trigger': 'repeated_favorites',
                            'favorite_count': favorite_count,
                            'latest_favorite': instance.equipment.name
                        }
                    )
                except Exception as e:
                    print(f"Error creating lead from favorites: {e}")


@receiver(post_save, sender=TicketComment)
def notify_on_ticket_comment(sender, instance, created, **kwargs):
    """
    Send notifications when a comment is added to a ticket.
    """
    if created and not instance.is_internal:
        ticket = instance.ticket
        
        # Notify customer if comment is from staff/seller
        if instance.created_by and instance.created_by.is_staff:
            try:
                NotificationService.create_notification(
                    user=ticket.customer.user,
                    notification_type='support_update',
                    title=f'Update on Ticket {ticket.ticket_number}',
                    message=f'New comment from support on your ticket: {ticket.title}',
                    related_rental=ticket.related_rental
                )
            except Exception as e:
                print(f"Error notifying customer of ticket comment: {e}")
        
        # Notify assigned staff if comment is from customer
        elif ticket.assigned_to and instance.created_by != ticket.assigned_to:
            try:
                NotificationService.create_notification(
                    user=ticket.assigned_to,
                    notification_type='support_update',
                    title=f'New Comment on Ticket {ticket.ticket_number}',
                    message=f'Customer replied to ticket: {ticket.title}',
                    related_rental=ticket.related_rental
                )
            except Exception as e:
                print(f"Error notifying staff of ticket comment: {e}")


@receiver(pre_save, sender=SupportTicket)
def notify_on_ticket_status_change(sender, instance, **kwargs):
    """
    Send notification when ticket status changes.
    """
    if instance.pk:  # Only for updates, not creates
        try:
            old_instance = SupportTicket.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Status changed - notify customer
                NotificationService.create_notification(
                    user=instance.customer.user,
                    notification_type='support_update',
                    title=f'Ticket {instance.ticket_number} Status Updated',
                    message=f'Your ticket status changed from {old_instance.get_status_display()} to {instance.get_status_display()}',
                    related_rental=instance.related_rental
                )
        except SupportTicket.DoesNotExist:
            pass
        except Exception as e:
            print(f"Error notifying on ticket status change: {e}")


@receiver(post_save, sender=Lead)
def notify_on_lead_assignment(sender, instance, created, **kwargs):
    """
    Notify staff member when a lead is assigned to them.
    """
    if instance.assigned_to and not created:
        # Check if assignment changed
        try:
            # This requires tracking previous state - could use django-dirtyfields
            # For now, simple notification on any update with assigned_to
            pass  # Implement if needed
        except Exception as e:
            print(f"Error notifying on lead assignment: {e}")
