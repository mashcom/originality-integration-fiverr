# Generated by Django 4.2 on 2023-05-12 11:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings_manager', '0016_alter_originalitylog_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='originalitylog',
            name='created_at',
            field=models.TextField(default=datetime.datetime(2023, 5, 12, 11, 3, 8, 303415, tzinfo=datetime.timezone.utc)),
        ),
    ]
