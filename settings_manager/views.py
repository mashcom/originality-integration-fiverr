import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from originality_project.decorators import check_user_able_to_see_page
from services import originality_service
from .models import OriginalityLog

@login_required()
@check_user_able_to_see_page("admins")
def index(request):
    settings = originality_service.get_active_settings()
    print(settings)
    return render(request, "index.html", {"settings": settings})

@login_required()
@check_user_able_to_see_page("admins")
def log(request):
    logs = OriginalityLog.objects.filter().order_by("-created_at")
    return render(request, "log.html", {"logs": logs})

@login_required()
@check_user_able_to_see_page("admins")
def google_classroom_settings(request):
    if request.method == "POST":
        google_client_id = request.POST.get('google_client_id', "")
        google_project_id = request.POST.get('google_project_id', "")
        google_client_secret = request.POST.get('google_client_secret', "")
        originality_service.save_setting("google_client_id", google_client_id)
        originality_service.save_setting("google_client_secret", google_client_secret)
        originality_service.save_setting("google_project_id", google_project_id)

        credentials_structure = {
            "installed": {
                "client_id": google_client_id,
                "project_id": google_project_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": google_client_secret,
                "redirect_uris": [
                    "urn:ietf:wg:oauth:2.0:oob",
                    "http://localhost"
                ]
            }
        }
        content_for_config = json.dumps(credentials_structure)

        try:
            # Create the credentials.json file that used by Google to authenticate
            filename = "credentials.json"
            with open(filename, 'w') as file_object:
                file_object.write(content_for_config)

            messages.add_message(request, messages.SUCCESS, "Google Classroom configuration updated successfully",
                                 "alert alert-success fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))
        except Exception as error:
            messages.add_message(request, messages.ERROR, error,
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

    settings = originality_service.get_google_active_settings()
    return render(request, "google_classroom.html", {"settings": settings})

'''
Verify and save Originality settings
'''

@login_required()
@require_http_methods(["POST"])
@check_user_able_to_see_page("admins")
def verify_key(request):
    originality_key = request.POST.get('key', False);
    api_url = request.POST.get("api_url", False)

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

    try:
        verification_status = originality_service.make_verification_request(originality_key, api_url)
        if verification_status['Pong']:
            originality_service.save_setting("key", originality_key)
            originality_service.save_setting("originality_status", originality_enabled)
            originality_service.save_setting("ghost_writer_status", ghost_writer_status)
            originality_service.save_setting("api_url", api_url)
            originality_service.log(name="key", setting=originality_key, success=True)
            originality_service.log(name="api_url", setting=api_url, success=True)
            messages.add_message(request, messages.ERROR, "Key updated successfully!",
                                 "alert alert-success fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

        originality_service.log(name="key", setting=originality_key, success=False)
        originality_service.log(name="api_url", setting=api_url, success=False)
        messages.add_message(request, messages.ERROR, "The key '" + originality_key + "' is invalid, please try again!",
                             "alert alert-danger fw-bold")

    except Exception as error:
        messages.add_message(request, messages.ERROR, "Error connecting to remote server, please try again",
                             "alert alert-danger fw-bold")
    return redirect(request.META.get('HTTP_REFERER'))
