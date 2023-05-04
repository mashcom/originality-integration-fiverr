from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages
from allauth.socialaccount.models import SocialAccount

import json

def index(request):
    authenticated = request.user.is_authenticated
    return render(request, "login.html", {"authenticated": authenticated})

def attempt(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        messages.add_message(request, messages.SUCCESS, "Login successful!",
                             "alert alert-success fw-bold")
        ...
    else:
        messages.add_message(request, messages.ERROR, "Invalid username or password!",
                             "alert alert-danger fw-bold")

    return render(request, "login.html")
