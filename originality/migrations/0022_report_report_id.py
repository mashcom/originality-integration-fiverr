# Generated by Django 4.2.1 on 2023-07-02 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('originality', '0021_grade_total_possible'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='report_id',
            field=models.TextField(default=''),
        ),
    ]
