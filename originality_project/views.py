import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

def index(request):
    return render(request, "../authentication/templates/homepage.html")
