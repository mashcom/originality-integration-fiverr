# Generated by Django 4.2 on 2023-06-07 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('originality', '0018_alter_report_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='file_name',
            field=models.TextField(default=''),
        ),
    ]