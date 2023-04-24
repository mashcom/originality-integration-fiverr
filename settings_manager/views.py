import requests
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .forms import NameForm

def index(request):
    form = NameForm()
    return render(request, "index.html", {"form": form})

def verify_key(request):
    key = request.POST["key"]
    headers = {"Authorization": key}
    try:
        api_request = requests.get("http://40.115.61.181/Rest/v2/api/customers/ping", headers=headers)
        response = api_request.json()
        return JsonResponse({"data": response, "key": key})
    except Exception:
        return JsonResponse(Exception)
