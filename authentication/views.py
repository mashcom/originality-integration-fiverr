from allauth.socialaccount.models import SocialAccount, SocialApp
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import BadRequest
from django.db import ProgrammingError
from django.shortcuts import render, redirect, HttpResponse
from oauthlib.oauth2 import InvalidClientError

from originality_project import settings
from originality_project.settings import REQUIRED_ORIGINALITY_INTEGRATION_SETTINGS, REQUIRED_GROUPS
from settings_manager.models import Originality
from services import originality_service
from django.contrib.sites.models import Site
from services import google_service
from django.core.management import call_command

def index(request):
    try:
        user_count = User.objects.all().count()
        if user_count == 0:
            return render(request, "no_super_user.html")
    except ProgrammingError:
        return render(request, "migrations_pending.html")

    social_app_exits = SocialApp.objects.all().exists()

    if not social_app_exits:
        return render(request, "no_social_app.html")

    for setting in REQUIRED_ORIGINALITY_INTEGRATION_SETTINGS:
        setting_key = setting.get("name")
        setting_value = setting.get("setting")
        if not originality_service.setting_defined(setting_key):
            originality_service.save_setting(setting_key, setting_value)

    if not request.user.is_authenticated:
        return render(request, "login.html", {"authenticated": request.user.is_authenticated})

    if request.user.is_superuser:
        return redirect("/config")

    active_user = SocialAccount.objects.filter(user=request.user)
    if not active_user:
        raise BadRequest

    user_id = active_user[0].user_id
    user = User.objects.filter(id=user_id).first()

    # if no email address is saved update it
    try:
        if user.email == "":
            uid = active_user[0].uid
            profile = google_service.get_user_profile(user_id=uid, uid=uid)
            email_address = profile.get("emailAddress")
            user.email = email_address
            user.save()
    except InvalidClientError as error:
        pass

    # check user groups and redirect accordingly
    if User.objects.filter(pk=user_id, groups__name='teachers').exists():
        return redirect("/teacher")

    if User.objects.filter(pk=user_id, groups__name='students').exists():
        return redirect("/student")

    return render(request, "no_group.html", {"email": user.email})

def attempt(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        messages.add_message(request, messages.SUCCESS, "Login successful!",
                             "alert alert-success fw-bold")

    else:
        messages.add_message(request, messages.ERROR, "Invalid username or password!",
                             "alert alert-danger fw-bold")

    return render(request, "login.html")

def no_group(request):
    return render(request, "no_group.html")
