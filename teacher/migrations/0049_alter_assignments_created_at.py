# Generated by Django 4.2.1 on 2023-05-11 10:35

import datetime

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('teacher', '0048_alter_assignments_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignments',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2023, 5, 11, 10, 35, 52, 837688, tzinfo=datetime.timezone.utc)),
        ),
    ]
