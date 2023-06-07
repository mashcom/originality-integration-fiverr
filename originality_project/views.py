from django.shortcuts import render

from .settings import REQUIRED_ORIGINALITY_INTEGRATION_SETTINGS

from django.contrib.admin.views.decorators import staff_member_required


def index(request):
    print(REQUIRED_ORIGINALITY_INTEGRATION_SETTINGS)
    for setting in REQUIRED_ORIGINALITY_INTEGRATION_SETTINGS:
        print(setting)
    return render(request, "../authentication/templates/homepage.html")
