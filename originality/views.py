from __future__ import print_function

import os.path
import uuid
from base64 import b64decode

from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import render, HttpResponse, redirect

from services import google_classroom, originality
from .models import Submission, Report

def index(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    submissions = Submission.objects.filter(student_code=uid)
    print(submissions)
    return render(request, "submissions.html", {"submissions": submissions})

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
            uploaded_file_path = originality.handle_uploaded_file(upload_file=file, uuid=request_uuid)

            response = originality.submit_document(
                params, file, uploaded_file_path)

            print("ERROR!")
            print(response)
            if response["success"]:
                messages.add_message(request, messages.SUCCESS, "Submission successfully sent ",
                                     "alert alert-success fw-bold")
                return redirect(request.META.get('HTTP_REFERER'))
            else:
                messages.add_message(request, messages.ERROR, response,
                                     "alert alert-danger fw-bold")
                return redirect(request.META.get('HTTP_REFERER'))
        except ConnectionError:
            messages.add_message(request, messages.ERROR, 'Request could not be completed check your connection',
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))
        except Exception as error:
            print(error)
            messages.add_message(request, messages.ERROR, 'Request could not be completed. Internal Error',
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

def reports_for_teacher(request, course_id, assignment_id):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    submissions = Submission.objects.filter(owner_id=uid, assignment_code=assignment_id)
    try:
        assignment_details = google_classroom.classroom_get_course_work_item(course_id=course_id,
                                                                             course_work_id=assignment_id)
        course_details = google_classroom.classroom_get_course(course_id)
    except Exception as error:
        messages.add_message(request, messages.ERROR, "There was an error connecting to Google APIs",
                             "alert alert-success fw-bold")
        return redirect(request.META.get('HTTP_REFERER'))
    reports = []
    for submission in submissions:
        report = Report.objects.filter(id=submission.id).first()
        if report:
            report.submitted_by = submission.student_code
            report.profile = google_classroom.get_user_profile(submission.student_code)
            reports.append(report)
            print(report.profile)

    return render(request, "report.html",
                  {"reports": reports, "assignment": assignment_details, "course_details": course_details})

def download_report(request, originality_id):
    report = get_object_or_404(Report, id=originality_id)
    b64 = report.file
    return _download_base64(request, report.id, b64, "report.pdf")

def download_submission(request, id):
    submission = get_object_or_404(Submission, id=id)
    b64 = submission.file
    return _download_base64(request, submission.id, b64, submission.file_name)

def _download_base64(request, id, base64_string, file_name):
    try:
        # Decode the Base64 string, making sure that it contains only valid characters
        bytes = b64decode(base64_string)

        # Write the PDF contents to a local file
        path = "reports/" + str(id) + '_' + file_name
        f = open(path, 'wb')
        f.write(bytes)
        f.close()
        file_path = path  # os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/pdf")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
    except Exception as error:
        return error
