"""
Signal handlers for automatic RentalSale creation
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Rental, RentalSale


@receiver(post_save, sender=Rental)
def create_sale_on_completion(sender, instance, created, **kwargs):
    """
    Automatically create a RentalSale record when rental status changes to 'completed'.
    
    This is the key trigger point: A rental becomes a sale when it's completed.
    """
    # Only process if status is 'completed' and no sale exists yet
    if instance.status == 'completed' and not hasattr(instance, 'sale'):
        try:
            # Calculate rental days
            rental_days = (instance.end_date - instance.start_date).days + 1
            
            # Create the sale record
            RentalSale.objects.create(
                rental=instance,
                
                # Financial details from rental
                total_revenue=instance.total_amount,
                subtotal=instance.subtotal,
                delivery_fee=instance.delivery_fee,
                insurance_fee=instance.insurance_fee,
                late_fees=getattr(instance, 'late_fees', 0),
                damage_fees=getattr(instance, 'damage_fees', 0),
                
                # Platform commission - can be customized per seller in future
                platform_commission_percentage=10.00,  # Default 10%
                
                # References
                seller=instance.equipment.seller_company,
                customer=instance.customer,
                equipment=instance.equipment,
                
                # Rental details for analytics
                rental_days=rental_days,
                rental_start_date=instance.start_date,
                rental_end_date=instance.end_date,
                equipment_quantity=instance.quantity,
                
                # Initial payout status
                payout_status='pending',
            )
            
            print(f"✅ Sale created for rental {instance.rental_reference}")
            
        except Exception as e:
            print(f"❌ Error creating sale for rental {instance.rental_reference}: {str(e)}")


@receiver(pre_save, sender=Rental)
def track_status_change(sender, instance, **kwargs):
    """
    Track when rental status changes to 'completed'.
    This helps us log when exactly a rental becomes a sale.
    """
    if instance.pk:  # Only for updates, not new rentals
        try:
            old_instance = Rental.objects.get(pk=instance.pk)
            
            # Log status change to completed
            if old_instance.status != 'completed' and instance.status == 'completed':
                print(f"📊 Rental {instance.rental_reference} marked as COMPLETED - Sale will be recorded")
                
        except Rental.DoesNotExist:
            pass
