# Generated by Django 4.2.1 on 2023-06-26 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('originality', '0020_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='total_possible',
            field=models.TextField(default='', max_length=20),
        ),
    ]
