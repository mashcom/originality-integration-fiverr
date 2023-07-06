from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Tenant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    country = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    trial = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tenant'



class UserTenant(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.PROTECT)
    tenant_id = models.IntegerField()

    class Meta:
        unique_together = ('user_id', 'tenant_id')
        db_table = 'tenant_user'
