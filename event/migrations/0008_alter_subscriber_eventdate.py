# Generated by Django 5.1.5 on 2025-01-21 14:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0007_alter_eventdate_maxsubscribers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriber',
            name='eventDate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', to='event.eventdate', verbose_name='Event Date'),
        ),
    ]
