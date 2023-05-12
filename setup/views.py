from django.contrib.auth.models import User
from django.db import ProgrammingError
from django.http import HttpResponse
from django.shortcuts import render
from django.core.management import call_command


def index(request):
    try:
        User.objects.all().exists()
    except ProgrammingError:
        return HttpResponse("seup")
        # call_command('makemigrations')
        # call_command('migrate')


def run_migrations():
    call_command('makemigrations')
    call_command('migrate')