# Generated by Django 5.0.1 on 2024-01-31 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bankapp', '0004_user_account_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
