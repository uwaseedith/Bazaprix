# Generated by Django 5.1.6 on 2025-02-09 15:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Baza', '0003_product_door_number_product_market_product_price_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
    ]
