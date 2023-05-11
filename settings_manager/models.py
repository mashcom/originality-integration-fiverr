from django.db import models
from django.utils import timezone

class Originality(models.Model):
    id = models.BigAutoField(primary_key="id", null=False)
    name = models.CharField(max_length=100,)
    setting = models.TextField(max_length=100)

class OriginalityLog(models.Model):
    id = models.BigAutoField(primary_key="id", null=False)
    name = models.TextField(max_length=100)
    setting = models.TextField(max_length=50)
    response = models.TextField(max_length=100)
    success = models.TextField(max_length=15)
    created_at = models.TextField(default=timezone.now())
