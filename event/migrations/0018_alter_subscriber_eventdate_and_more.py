# Generated by Django 5.1.5 on 2025-03-05 09:37

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0017_alter_eventtime_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriber',
            name='eventDate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscribers', to='event.eventdate', verbose_name='Event Date'),
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='eventTime',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscribers', to='event.eventtime', verbose_name='Event Time'),
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='phone',
            field=models.CharField(blank=True, max_length=17, validators=[django.core.validators.RegexValidator(message='Enter a valid phone number (e.g., +123456789). Max 15 digits.', regex='^\\+?1?\\d{9,15}$')], verbose_name='Phone'),
        ),
    ]
