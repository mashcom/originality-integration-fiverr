from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from services import google_service

def index(request):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"authenticated": request.user.is_authenticated})

    if request.user.is_superuser:
        return redirect("/config")

    active_user = SocialAccount.objects.filter(user=request.user)[0]
    user_id = active_user.user_id
    user = User.objects.filter(id=user_id).first()

    # if no email address is saved update it
    if user.email == "":
        uid = active_user.uid
        profile = google_service.get_user_profile(user_id=uid, uid=uid)
        email_address = profile.get("emailAddress")
        user.email = email_address
        user.save()

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
