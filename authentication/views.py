from allauth.socialaccount.models import SocialAccount, SocialApp
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import BadRequest
from django.db import ProgrammingError
from django.shortcuts import render, redirect
from google_auth_oauthlib.flow import InstalledAppFlow
from oauthlib.oauth2 import InvalidClientError

from originality_project.settings import REQUIRED_ORIGINALITY_INTEGRATION_SETTINGS
from services import google_service
from services import originality_service

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
        # return redirect("/accounts/google/login")

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

def oauth_callback(request):
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', google_service.SCOPES)

    #
    # Exchange the authorization code for credentials
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    # Save the credentials for the next run
    creds = flow.credentials
    # Save the credentials to token.json or any other preferred storage method
    print(creds)
    return render(request, 'oauth_app/callback.html')
