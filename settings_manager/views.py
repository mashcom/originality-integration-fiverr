from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .models import OriginalityLog

from services import originality
from django.contrib.auth.decorators import login_required
from originality_project.decorators import check_user_able_to_see_page

@login_required()
@check_user_able_to_see_page("admin")
def index(request):
    settings = originality.get_active_settings()
    return render(request, "index.html", {"settings": settings})

def log(request):
    logs = OriginalityLog.objects.filter().order_by("-created_at")
    return render(request, "log.html", {"logs": logs})

'''
Verify and save Originality settings
'''

@login_required()
@require_http_methods(["POST"])
@check_user_able_to_see_page("admin")
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
        originality.log(name="key", setting=originality_key, success=True)
        originality.log(name="api_url", setting=api_url, success=True)
        messages.add_message(request, messages.ERROR, "Key updated successfully!",
                             "alert alert-success fw-bold")
        return redirect(request.META.get('HTTP_REFERER'))

    originality.log(name="key", setting=originality_key, success=False)
    originality.log(name="api_url", setting=api_url, success=False)
    messages.add_message(request, messages.ERROR, "The key '" + originality_key + "' is invalid, please try again!",
                         "alert alert-danger fw-bold")
    return redirect(request.META.get('HTTP_REFERER'))
