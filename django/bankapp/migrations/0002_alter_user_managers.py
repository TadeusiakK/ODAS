# Generated by Django 5.0.1 on 2024-01-30 18:15

import bankapp.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bankapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', bankapp.models.CustomUserManager()),
            ],
        ),
    ]
