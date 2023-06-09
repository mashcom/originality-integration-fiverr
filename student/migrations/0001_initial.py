# Generated by Django 4.2 on 2023-04-25 11:53

from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Courses',
            fields=[
                ('id', models.BigIntegerField(primary_key='id', serialize=False)),
                ('name', models.TextField(max_length=250)),
                ('section', models.TextField(max_length=250)),
                ('descriptionHeading', models.TextField(max_length=2500)),
                ('ownerId', models.TextField(max_length=50)),
                ('alternateLink', models.TextField(max_length=200)),
            ],
        ),
    ]
