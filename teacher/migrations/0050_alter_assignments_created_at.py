# Generated by Django 4.2 on 2023-05-11 10:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0049_alter_assignments_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignments',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 11, 10, 37, 36, 808008, tzinfo=datetime.timezone.utc)),
        ),
    ]
