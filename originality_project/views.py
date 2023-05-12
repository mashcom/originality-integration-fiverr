from django.shortcuts import render
from .settings import REQUIRED_ORIGINALITY_INTEGRATION_SETTINGS
from settings_manager.models import Originality

def index(request):
    print(REQUIRED_ORIGINALITY_INTEGRATION_SETTINGS)
    for setting in REQUIRED_ORIGINALITY_INTEGRATION_SETTINGS:
        print(setting)
    return render(request, "../authentication/templates/homepage.html")
