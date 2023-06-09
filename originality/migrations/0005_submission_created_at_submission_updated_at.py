# Generated by Django 4.2 on 2023-05-03 08:10

import django.utils.timezone
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('originality', '0004_report_created_at_report_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submission',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
