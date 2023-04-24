from django.shortcuts import render, HttpResponse
from django.contrib import messages

def index(request):
    return render(request, "courses.html")

def create_assingment(request):
    return render(request, "create_assignment.html")

def save_assignment(request):
    title = request.POST["title"]
    course = request.POST["course"]
    originality_enabled = request.POST["originality_enabled"]
    # messages.add_message(request, messages.INFO, "Hello world.", "alert alert-danger fw-bold")
    return render(request, "create_assignment.html")
