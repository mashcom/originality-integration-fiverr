# Generated by Django 4.2 on 2023-05-05 12:32

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('originality', '0006_submission_owner_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='google_classroom_id',
            field=models.TextField(default='', max_length=100),
        ),
    ]
