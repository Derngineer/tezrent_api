# Generated migration for performance indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0003_rentalsale'),
    ]

    operations = [
        # Index for seller dashboard queries (most common)
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(
                fields=['seller', 'status', '-created_at'],
                name='rental_seller_status_idx'
            ),
        ),
        
        # Index for customer queries
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(
                fields=['customer', 'status'],
                name='rental_customer_status_idx'
            ),
        ),
        
        # Index for date availability queries
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(
                fields=['status', 'start_date', 'end_date'],
                name='rental_availability_idx'
            ),
        ),
        
        # Index for payment and approval queries
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(
                fields=['payment_status', 'approval_status'],
                name='rental_payment_approval_idx'
            ),
        ),
        
        # Index for equipment rental lookup
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(
                fields=['equipment', 'status'],
                name='rental_equipment_status_idx'
            ),
        ),
    ]
