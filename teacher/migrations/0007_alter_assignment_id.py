# Generated by Django 4.2 on 2023-04-25 12:20

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('teacher', '0006_alter_assignment_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
