# Generated by Django 4.2 on 2023-05-11 09:28

import datetime

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('teacher', '0046_alter_assignments_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignments',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2023, 5, 11, 9, 28, 45, 613939, tzinfo=datetime.timezone.utc)),
        ),
    ]
