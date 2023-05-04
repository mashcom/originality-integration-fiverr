import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .forms import NameForm
from .models import Originality, OriginalityLog
from django.contrib import messages
import json
from services import originality

def index(request):
    settings = originality.get_active_settings()
    return render(request, "index.html", {"settings": settings})

'''
Verify and save Originality settings
'''

def verify_key(request):
    originality_key = request.POST.get('key', False);
    api_url = request.POST.get("api_url", False)
    settings = originality.get_active_settings()

    try:
        request.POST["originality_status"]
        originality_enabled = True
    except KeyError:
        originality_enabled = False

    try:
        request.POST["ghost_writer_status"]
        ghost_writer_status = True
    except KeyError:
        ghost_writer_status = False

    verification_status = originality._make_verification_request(originality_key, api_url)
    if verification_status['Pong'] == True:
        originality._save_setting("key", originality_key)
        originality._save_setting("originality_status", originality_enabled)
        originality._save_setting("ghost_writer_status", ghost_writer_status)
        originality._save_setting("api_url", api_url)
        messages.add_message(request, messages.ERROR, "Key updated successfully!",
                             "alert alert-success fw-bold")
        return redirect(request.META.get('HTTP_REFERER'))

    messages.add_message(request, messages.ERROR, "The key is invalid, please try again!",
                         "alert alert-danger fw-bold")
    return redirect(request.META.get('HTTP_REFERER'))
