# Generated by Django 4.2 on 2023-04-25 12:15

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('teacher', '0003_alter_assignment_processed'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='course_id',
            field=models.TextField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
