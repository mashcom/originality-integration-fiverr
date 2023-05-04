# Generated by Django 4.2 on 2023-04-25 12:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0013_course_alter_assignment_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignments',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('title', models.TextField(max_length=250)),
                ('course_id', models.TextField(max_length=200)),
                ('description', models.TextField(max_length=250)),
                ('originality_check', models.TextField(max_length=2500)),
                ('owner_id', models.TextField(max_length=100)),
                ('processed', models.BooleanField(default=False, max_length=20)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2023, 4, 25, 12, 46, 38, 978529, tzinfo=datetime.timezone.utc))),
            ],
        ),
        migrations.RenameModel(
            old_name='AssignmentMaterial',
            new_name='AssignmentMaterials',
        ),
        migrations.RenameModel(
            old_name='AssignmentStudent',
            new_name='AssignmentStudents',
        ),
        migrations.RenameModel(
            old_name='Course',
            new_name='Courses',
        ),
        migrations.DeleteModel(
            name='Assignment',
        ),
    ]
