# Generated by Django 5.1.6 on 2025-02-09 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Baza', '0008_savedproduct_saved_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricealert',
            name='seen',
            field=models.BooleanField(default=False),
        ),
    ]
