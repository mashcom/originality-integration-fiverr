# Generated by Django 4.2.1 on 2023-07-05 14:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings_manager', '0031_alter_originality_tenant_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='originalitylog',
            name='created_at',
            field=models.TextField(default=datetime.datetime(2023, 7, 5, 14, 11, 11, 792180, tzinfo=datetime.timezone.utc)),
        ),
    ]
