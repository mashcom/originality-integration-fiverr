import requests
from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    try:
        api_request = requests.get("http://40.115.61.181/Rest/v2/api/customers/ping")
        response = api_request.json()
        return JsonResponse(response)
    except Exception:
        return JsonResponse(Exception)



