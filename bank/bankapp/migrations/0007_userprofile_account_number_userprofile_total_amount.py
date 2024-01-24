# Generated by Django 5.0.1 on 2024-01-24 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bankapp', '0006_userprofile_first_name_userprofile_last_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='account_number',
            field=models.CharField(default='', max_length=32, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
