# Generated by Django 4.2.1 on 2023-07-05 13:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0074_alter_assignments_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignments',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 5, 13, 0, 27, 37279, tzinfo=datetime.timezone.utc)),
        ),
    ]
