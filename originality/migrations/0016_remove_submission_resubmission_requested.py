# Generated by Django 4.2 on 2023-05-11 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('originality', '0015_rename_resubmission_created_at_submission_resubmission_requested'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='resubmission_requested',
        ),
    ]
