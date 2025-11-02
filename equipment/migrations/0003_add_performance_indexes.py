# Generated migration for equipment performance indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0002_equipment_manual_description_and_more'),
    ]

    operations = [
        # Index for seller's equipment queries
        migrations.AddIndex(
            model_name='equipment',
            index=models.Index(
                fields=['seller_company', 'is_active'],
                name='equip_seller_active_idx'
            ),
        ),
        
        # Index for category browsing with price sorting
        migrations.AddIndex(
            model_name='equipment',
            index=models.Index(
                fields=['category', 'is_active', 'daily_rate'],
                name='equip_category_price_idx'
            ),
        ),
        
        # Index for availability filtering
        migrations.AddIndex(
            model_name='equipment',
            index=models.Index(
                fields=['availability_status', 'is_active'],
                name='equip_availability_idx'
            ),
        ),
        
        # Index for featured and deals queries
        migrations.AddIndex(
            model_name='equipment',
            index=models.Index(
                fields=['is_active', 'featured', '-created_at'],
                name='equip_featured_idx'
            ),
        ),
        
        # Index for status filtering
        migrations.AddIndex(
            model_name='equipment',
            index=models.Index(
                fields=['status', '-created_at'],
                name='equip_status_created_idx'
            ),
        ),
    ]
