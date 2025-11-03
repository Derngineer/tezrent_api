from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0004_remove_equipment_equip_seller_status_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Show/hide this equipment in listings'),
        ),
    ]
