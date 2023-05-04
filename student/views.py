from __future__ import print_function

import os.path
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from authentication import google
from services import google_classroom, originality
from .forms import NameForm
from django.contrib import messages
from django.conf import settings
import uuid
from allauth.socialaccount.models import SocialAccount

def index(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid

    form = NameForm()

    try:

        service = google.get_google_service_instance()

        # Call the Classroom API
        results = service.courses().list(studentId=uid).execute()
        courses = results.get('courses', [])

        if not courses:
            messages.add_message(request, messages.ERROR, 'No active course found!',
                                 "alert alert-danger fw-bold")

        return render(request, "classes.html", {"form": form, "classes": courses})

    except Exception as error:
        messages.add_message(request, messages.ERROR, 'An error occurred: %s' % error,
                             "alert alert-danger fw-bold")
        return render(request, "classes.html", {"form": form, "classes": {}})

def course(request, id):
    try:
        assignments = google_classroom.classroom_get_course_work(id)
        course_details = google_classroom.classroom_get_course(id)
        return render(request, "course.html", {"assignments": assignments, "course_details": course_details})
    except Exception as error:
        messages.add_message(request, messages.ERROR, 'An error occurred: %s' % error,
                             "alert alert-danger fw-bold")
        return render(request, "course.html", {"assignments": {}, "course_details": {}})

def course_assignments(request, course_id, assignment_id):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    course_details = {}
    assignment_details = {}
    try:
        course_details = google_classroom.classroom_get_course(course_id)
        assignment_details = google_classroom.classroom_get_course_work_item(course_id, assignment_id)
    except Exception as error:
        messages.add_message(request, messages.ERROR, 'An error occurred: %s' % error,
                             "alert alert-danger fw-bold")
    return render(request, "submit_assignment.html",
                  {"assignment_details": assignment_details, "course_details": course_details, "uid": uid})
