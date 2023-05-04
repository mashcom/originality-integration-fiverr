from django.db import models

class Originality(models.Model):
    name = models.TextField(primary_key="id", max_length=100)
    setting = models.TextField(max_length=100)

class OriginalityLog(models.Model):
    name = models.TextField(max_length=100)
    setting = models.TextField(max_length=100)
    created_at = models.TextField(max_length=50)
