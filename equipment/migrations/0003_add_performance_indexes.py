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
                fields=['seller_company', 'status'],
                name='equip_seller_status_idx'
            ),
        ),
        
        # Index for category browsing with price sorting
        migrations.AddIndex(
            model_name='equipment',
            index=models.Index(
                fields=['category', 'status', 'daily_rate'],
                name='equip_category_price_idx'
            ),
        ),
        
        # Index for status filtering (covers availability queries)
        migrations.AddIndex(
            model_name='equipment',
            index=models.Index(
                fields=['status', '-created_at'],
                name='equip_status_idx'
            ),
        ),
        
        # Index for featured and deals queries
        migrations.AddIndex(
            model_name='equipment',
            index=models.Index(
                fields=['featured', 'status', '-created_at'],
                name='equip_featured_idx'
            ),
        ),
        
        # Index for country/city location queries
        migrations.AddIndex(
            model_name='equipment',
            index=models.Index(
                fields=['country', 'city', 'status'],
                name='equip_location_idx'
            ),
        ),
    ]
