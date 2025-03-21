# Generated by Django 4.2.16 on 2025-01-20 16:01

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0003_rename_max_subscribers_eventdate_maxsubscribers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='altitude',
            field=models.CharField(choices=[('3400', '3 500 m (11 000 feet)'), ('4500', '4 500 m (14,000 feet)'), ('4500+', 'Over 4500 m (14,000 feet)')], default='3400', max_length=5, verbose_name='At what altitude would you like to jump from a plane?'),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='country',
            field=django_countries.fields.CountryField(default=1, max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscriber',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default='M', max_length=1, verbose_name='Gender'),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='region',
            field=models.CharField(default=1, max_length=100, verbose_name='City'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscriber',
            name='skydiver_option',
            field=models.CharField(choices=[('tandem', 'Tandem (Beginner)'), ('solo', 'Solo'), ('experienced', 'Experienced')], default='tandem', max_length=12, verbose_name='Are you a skydiver?'),
        ),
    ]
