# Generated by Django 5.1.5 on 2025-03-12 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0006_alter_company_countrycode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='countryCode',
            field=models.CharField(default='+216', help_text='add your country code like +216 or 00216', max_length=4, verbose_name='Country code'),
        ),
    ]
