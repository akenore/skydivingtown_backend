# Generated by Django 4.2.16 on 2025-01-20 16:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0004_subscriber_altitude_subscriber_country_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriber',
            name='phone',
            field=models.CharField(blank=True, max_length=17, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')], verbose_name='Phone'),
        ),
    ]
