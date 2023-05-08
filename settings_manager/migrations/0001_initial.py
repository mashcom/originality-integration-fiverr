# Generated by Django 4.2 on 2023-04-25 20:38

from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Originality',
            fields=[
                ('name', models.TextField(max_length=100, primary_key='id', serialize=False)),
                ('setting', models.TextField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='OriginalityLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=100)),
                ('setting', models.TextField(max_length=100)),
                ('created_at', models.TextField(max_length=50)),
            ],
        ),
    ]
