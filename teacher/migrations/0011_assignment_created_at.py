# Generated by Django 4.2 on 2023-04-25 12:32

import datetime

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('teacher', '0010_remove_assignment_due_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2023, 4, 25, 12, 32, 0, 79883, tzinfo=datetime.timezone.utc)),
        ),
    ]
