import json
import logging

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from allauth.socialaccount.models import SocialAccount, SocialApp
from django.shortcuts import render, redirect
from .models import Tenant, UserTenant
from django.contrib.auth.models import User, Group
from django.db.models import Prefetch


# Get a logger instance
logger = logging.getLogger(__name__)

def index(request):
    return render(request, "create_tenant.html")

def add_institution(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        country = request.POST.get('country')
        contact_number = request.POST.get('contact')
        website = request.POST.get('website')

        tenant = Tenant(name=name, address=address, country=country, contact_number=contact_number, website=website)
        tenant.save()

        return redirect('/')
    # else:
    #     return render(request, 'add_institution.html')  # Replace 'add_institution.html' with the template name for your add institution form

def tenant_users(request):
    tenant_id=1
    # Retrieve users for the given tenant
    user_tenants = UserTenant.objects.filter(tenant_id=tenant_id).select_related('user_id')

    users = []
    for user_tenant in user_tenants:
        user = user_tenant.user_id
        groups = Group.objects.filter(user=user).values_list('name', flat=True)

        user_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            'groups': list(groups),
        }
        users.append(user_data)
    context = {
        "users": users
    }
    return render(request, "tenant_users.html", context=context)
