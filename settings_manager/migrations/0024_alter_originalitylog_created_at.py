# Generated by Django 4.2 on 2023-06-07 02:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings_manager', '0023_alter_originalitylog_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='originalitylog',
            name='created_at',
            field=models.TextField(default=datetime.datetime(2023, 6, 7, 2, 52, 43, 335640, tzinfo=datetime.timezone.utc)),
        ),
    ]