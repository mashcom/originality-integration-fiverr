# Generated by Django 4.2 on 2023-05-30 08:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0067_alter_assignments_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignments',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 30, 8, 12, 46, 757043, tzinfo=datetime.timezone.utc)),
        ),
    ]
