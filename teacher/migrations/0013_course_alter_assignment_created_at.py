# Generated by Django 4.2 on 2023-04-25 12:45

import datetime

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('teacher', '0012_alter_assignment_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('course_id', models.BigIntegerField()),
                ('name', models.TextField(max_length=250)),
                ('description', models.TextField(max_length=250)),
                ('owner_id', models.BigIntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='assignment',
            name='created_at',
            field=models.DateTimeField(
                default=datetime.datetime(2023, 4, 25, 12, 45, 12, 800760, tzinfo=datetime.timezone.utc)),
        ),
    ]
