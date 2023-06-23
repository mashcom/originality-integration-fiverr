import os.path

from allauth.socialaccount.models import SocialAccount, SocialApp
from django.conf import settings
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
from services.exceptions import NoGoogleTokenException
from originality_project.decorators import check_user_able_to_see_page
from django.contrib.auth.decorators import login_required

from django.shortcuts import redirect
from django.contrib.auth import logout
from allauth.socialaccount.models import SocialToken
from django.contrib.auth.models import Group


def index(request):
    create_groups()
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
    except NoGoogleTokenException as error:
        messages.add_message(request, messages.ERROR, error,
                             "alert alert-danger fw-bold")
        context = {"email": user.email, "url": error+"&login_hint="+user.email,"user":user}
        return render(request, "google_permission.html", context)
    except InvalidClientError as error:
        pass

    # check user groups and redirect accordingly
    if User.objects.filter(pk=user_id, groups__name='teachers').exists():
        return redirect("/teacher")

    if User.objects.filter(pk=user_id, groups__name='students').exists():
        return redirect("/student")

    return render(request, "no_group.html", {"email": user.email})

def create_groups():
    group_names = ['admins', 'students', 'teachers','developers']

    for name in group_names:
        group, created = Group.objects.get_or_create(name=name)


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
    uid = ""
    try:
        uid = SocialAccount.objects.filter(user=request.user)[0].uid
    except Exception:
        pass
    credentials_file = os.path.join(settings.BASE_DIR, "credentials.json")
    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, google_service.SCOPES,
                                                     redirect_uri=request.build_absolute_uri(
                                                         '/') + "auth/oauth_callback"
                                                     )

    #
    # Exchange the authorization code for credentials
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    # Save the credentials for the next run
    google_credentials = flow.credentials
    # Save the credentials to token.json or any other preferred storage method
    with open(google_service.token_file(uid), 'w') as token:
        token.write(google_credentials.to_json())

    messages.add_message(request, messages.SUCCESS,
                         google_credentials.to_json(),
                         "alert alert-info fw-bold")
    return redirect(request.build_absolute_uri('/')+"auth/completed")


def auth_completed(request):
    try:
        uid = SocialAccount.objects.filter(user=request.user)[0].uid
        profile = google_service.get_user_profile(user_id=uid, uid=uid)
        storage = messages.get_messages(request)

        # Iterate over messages and delete them
        for message in storage:
            pass  # Do nothing, effectively deleting the message

        # Reset the storage to remove deleted messages
        storage.used = True
        return render(request, "auth_completed.html")
    except NoGoogleTokenException as error:
        messages.add_message(request, messages.ERROR, error,
                             "alert alert-danger fw-bold")
        return render(request, "google_permission.html", {"url": error})
    except Exception:
        messages.add_message(request, messages.ERROR, "",
                             "alert alert-danger fw-bold")
        return redirect("/")


@login_required()
def reset_token_page(request):
    return render(request, "reset_token.html")


@login_required()
def reset_token(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    if google_service.remove_token_file(uid):
        messages.add_message(request, messages.SUCCESS,"Google Token be removed",
                             "alert alert-success fw-bold")
        return redirect("/")

    messages.add_message(request, messages.ERROR,"Google Token could not be removed",
                         "alert alert-danger fw-bold")
    return redirect(request.META.get('HTTP_REFERER'))
