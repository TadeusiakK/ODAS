# Generated by Django 5.0.1 on 2024-01-24 12:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bankapp', '0011_blog'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfer',
            name='sender',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='transfers_sent', to='bankapp.userprofile'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Blog',
        ),
    ]