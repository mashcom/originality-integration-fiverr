from django.db import models
from django.utils import timezone

class Originality(models.Model):
    name = models.TextField(primary_key="id", max_length=100)
    setting = models.TextField(max_length=100)

class OriginalityLog(models.Model):
    name = models.TextField(max_length=100)
    setting = models.TextField(max_length=50)
    response = models.TextField(max_length=100)
    success = models.TextField(max_length=15)
    created_at = models.DateTimeField(default=timezone.now())
