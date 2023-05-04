from __future__ import print_function

import os.path
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from authentication import google
from services import google_classroom, originality
from django.contrib import messages
from django.conf import settings
import uuid
from .models import Submission
from allauth.socialaccount.models import SocialAccount

def index(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    submissions = Submission.objects.filter(student_code=uid)
    print(submissions)
    return render(request, "submissions.html", {"submissions": submissions})

def reports_for_teacher(request, course_id, assignment_id):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    submissions = Submission.objects.filter(owner_id=uid, assignment_code=assignment_id)
    assignment_details = google_classroom.classroom_get_course_work_item(course_id=course_id,
                                                                     assignment_id=assignment_id)
    print(submissions)
    return render(request, "report.html", {"submissions": submissions, "assignment": assignment_details})

def submit_to_originality(request):
    if request.method == "POST":
        print("params")
        params = request.POST.dict()
        redirect_url = "/student/course/" + \
                       params.get("CourseCode") + "/assignment/" + \
                       params.get("AssignmentCode")

        file = request.FILES["file"]
        request_uuid = str(uuid.uuid4())

        try:
            uploaded_file_path = handle_uploaded_file(file, request_uuid)
            response = originality.submit_document(
                params, file, uploaded_file_path)
            if response["success"]:
                return HttpResponseRedirect("/originality")
            else:
                messages.add_message(request, response,
                                     "alert alert-danger fw-bold")
                return HttpResponseRedirect(redirect_url)
        except ConnectionError:
            messages.add_message(request, 'Request could not be completed check your connection',
                                 "alert alert-danger fw-bold")
            return HttpResponseRedirect(redirect_url)
        except Exception as error:
            messages.add_message(request, 'Request could not be completed. Internal Error',
                                 "alert alert-danger fw-bold")
            return HttpResponseRedirect(redirect_url)

def handle_uploaded_file(upload_file, uuid):
    new_file_name = uuid + "_" + upload_file.name
    with open(os.path.join(settings.BASE_DIR, 'uploads/') + new_file_name, 'wb+') as destination:
        for chunk in upload_file.chunks():
            destination.write(chunk)
    return os.path.join(settings.BASE_DIR, 'uploads/') + new_file_name
