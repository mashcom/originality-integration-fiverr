# Generated by Django 4.2 on 2023-05-18 12:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings_manager', '0019_alter_originalitylog_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='originalitylog',
            name='created_at',
            field=models.TextField(default=datetime.datetime(2023, 5, 18, 12, 51, 19, 652121, tzinfo=datetime.timezone.utc)),
        ),
    ]