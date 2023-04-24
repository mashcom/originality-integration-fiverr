from django.db import models

class Courses(models.Model):
    id = models.BigIntegerField(primary_key="id", max_length=200)
    name = models.TextField(max_length=250)
    section = models.TextField(max_length=250)
    descriptionHeading = models.TextField(max_length=2500)
    ownerId = models.TextField(max_length=50)
    alternateLink = models.TextField(max_length=200)
