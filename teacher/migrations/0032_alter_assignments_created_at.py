# Generated by Django 4.2 on 2023-05-05 12:32

import datetime

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('teacher', '0031_assignments_assignment_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignments',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2023, 5, 5, 12, 32, 36, 591109, tzinfo=datetime.timezone.utc)),
        ),
    ]
