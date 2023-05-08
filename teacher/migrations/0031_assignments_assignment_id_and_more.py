# Generated by Django 4.2 on 2023-05-05 09:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0030_alter_assignments_created_at_alter_courses_course_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignments',
            name='assignment_id',
            field=models.TextField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='assignments',
            name='course_id',
            field=models.TextField(max_length=50),
        ),
        migrations.AlterField(
            model_name='assignments',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 5, 9, 14, 58, 707641, tzinfo=datetime.timezone.utc)),
        ),
    ]
