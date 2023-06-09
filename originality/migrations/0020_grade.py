# Generated by Django 4.2.1 on 2023-06-26 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('originality', '0019_report_file_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('grade', models.TextField(default='', max_length=20)),
                ('user_id', models.TextField(default='')),
                ('assignment_id', models.TextField(default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
