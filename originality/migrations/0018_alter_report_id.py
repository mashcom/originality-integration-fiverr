# Generated by Django 4.2 on 2023-06-07 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('originality', '0017_report_assignment_id_report_doc_sequence_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
