# Generated by Django 4.2 on 2023-05-08 20:45

import datetime

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('teacher', '0036_assignments_due_date_assignments_due_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignments',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2023, 5, 8, 20, 45, 34, 884574, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='assignments',
            name='due_date',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='assignments',
            name='due_time',
            field=models.TextField(default=''),
        ),
    ]
