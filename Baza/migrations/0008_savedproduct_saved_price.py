# Generated by Django 5.1.6 on 2025-02-09 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Baza', '0007_rename_target_price_pricealert_change_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='savedproduct',
            name='saved_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
